#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include "reconfiguration_crossfade.hpp"

namespace stoch::packet {

constexpr int MaxPackets=64;
constexpr int RhythmSequenceLength=4096;

struct Random {
    uint64_t state=1;
    explicit Random(uint64_t seed=1):state(seed ? seed : 1) {}
    double uniform() {
        state^=state>>12; state^=state<<25; state^=state>>27;
        return (double((state*UINT64_C(2685821657736338717))>>11)+0.5)/9007199254740992.0;
    }
    std::array<double,2> normal() {
        constexpr double pi=3.14159265358979323846;
        const double radius=std::sqrt(-2*std::log(uniform()));
        const double phase=2*pi*uniform();
        return {radius*std::cos(phase),radius*std::sin(phase)};
    }
};

// Marsaglia-Tsang gamma sampler. This runs only when a control snapshot is
// built, never in the signal callback.
inline double gammaUnit(Random& rng,double shape) {
    shape=std::max(shape,0.05);
    if(shape<1) return gammaUnit(rng,shape+1)*std::pow(rng.uniform(),1/shape);
    const double d=shape-1.0/3.0,c=1/std::sqrt(9*d);
    for(;;) {
        const double x=rng.normal()[0];
        double v=1+c*x;
        if(v<=0) continue;
        v=v*v*v;
        const double u=rng.uniform(),x2=x*x;
        if(u<1-0.0331*x2*x2 || std::log(u)<0.5*x2+d*(1-v+std::log(v))) return d*v;
    }
}

// Corrected finite-support Gaussian: exactly zero at both ends and one at the
// center. It is an amplitude envelope, not a claim of wavelet admissibility.
inline double gaussianWindow(double unitPosition) {
    if(!(unitPosition>0 && unitPosition<1)) return 0;
    constexpr double sigma=1.0/6.0;
    const double edge=std::exp(-0.5*std::pow(0.5/sigma,2));
    const double z=(unitPosition-0.5)/sigma;
    return (std::exp(-0.5*z*z)-edge)/(1-edge);
}

struct Settings {
    double sr=48000;
    double density=3;
    double shape=2;
    double durationMs=150;
    double gain=1;
    int mode=0; // 0 bypass, 1 gamma renewal, 2 external trigger input/message.
    int polyphony=16;
    uint64_t seed=1701;
    uint64_t reset=1;
    uint64_t nextTrigger=0;
};

struct Bank {
    Settings s;
    std::array<uint64_t,RhythmSequenceLength> intervals{};
};

inline Bank makeBank(Settings settings) {
    settings.sr=std::clamp(settings.sr,8000.0,384000.0);
    settings.density=std::clamp(settings.density,0.01,100.0);
    settings.shape=std::clamp(settings.shape,0.05,100.0);
    settings.durationMs=std::clamp(settings.durationMs,1.0,60000.0);
    settings.gain=std::clamp(settings.gain,0.0,1.0);
    settings.mode=std::clamp(settings.mode,0,2);
    settings.polyphony=std::clamp(settings.polyphony,1,MaxPackets);
    Bank bank; bank.s=settings;
    Random rng(settings.seed^UINT64_C(0x6a09e667f3bcc909));
    const double scale=1/(settings.shape*settings.density);
    const double maximum=double(std::numeric_limits<uint64_t>::max()/4);
    for(auto& interval:bank.intervals) {
        const double samples=gammaUnit(rng,settings.shape)*scale*settings.sr;
        interval=uint64_t(std::llround(std::clamp(samples,1.0,maximum)));
    }
    return bank;
}

struct Frame {
    double envelope=1;
    bool event=false;
    int activePackets=0;
};

class Engine {
    struct Voice {
        bool active=false;
        uint64_t age=0;
        uint64_t duration=2;
    };
    Bank bank_{};
    std::array<Voice,MaxPackets> voices{};
    uint64_t countdown=0,intervalIndex=0,voiceSteals_=0,manualTriggers=0;
    bool previousSignalTrigger=false,initialized=false;

    void clear() { for(auto& voice:voices) voice.active=false; }
    void resetProcess() {
        clear(); countdown=0; intervalIndex=0; voiceSteals_=0;
        previousSignalTrigger=false; manualTriggers=0;
    }
    void startVoice() {
        Voice* voice=nullptr;
        for(int i=0;i<bank_.s.polyphony;++i) if(!voices[i].active) { voice=&voices[i]; break; }
        if(!voice) {
            voice=&voices[0];
            for(int i=1;i<bank_.s.polyphony;++i)
                if(voices[i].age>voice->age) voice=&voices[i];
            ++voiceSteals_;
        }
        *voice=Voice{};
        voice->active=true;
        voice->duration=std::max<uint64_t>(2,uint64_t(std::llround(bank_.s.durationMs*0.001*bank_.s.sr)));
    }

public:
    void configure(const Bank& next) {
        const bool reset=!initialized || next.s.reset!=bank_.s.reset;
        const bool modeChanged=initialized && next.s.mode!=bank_.s.mode;
        const uint64_t newManualTriggers=initialized ? next.s.nextTrigger-bank_.s.nextTrigger : 0;
        bank_=next;
        for(int i=bank_.s.polyphony;i<MaxPackets;++i) voices[i].active=false;
        if(reset || modeChanged) resetProcess();
        if(bank_.s.mode==2) manualTriggers+=newManualTriggers;
        initialized=true;
    }

    Frame sample(double triggerSignal=0) {
        if(bank_.s.mode==0) return {bank_.s.gain,false,0};
        bool event=false;
        if(bank_.s.mode==1 && countdown==0) {
            startVoice(); event=true;
            countdown=bank_.intervals[intervalIndex++%RhythmSequenceLength];
        }
        const bool signalHigh=std::isfinite(triggerSignal) && triggerSignal>0;
        if(bank_.s.mode==2 && ((signalHigh && !previousSignalTrigger) || manualTriggers>0)) {
            startVoice(); event=true;
            if(manualTriggers>0) --manualTriggers;
        }
        previousSignalTrigger=signalHigh;

        double value=0;
        int active=0;
        for(int i=0;i<bank_.s.polyphony;++i) {
            auto& voice=voices[i];
            if(!voice.active) continue;
            const double u=double(voice.age)/double(voice.duration-1);
            value+=gaussianWindow(u);
            ++active;
            if(++voice.age>=voice.duration) voice.active=false;
        }
        if(bank_.s.mode==1 && countdown>0) --countdown;
        return {bank_.s.gain*value,event,active};
    }

    uint64_t voiceSteals() const { return voiceSteals_; }
};

struct FrameMixer {
    Frame operator()(const Frame& previous,const Frame& current,double weight) const {
        return {
            (1-weight)*previous.envelope+weight*current.envelope,
            previous.event || current.event,
            current.activePackets
        };
    }
};

using ClickFreeEngine=stoch::transition::ReconfigurationCrossfade<Engine,Bank,FrameMixer>;

} // namespace stoch::packet
