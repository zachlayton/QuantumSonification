#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include "reconfiguration_crossfade.hpp"

namespace stoch {
constexpr double pi = 3.14159265358979323846;
constexpr int MaxModes = 32, TableSize = 8192;
// Fixed algorithm, reproducible across standard libraries. Box-Muller pairs.
struct Random {
    uint64_t state = 1;
    explicit Random(uint64_t s=1): state(s ? s : 1) {}
    double uniform() {
        state ^= state >> 12; state ^= state << 25; state ^= state >> 27;
        return (double((state * UINT64_C(2685821657736338717)) >> 11) + 0.5) / 9007199254740992.0;
    }
    std::array<double,2> normal() {
        double r=std::sqrt(-2*std::log(uniform())), p=2*pi*uniform();
        return {r*std::cos(p),r*std::sin(p)};
    }
};
struct Settings {
    double sr=48000, f0=55, slope=2, tau=0.4, gain=0.15;
    int modes=16;
    double rate=1, interpMs=600, slewMs=80, ampdepth=1, phasedepth=1;
    int evolve=0, curve=1;
    uint64_t nextTarget=0;
    uint64_t seed=1701, reset=1;
    // 0: undamped, 1: free decay, 2: stationary stochastic modal process
    int motion=0;
};
struct Bank {
    Settings s;
    int active=0;
    std::array<double,MaxModes> a{},b{},variance{};
    std::array<double,TableSize> table{};
};
inline Bank makeBank(Settings s) {
    s.sr=std::clamp(s.sr,8000.0,384000.0);
    s.f0=std::clamp(s.f0,1.0,0.45*s.sr);
    s.modes=std::clamp(s.modes,1,MaxModes);
    s.slope=std::clamp(s.slope,0.0,6.0);
    s.tau=std::clamp(s.tau,0.001,60.0);
    s.gain=std::clamp(s.gain,0.0,1.0);
    s.motion=std::clamp(s.motion,0,2);
    s.rate=std::clamp(s.rate,0.01,100.0);
    s.interpMs=std::clamp(s.interpMs,0.0,60000.0);
    s.slewMs=std::clamp(s.slewMs,0.0,60000.0);
    s.ampdepth=std::clamp(s.ampdepth,0.0,1.0);
    s.phasedepth=std::clamp(s.phasedepth,0.0,1.0);
    s.evolve=s.evolve!=0; s.curve=s.curve!=0;
    Bank bank; bank.s=s;
    bank.active=std::min(s.modes,int(std::floor(0.45*s.sr/s.f0)));
    double total=0;
    for(int m=0;m<bank.active;++m) total += std::pow(m+1.0,-s.slope);
    Random rng(s.seed);
    for(int m=0;m<bank.active;++m) {
        bank.variance[m]=std::pow(m+1.0,-s.slope)/total;
        auto z=rng.normal();
        bank.a[m]=z[0]*std::sqrt(bank.variance[m]);
        bank.b[m]=z[1]*std::sqrt(bank.variance[m]);
        for(int j=0;j<TableSize;++j) {
            double p=2*pi*(m+1)*j/TableSize;
            bank.table[j]+=bank.a[m]*std::cos(p)+bank.b[m]*std::sin(p);
        }
    }
    return bank;
}
struct Frame { double wavetable,modal; };
// Finite-duration target interpolation followed by exponential slew.
// A retarget begins at the current interpolated command, preserving continuity.
struct Smoother {
    double start=0, target=0, command=0, value=0;
    uint64_t elapsed=0, duration=0;
    int shape=1;
    void reset(double v) { start=target=command=value=v; elapsed=duration=0; }
    void set(double v, uint64_t samples, int curve=1) { start=command; target=v; elapsed=0; duration=samples; shape=curve; }
    double tick(double alpha) {
        double u=duration ? std::min(1.0,double(++elapsed)/double(duration)) : 1.0;
        double w=shape ? u*u*(3-2*u) : u;
        command=start+(target-start)*w;
        value+=alpha*(command-value); return value;
    }
};
inline double wrap(double p) { return std::remainder(p,2*pi); }
class Engine {
    Bank bank_{};
    std::array<double,MaxModes> x{},y{},co{},si{},kick{};
    Random rng, morphRng;
    std::array<Smoother,MaxModes> amplitudes{}, phases{};
    std::array<double,TableSize> sine{};
    double targetClock=0, slewAlpha=1;
    uint64_t targetCount_=0;
    bool evolvingTable=false;
    void chooseTarget() {
        ++targetCount_;
        uint64_t duration=uint64_t(std::llround(bank_.s.interpMs*0.001*bank_.s.sr));
        for(int m=0;m<bank_.active;++m) {
            auto z=morphRng.normal();
            double baseA=std::hypot(bank_.a[m],bank_.b[m]);
            double baseP=std::atan2(bank_.b[m],bank_.a[m]);
            double nextA=std::hypot(z[0],z[1])*std::sqrt(bank_.variance[m]);
            double nextP=baseP+bank_.s.phasedepth*wrap(std::atan2(z[1],z[0])-baseP);
            amplitudes[m].set(baseA+bank_.s.ampdepth*(nextA-baseA),duration,bank_.s.curve);
            // Keep angles bounded without changing the represented waveform.
            double shift=2*pi*std::floor(phases[m].command/(2*pi));
            phases[m].start-=shift; phases[m].target-=shift;
            phases[m].command-=shift; phases[m].value-=shift;
            phases[m].set(phases[m].command+wrap(nextP-phases[m].command),duration,bank_.s.curve);
        }
        evolvingTable=true;
    }
    double lookup(double cycles) const {
        cycles-=std::floor(cycles);
        double pos=cycles*TableSize; int i=int(pos); double f=pos-i;
        return sine[i]+f*(sine[(i+1)%TableSize]-sine[i]);
    }
    double phase=0, decay=1;
    bool initialized=false;
public:
    Engine() { for(int i=0;i<TableSize;++i) sine[i]=std::sin(2*pi*i/TableSize); }
    void configure(const Bank& next) {
        bool reset=!initialized || next.s.reset!=bank_.s.reset;
        bool trigger=initialized && next.s.nextTarget!=bank_.s.nextTarget;
        bool enable=next.s.evolve && (!initialized || !bank_.s.evolve);
        bank_=next;
        const auto& s=bank_.s;
        decay=s.motion==0 ? 1.0 : std::exp(-1/(s.sr*s.tau));
        for(int m=0;m<MaxModes;++m) {
            double angle=2*pi*(m+1)*s.f0/s.sr;
            co[m]=std::cos(angle); si[m]=std::sin(angle);
            kick[m]=s.motion==2 ? std::sqrt(bank_.variance[m]*(-std::expm1(-2/(s.sr*s.tau)))) : 0;
            if(reset) { x[m]=bank_.a[m]; y[m]=bank_.b[m]; }
        }
        slewAlpha=s.slewMs<=0 ? 1 : -std::expm1(-1/(s.sr*s.slewMs*0.001));
        if(reset) {
            phase=0; rng=Random(s.seed ^ UINT64_C(0x123456789abcdef));
            morphRng=Random(s.seed ^ UINT64_C(0xfedcba987654321));
            targetClock=0; targetCount_=0; evolvingTable=false;
            for(int m=0;m<MaxModes;++m) {
                amplitudes[m].reset(std::hypot(bank_.a[m],bank_.b[m]));
                phases[m].reset(std::atan2(bank_.b[m],bank_.a[m]));
            }
        }
        if((reset && s.evolve) || enable || trigger) { chooseTarget(); targetClock=0; }
        initialized=true;
    }
    Frame sample(double excitation=0) {
        double pos=phase*TableSize;
        int i=int(pos); double f=pos-i;
        double wave=bank_.table[i]+f*(bank_.table[(i+1)%TableSize]-bank_.table[i]);
        if(evolvingTable) {
            wave=0;
            for(int m=0;m<bank_.active;++m) {
                double a=amplitudes[m].tick(slewAlpha);
                double p=phases[m].tick(slewAlpha);
                wave+=a*lookup((m+1)*phase-p/(2*pi)+0.25);
            }
        }
        if(bank_.s.evolve) {
            targetClock+=bank_.s.rate/bank_.s.sr;
            if(targetClock>=1) { targetClock-=std::floor(targetClock); chooseTarget(); }
        }
        double modal=0;
        for(int m=0;m<bank_.active;++m) {
            // Input is a per-sample quadrature impulse, not a force in SI units.
            if(std::isfinite(excitation)) y[m]+=excitation*std::sqrt(bank_.variance[m]);
            modal+=x[m];
            double nx=decay*(co[m]*x[m]+si[m]*y[m]);
            double ny=decay*(-si[m]*x[m]+co[m]*y[m]);
            if(bank_.s.motion==2) {
                auto z=rng.normal(); nx+=kick[m]*z[0]; ny+=kick[m]*z[1];
            }
            x[m]=std::abs(nx)<1e-280 ? 0 : nx;
            y[m]=std::abs(ny)<1e-280 ? 0 : ny;
        }
        phase+=bank_.s.f0/bank_.s.sr; phase-=std::floor(phase);
        return {bank_.s.gain*wave,bank_.s.gain*modal};
    }
    uint64_t targetCount() const { return targetCount_; }
};

struct FrameMixer {
    Frame operator()(const Frame& previous,const Frame& current,double weight) const {
        const double oldWeight=1-weight;
        return {
            oldWeight*previous.wavetable+weight*current.wavetable,
            oldWeight*previous.modal+weight*current.modal
        };
    }
};

using ClickFreeEngine=transition::ReconfigurationCrossfade<Engine,Bank,FrameMixer>;
}
