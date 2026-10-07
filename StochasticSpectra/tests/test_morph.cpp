#include "../source/stochastic_core.hpp"
#include <iostream>
#include <stdexcept>
void require(bool b,const char* m) { if(!b) throw std::runtime_error(m); }
int main() {
    stoch::Smoother f; f.reset(0); f.set(1,4800,0);
    for(int i=0;i<2400;++i) f.tick(1);
    require(std::abs(f.value-0.5)<1e-12,"linear interpolation midpoint");
    f.set(0,4800,1);
    require(std::abs(f.command-0.5)<1e-12,"retarget continuity");
    for(int i=0;i<4800;++i) f.tick(1);
    require(std::abs(f.value)<1e-12,"finite interpolation endpoint");
    f.reset(0); f.set(1,0);
    double alpha=-std::expm1(-1/4800.0);
    for(int i=0;i<4800;++i) f.tick(alpha);
    require(std::abs(f.value-(1-std::exp(-1.0)))<1e-12,"100 ms slew time constant");
    f.reset(0);f.set(1,0);require(f.tick(1)==1,"zero-time bypass");
    stoch::Settings s; s.slope=0.5; s.modes=24; s.evolve=1; s.rate=2;
    s.interpMs=300;s.slewMs=80;
    auto bank=stoch::makeBank(s); stoch::Engine a,b;
    a.configure(bank);b.configure(bank);
    double difference=0;
    for(int i=0;i<480000;++i) {
        auto x=a.sample(),y=b.sample();
        require(std::isfinite(x.wavetable),"finite evolving samples");
        require(x.wavetable==y.wavetable,"seeded evolution reproducibility");
        difference+=(x.wavetable-x.modal)*(x.wavetable-x.modal);
    }
    require(difference/480000>0.005,"audible-scale evolving/frozen difference");

    // `rate` is target arrivals per second. It preserves scheduler phase when
    // edited, but changes the subsequent target count without resetting sound.
    stoch::Settings timed; timed.sr=8000; timed.f0=50; timed.evolve=1;
    timed.rate=1; timed.interpMs=200; timed.slewMs=20;
    stoch::Engine scheduler; scheduler.configure(stoch::makeBank(timed));
    require(scheduler.targetCount()==1,"evolve starts one target immediately");
    for(int i=0;i<16000;++i) scheduler.sample();
    require(scheduler.targetCount()==3,"rate 1 schedules one target per second");
    timed.rate=4;
    scheduler.configure(stoch::makeBank(timed));
    for(int i=0;i<8000;++i) scheduler.sample();
    require(scheduler.targetCount()==7,"live rate change schedules four targets per second");

    auto slowSettings=timed,fastSettings=timed;
    slowSettings.rate=0.5; fastSettings.rate=8;
    ++slowSettings.reset; fastSettings.reset=slowSettings.reset;
    stoch::Engine slowRate,fastRate;
    slowRate.configure(stoch::makeBank(slowSettings));
    fastRate.configure(stoch::makeBank(fastSettings));
    double rateContrast=0;
    for(int i=0;i<4*8000;++i) {
        const double delta=slowRate.sample().wavetable-fastRate.sample().wavetable;
        rateContrast+=delta*delta;
    }
    rateContrast=std::sqrt(rateContrast/(4*8000));
    require(rateContrast>0.02,"contrasting rates produce contrasting evolving signals");
    // Freeze target generation, allow interpolation/slew to finish, then verify periodicity.
    s.evolve=0;a.configure(stoch::makeBank(s));
    for(int i=0;i<480000;++i) a.sample();
    std::array<double,9600> period{}; // 11 cycles at 55 Hz
    for(auto& v:period) v=a.sample().wavetable;
    double freezeError=0;
    for(auto v:period) freezeError=std::max(freezeError,std::abs(v-a.sample().wavetable));
    require(freezeError<1e-9,"evolve off settles to fixed cycle");
    // Zero depths leave the base coefficients unchanged.
    s.evolve=1;s.ampdepth=s.phasedepth=0;++s.reset;
    a.configure(stoch::makeBank(s));double zeroError=0;
    for(int i=0;i<48000;++i) {auto x=a.sample();zeroError+=std::pow(x.wavetable-x.modal,2);}
    require(std::sqrt(zeroError/48000)<1e-6,"zero depths preserve original tone");
    std::cout<<"PASS morph: interpolation endpoint, continuous retarget, slew time constant, zero bypass,\nseed reproducibility, exact live rate scheduling, evolving signal, freeze settling, zero depths.\n"
             <<"Evolving/frozen RMS difference: "<<std::sqrt(difference/480000)<<"\nFreeze periodicity error: "<<freezeError<<"\n";
    std::cout<<"Slow/fast rate RMS contrast: "<<rateContrast<<"\n";
}
