#include "ext.h"
#include "ext_obex.h"
#include "z_dsp.h"
#include "ext_buffer.h"
#include "../stochastic_core.hpp"
#include <atomic>
#include <mutex>
#include <cstdio>
#include <new>

// Message producers are serialized; audio consumer never waits, allocates or frees.
struct State {
    static constexpr unsigned QueueCapacity=64;
    stoch::Settings desired;
    stoch::Bank current;
    stoch::ClickFreeEngine engine;
    // A help preset expands into several Max messages in one scheduler turn.
    // Keep enough immutable snapshots for the whole UI, not merely one preset.
    std::array<stoch::Bank,QueueCapacity> queue;
    std::atomic<unsigned> write{0},read{0};
    std::mutex producers;
    State():current(stoch::makeBank(desired)) { engine.configure(current); }
    bool publish(stoch::Settings s) {
        auto bank=stoch::makeBank(s);
        // Desired state remains authoritative even while DSP is stopped.  A
        // subsequent DSP start rebuilds from this newest state rather than
        // silently retaining whichever eight messages happened to arrive first.
        desired=bank.s; current=bank;
        unsigned w=write.load(std::memory_order_relaxed);
        if(w-read.load(std::memory_order_acquire)>=queue.size()) return false;
        queue[w%queue.size()]=bank;
        write.store(w+1,std::memory_order_release); return true;
    }
    void consume() {
        unsigned r=read.load(std::memory_order_relaxed),w=write.load(std::memory_order_acquire);
        // Consume the newest complete snapshot; intermediate controls are superseded.
        if(r!=w) {
            engine.configure(queue[(w-1)%queue.size()]);
            read.store(w,std::memory_order_release);
        } else engine.servicePending();
    }
};
static_assert(std::atomic<unsigned>::is_always_lock_free,"Lock-free indices required");
struct t_stoch { t_pxobject ob; State* state; };
static t_class* klass=nullptr;
static void perform(t_stoch* x,t_object*,double** ins,long,double** outs,long,long n,long,void*) {
    x->state->consume();
    for(long i=0;i<n;++i) {
        if(x->ob.z_disabled) { outs[0][i]=outs[1][i]=0; continue; }
        auto f=x->state->engine.sample(ins[0][i]); outs[0][i]=f.wavetable; outs[1][i]=f.modal;
    }
}
static void dsp64(t_stoch* x,t_object* dsp,short*,double sr,long,long) {
    { std::lock_guard<std::mutex> lock(x->state->producers);
      auto s=x->state->desired; s.sr=sr; ++s.reset;
      // DSP setup runs while this object's perform routine is stopped.
      x->state->read.store(x->state->write.load());
      x->state->publish(s);
    }
    object_method(dsp,gensym("dsp_add64"),x,perform,0,nullptr);
}
static void command(t_stoch* x,t_symbol* name,long argc,t_atom* argv) {
    std::lock_guard<std::mutex> lock(x->state->producers);
    auto s=x->state->desired;
    if(name==gensym("reset")) ++s.reset;
    else if(name==gensym("next")) ++s.nextTarget;
    else {
        if(argc!=1 || (atom_gettype(argv)!=A_LONG && atom_gettype(argv)!=A_FLOAT)) {
            object_error((t_object*)x,"%s requires one number",name->s_name); return;
        }
        double v=atom_getfloat(argv);
        if(!std::isfinite(v)) { object_error((t_object*)x,"finite number required"); return; }
        if(name==gensym("freq")) { s.f0=std::clamp(v,1.0,0.45*s.sr); ++s.reset; }
        else if(name==gensym("modes")) { s.modes=int(std::clamp(v,1.0,32.0)); ++s.reset; }
        else if(name==gensym("slope")) { s.slope=std::clamp(v,0.0,6.0); ++s.reset; }
        else if(name==gensym("seed")) { s.seed=uint64_t(std::clamp(v,1.0,4294967295.0)); ++s.reset; }
        else if(name==gensym("motion")) s.motion=int(std::clamp(v,0.0,2.0));
        else if(name==gensym("tau")) s.tau=std::clamp(v,0.001,60.0);
        else if(name==gensym("evolve")) s.evolve=v!=0;
        else if(name==gensym("rate")) s.rate=std::clamp(v,0.01,100.0);
        else if(name==gensym("interp")) s.interpMs=std::clamp(v,0.0,60000.0);
        else if(name==gensym("slew")) s.slewMs=std::clamp(v,0.0,60000.0);
        else if(name==gensym("ampdepth")) s.ampdepth=std::clamp(v,0.0,1.0);
        else if(name==gensym("phasedepth")) s.phasedepth=std::clamp(v,0.0,1.0);
        else if(name==gensym("curve")) s.curve=v!=0;
        else if(name==gensym("gain")) s.gain=std::clamp(v,0.0,1.0);
    }
    if(!x->state->publish(s)) object_error((t_object*)x,"control queue full; latest value saved for the next DSP start (send slower while DSP runs)");
}
static void status(t_stoch* x) {
    std::lock_guard<std::mutex> lock(x->state->producers);
    const auto& s=x->state->desired;
    const unsigned pending=x->state->write.load(std::memory_order_acquire)-x->state->read.load(std::memory_order_acquire);
    object_post((t_object*)x,
        "stochspectra~ 0.5.0 | freq %.3f modes %d slope %.3f gain %.3f | evolve %d rate %.3f interp %.3f slew %.3f | pending %u/%u | reconfigure crossfade 20 ms",
        s.f0,s.modes,s.slope,s.gain,s.evolve,s.rate,s.interpMs,s.slewMs,
        pending,State::QueueCapacity);
}
static void tobuffer(t_stoch* x,t_symbol* name) {
    std::lock_guard<std::mutex> lock(x->state->producers);
    t_buffer_ref* ref=buffer_ref_new((t_object*)x,name);
    t_buffer_obj* buffer=buffer_ref_getobject(ref);
    if(!buffer) { object_error((t_object*)x,"buffer~ %s not found",name->s_name); object_free(ref); return; }
    float* samples=buffer_locksamples(buffer);
    if(!samples) { object_error((t_object*)x,"buffer unavailable"); object_free(ref); return; }
    long frames=buffer_getframecount(buffer),channels=buffer_getchannelcount(buffer);
    if(frames!=stoch::TableSize || channels!=1) {
        buffer_unlocksamples(buffer); object_error((t_object*)x,"buffer must be mono, sizeinsamps 8192"); object_free(ref); return;
    }
    // Unscaled cycle: shared ensemble variance normalization, not per-table peak normalization.
    for(long i=0;i<frames;++i) samples[i]=float(x->state->current.table[i]);
    buffer_unlocksamples(buffer); buffer_setdirty(buffer); object_free(ref);
}
static void assist(t_stoch*,void*,long io,long index,char* text) {
    snprintf(text,512,"%s",io==ASSIST_INLET ? "(signal) Modal excitation; messages: evolve, rate, interp, slew; freq, modes, slope, seed, motion, tau, gain, reset, status, tobuffer" : index==0 ? "(signal) Continuous stochastic spectral voice" : "(signal) Modal / stochastic output");
}
static void freeobj(t_stoch* x) { dsp_free((t_pxobject*)x); delete x->state; }
static void* create(t_symbol*,long,t_atom*) {
    auto* x=(t_stoch*)object_alloc(klass); if(!x) return nullptr;
    x->state=nullptr;
    dsp_setup((t_pxobject*)x,1);
    try { x->state=new State; } catch(...) { object_free(x); return nullptr; }
    outlet_new((t_object*)x,"signal"); outlet_new((t_object*)x,"signal");
    x->ob.z_misc|=Z_NO_INPLACE; return x;
}
extern "C" void C74_EXPORT ext_main(void*) {
    auto* c=class_new("stochspectra~",(method)create,(method)freeobj,sizeof(t_stoch),nullptr,A_GIMME,0);
    class_addmethod(c,(method)dsp64,"dsp64",A_CANT,0);
    class_addmethod(c,(method)assist,"assist",A_CANT,0);
    for(const char* name:{"freq","modes","slope","seed","motion","tau","gain","reset","evolve","rate","interp","slew","ampdepth","phasedepth","curve","next"})
        class_addmethod(c,(method)command,name,A_GIMME,0);
    class_addmethod(c,(method)status,"status",0);
    class_addmethod(c,(method)tobuffer,"tobuffer",A_SYM,0);
    class_dspinit(c); class_register(CLASS_BOX,c); klass=c;
}
