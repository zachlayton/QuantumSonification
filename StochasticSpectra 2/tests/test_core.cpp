#include "../source/stochastic_core.hpp"
#include <iostream>
#include <stdexcept>
void require(bool ok,const char* message) { if(!ok) throw std::runtime_error(message); }
int main() {
    stoch::Settings s; s.gain=1;
    auto b=stoch::makeBank(s); stoch::Engine e; e.configure(b);
    double error=0,power=0;
    for(int n=0;n<480000;++n) { auto f=e.sample(); error+=(f.wavetable-f.modal)*(f.wavetable-f.modal); power+=f.modal*f.modal; }
    double relative=std::sqrt(error/power);
    require(relative<2e-5,"wavetable/modal equivalence");
    auto repeat=stoch::makeBank(s); require(b.table==repeat.table,"seed reproducibility");
    // Ensemble mean, variance and lag covariance, exact analytic prediction.
    double mean=0,var=0,cov=0; int lag=17, count=40000;
    s.modes=1;
    for(int n=0;n<count;++n) {
        // Sample coefficients directly: avoids 40k unnecessary table builds.
        stoch::Random r(uint64_t(n+1)); auto z=r.normal();
        double later=z[0]*std::cos(2*stoch::pi*s.f0*lag/s.sr)+z[1]*std::sin(2*stoch::pi*s.f0*lag/s.sr);
        mean+=z[0]; var+=z[0]*z[0]; cov+=z[0]*later;
    }
    mean/=count; var/=count; cov/=count;
    require(std::abs(mean)<0.035 && std::abs(var-1)<0.035,"Gaussian ensemble moments");
    require(std::abs(cov-std::cos(2*stoch::pi*s.f0*lag/s.sr))<0.035,"line covariance");
    // Exact free-decay comparison (same initial random coefficients).
    s.motion=1; s.tau=0.1; ++s.reset; b=stoch::makeBank(s); e.configure(b);
    double maxDecayError=0;
    for(int n=0;n<48000;++n) {
        double t=n/s.sr, p=2*stoch::pi*s.f0*t;
        double expected=std::exp(-t/s.tau)*(b.a[0]*std::cos(p)+b.b[0]*std::sin(p));
        maxDecayError=std::max(maxDecayError,std::abs(e.sample().modal-expected));
    }
    require(maxDecayError<1e-10,"exact modal decay");
    // Sampled rotating OU process: covariance r^lag cos(angle*lag).
    s.motion=2; s.tau=0.02; ++s.reset; b=stoch::makeBank(s); e.configure(b);
    constexpr int L=240; std::array<double,L> history{};
    double m=0,v=0,c=0; int samples=48000*60;
    for(int n=0;n<samples+L;++n) {
        double x=e.sample().modal;
        if(n>=L) { m+=x; v+=x*x; c+=x*history[n%L]; }
        history[n%L]=x;
    }
    m/=samples; v/=samples; c/=samples;
    double expected=std::exp(-L/(s.sr*s.tau))*std::cos(2*stoch::pi*s.f0*L/s.sr);
    require(std::abs(m)<0.035 && std::abs(v-1)<0.07,"stationary variance");
    require(std::abs(c-expected)<0.07,"stationary lag covariance");
    s.f0=10000; s.modes=32; b=stoch::makeBank(s);
    require(b.active==2,"Nyquist harmonic cutoff");
    std::cout<<"PASS\nrelative table/modal RMS error: "<<relative<<"\nensemble mean/variance: "<<mean<<" / "<<var
             <<"\nmax decay error: "<<maxDecayError<<"\nOU mean/variance: "<<m<<" / "<<v<<"\nOU covariance: "<<c<<" expected "<<expected<<"\n";
}
