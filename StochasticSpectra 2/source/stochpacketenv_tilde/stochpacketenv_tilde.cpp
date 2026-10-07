#include "ext.h"
#include "ext_obex.h"
#include "z_dsp.h"
#include "../packet_envelope_core.hpp"
#include <array>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <mutex>
#include <new>

struct EnvelopeState {
    static constexpr unsigned QueueCapacity=64;
    stoch::packet::Settings desired;
    stoch::packet::Bank current;
    stoch::packet::ClickFreeEngine engine;
    std::array<stoch::packet::Bank,QueueCapacity> queue;
    std::atomic<unsigned> write{0},read{0};
    std::mutex producers;

    EnvelopeState():current(stoch::packet::makeBank(desired)) { engine.configure(current); }
    bool publish(stoch::packet::Settings settings) {
        const auto bank=stoch::packet::makeBank(settings);
        desired=bank.s; current=bank;
        const unsigned w=write.load(std::memory_order_relaxed);
        if(w-read.load(std::memory_order_acquire)>=queue.size()) return false;
        queue[w%queue.size()]=bank;
        write.store(w+1,std::memory_order_release);
        return true;
    }
    void consume() {
        const unsigned r=read.load(std::memory_order_relaxed);
        const unsigned w=write.load(std::memory_order_acquire);
        if(r!=w) {
            engine.configure(queue[(w-1)%queue.size()]);
            read.store(w,std::memory_order_release);
        } else engine.servicePending();
    }
};

static_assert(std::atomic<unsigned>::is_always_lock_free,"Lock-free indices required");

struct t_stochpacketenv {
    t_pxobject ob;
    EnvelopeState* state;
};

static t_class* klass=nullptr;

static void perform(t_stochpacketenv* x,t_object*,double** ins,long,double** outs,long,long frames,long,void*) {
    x->state->consume();
    for(long i=0;i<frames;++i) {
        outs[0][i]=x->ob.z_disabled ? 0 : x->state->engine.sample(ins[0][i]).envelope;
    }
}

static void dsp64(t_stochpacketenv* x,t_object* dsp,short*,double sampleRate,long,long) {
    {
        std::lock_guard<std::mutex> lock(x->state->producers);
        auto settings=x->state->desired;
        settings.sr=sampleRate;
        ++settings.reset;
        x->state->read.store(x->state->write.load());
        x->state->publish(settings);
    }
    object_method(dsp,gensym("dsp_add64"),x,perform,0,nullptr);
}

static void command(t_stochpacketenv* x,t_symbol* name,long argc,t_atom* argv) {
    std::lock_guard<std::mutex> lock(x->state->producers);
    auto settings=x->state->desired;
    if(name==gensym("reset")) ++settings.reset;
    else if(name==gensym("trigger")) ++settings.nextTrigger;
    else {
        if(argc!=1 || (atom_gettype(argv)!=A_LONG && atom_gettype(argv)!=A_FLOAT)) {
            object_error((t_object*)x,"%s requires one number",name->s_name);
            return;
        }
        const double value=atom_getfloat(argv);
        if(!std::isfinite(value)) {
            object_error((t_object*)x,"finite number required");
            return;
        }
        if(name==gensym("density")) settings.density=std::clamp(value,0.01,100.0);
        else if(name==gensym("shape")) settings.shape=std::clamp(value,0.05,100.0);
        else if(name==gensym("duration")) settings.durationMs=std::clamp(value,1.0,60000.0);
        else if(name==gensym("polyphony")) settings.polyphony=int(std::clamp(value,1.0,double(stoch::packet::MaxPackets)));
        else if(name==gensym("gain")) settings.gain=std::clamp(value,0.0,1.0);
        else if(name==gensym("seed")) {
            settings.seed=uint64_t(std::clamp(value,1.0,4294967295.0));
            ++settings.reset;
        }
    }
    if(!x->state->publish(settings))
        object_error((t_object*)x,"control queue full; latest value saved for the next DSP start (send slower while DSP runs)");
}

static void mode(t_stochpacketenv* x,t_symbol* value) {
    std::lock_guard<std::mutex> lock(x->state->producers);
    auto settings=x->state->desired;
    if(value==gensym("off") || value==gensym("bypass")) settings.mode=0;
    else if(value==gensym("gamma")) settings.mode=1;
    else if(value==gensym("external")) settings.mode=2;
    else {
        object_error((t_object*)x,"mode must be off, gamma, or external");
        return;
    }
    if(!x->state->publish(settings))
        object_error((t_object*)x,"control queue full; latest value saved for the next DSP start (send slower while DSP runs)");
}

static void window(t_stochpacketenv* x,t_symbol* value) {
    if(value!=gensym("gaussian"))
        object_error((t_object*)x,"window currently supports gaussian");
}

static void status(t_stochpacketenv* x) {
    std::lock_guard<std::mutex> lock(x->state->producers);
    const auto& settings=x->state->desired;
    const unsigned pending=x->state->write.load(std::memory_order_acquire)-x->state->read.load(std::memory_order_acquire);
    const char* modeName=settings.mode==1 ? "gamma" : settings.mode==2 ? "external" : "off";
    object_post((t_object*)x,
        "stochpacketenv~ 0.5.0 | mode %s density %.3f shape %.3f duration %.3f gain %.3f polyphony %d | pending %u/%u | reconfigure crossfade 20 ms",
        modeName,settings.density,settings.shape,settings.durationMs,settings.gain,
        settings.polyphony,pending,EnvelopeState::QueueCapacity);
}

static void assist(t_stochpacketenv*,void*,long io,long,char* text) {
    snprintf(text,512,"%s",io==ASSIST_INLET
        ? "(signal) Positive edges trigger in external mode; messages: mode, density, shape, duration, polyphony, gain, seed, trigger, reset, status"
        : "(signal) Summed Gaussian packet envelope; multiply a voice with *~");
}

static void freeobj(t_stochpacketenv* x) {
    dsp_free((t_pxobject*)x);
    delete x->state;
}

static void* create(t_symbol*,long,t_atom*) {
    auto* x=(t_stochpacketenv*)object_alloc(klass);
    if(!x) return nullptr;
    x->state=nullptr;
    dsp_setup((t_pxobject*)x,1);
    try { x->state=new EnvelopeState; }
    catch(...) { object_free(x); return nullptr; }
    outlet_new((t_object*)x,"signal");
    x->ob.z_misc|=Z_NO_INPLACE;
    return x;
}

extern "C" void C74_EXPORT ext_main(void*) {
    auto* c=class_new("stochpacketenv~",(method)create,(method)freeobj,sizeof(t_stochpacketenv),nullptr,A_GIMME,0);
    class_addmethod(c,(method)dsp64,"dsp64",A_CANT,0);
    class_addmethod(c,(method)assist,"assist",A_CANT,0);
    for(const char* name:{"density","shape","duration","polyphony","gain","seed","trigger","reset"})
        class_addmethod(c,(method)command,name,A_GIMME,0);
    class_addmethod(c,(method)mode,"mode",A_SYM,0);
    class_addmethod(c,(method)window,"window",A_SYM,0);
    class_addmethod(c,(method)status,"status",0);
    class_dspinit(c);
    class_register(CLASS_BOX,c);
    klass=c;
}
