#include "../source/packet_envelope_core.hpp"
#include "../source/stochastic_core.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <vector>

void require(bool ok,const char* message) {
    if(!ok) throw std::runtime_error(message);
}

int main() {
    using namespace stoch::packet;

    // Gamma(k, scale=1/(k*lambda)) retains mean 1/lambda and CV 1/sqrt(k).
    for(double shape:{0.5,1.0,4.0}) {
        Settings settings; settings.density=5; settings.shape=shape;
        const auto bank=makeBank(settings),repeat=makeBank(settings);
        require(bank.intervals==repeat.intervals,"seeded interval reproducibility");
        double mean=0,second=0;
        for(const auto samples:bank.intervals) {
            const double interval=samples/settings.sr;
            mean+=interval; second+=interval*interval;
        }
        mean/=RhythmSequenceLength; second/=RhythmSequenceLength;
        const double cv=std::sqrt(std::max(0.0,second-mean*mean))/mean;
        require(std::abs(mean-1/settings.density)<0.015,"gamma interval mean");
        require(std::abs(cv-1/std::sqrt(shape))<0.12,"gamma interval coefficient of variation");
    }

    // Gamma mode starts at t=0 and follows the exact precomputed renewal intervals.
    Settings settings; settings.mode=1; settings.gain=1; settings.durationMs=10;
    auto bank=makeBank(settings);
    bank.intervals[0]=11; bank.intervals[1]=23; bank.intervals[2]=37;
    Engine engine; engine.configure(bank);
    std::vector<int> events;
    for(int n=0;n<80;++n) if(engine.sample().event) events.push_back(n);
    require(events.size()>=4,"renewal events generated");
    require(events[0]==0 && events[1]==11 && events[2]==34 && events[3]==71,"renewal interval schedule");

    require(gaussianWindow(0)==0 && gaussianWindow(1)==0,"window endpoints");
    require(std::abs(gaussianWindow(0.5)-1)<1e-14,"window unit peak");
    require(std::abs(gaussianWindow(0.25)-gaussianWindow(0.75))<1e-14,"window symmetry");

    // Overlaps sum inside the envelope object and remain bounded by polyphony.
    settings.sr=8000; settings.durationMs=200; settings.polyphony=2; ++settings.reset;
    bank=makeBank(settings); bank.intervals.fill(400);
    engine.configure(bank);
    int maximumActive=0;
    double maximumEnvelope=0;
    for(int n=0;n<2000;++n) {
        const auto frame=engine.sample();
        maximumActive=std::max(maximumActive,frame.activePackets);
        maximumEnvelope=std::max(maximumEnvelope,frame.envelope);
    }
    require(maximumActive==2,"overlapping envelope voices");
    require(maximumEnvelope>1,"overlapping windows sum");
    require(engine.voiceSteals()>0,"bounded polyphony voice stealing");

    // External mode accepts message-count triggers and positive signal edges.
    Settings external; external.mode=2; external.sr=8000; external.durationMs=20;
    auto externalBank=makeBank(external);
    Engine externalEngine; externalEngine.configure(externalBank);
    require(!externalEngine.sample().event,"external mode waits for a trigger");
    ++external.nextTrigger; externalBank=makeBank(external); externalEngine.configure(externalBank);
    require(externalEngine.sample().event,"message trigger starts an envelope");
    while(externalEngine.sample().activePackets) {}
    require(externalEngine.sample(1).event,"positive signal edge starts an envelope");
    require(!externalEngine.sample(1).event,"held-high signal does not retrigger");
    externalEngine.sample(0);
    require(externalEngine.sample(1).event,"a new positive edge retriggers");

    // Off mode is a unity bypass so the explicit Max *~ passes the voice unchanged.
    Settings bypass; bypass.mode=0; bypass.gain=1;
    Engine bypassEngine; bypassEngine.configure(makeBank(bypass));
    stoch::Settings spectral; spectral.gain=1;
    stoch::Engine spectralEngine; spectralEngine.configure(stoch::makeBank(spectral));
    for(int n=0;n<1000;++n) {
        const double voice=spectralEngine.sample().wavetable;
        const double envelope=bypassEngine.sample().envelope;
        require(envelope==1,"off mode is unity");
        require(voice*envelope==voice,"explicit multiplication preserves bypassed voice");
    }

    std::cout << "PASS modular packets: gamma mean/CV and exact renewal schedule, Gaussian envelope,\n"
                 "overlap/polyphony, external triggers, unity bypass, and explicit voice * envelope.\n";
}
