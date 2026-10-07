#include "../source/stochastic_core.hpp"
#include "../source/packet_envelope_core.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>

static void require(bool condition,const char* message) {
    if(!condition) throw std::runtime_error(message);
}

static bool close(double a,double b,double tolerance=1e-12) {
    return std::abs(a-b)<=tolerance;
}

int main() {
    // A rebuild starts with the exact next sample of the old spectral engine
    // and ends on the corresponding sample of the new engine.
    stoch::Settings oldSettings;
    oldSettings.sr=8000;
    oldSettings.gain=0.2;
    const auto oldBank=stoch::makeBank(oldSettings);

    auto newSettings=oldSettings;
    newSettings.f0=113;
    newSettings.slope=0.4;
    newSettings.gain=0.8;
    ++newSettings.reset;
    const auto newBank=stoch::makeBank(newSettings);

    stoch::ClickFreeEngine spectral;
    stoch::Engine oldReference,newReference;
    spectral.configure(oldBank);
    oldReference.configure(oldBank);
    newReference.configure(newBank);
    for(int n=0;n<137;++n) {
        const auto actual=spectral.sample();
        const auto expected=oldReference.sample();
        require(close(actual.wavetable,expected.wavetable),"initial spectral engine");
        require(close(actual.modal,expected.modal),"initial modal engine");
    }

    spectral.configure(newBank);
    const uint64_t spectralFade=spectral.transitionSamples();
    require(spectralFade==160,"20 ms spectral transition at 8 kHz");
    for(uint64_t n=0;n<spectralFade;++n) {
        const auto actual=spectral.sample();
        const auto oldFrame=oldReference.sample();
        const auto newFrame=newReference.sample();
        require(std::isfinite(actual.wavetable) && std::isfinite(actual.modal),"finite spectral transition");
        if(n==0) {
            require(close(actual.wavetable,oldFrame.wavetable),"spectral transition starts on old continuation");
            require(close(actual.modal,oldFrame.modal),"modal transition starts on old continuation");
        }
        if(n+1==spectralFade) {
            require(close(actual.wavetable,newFrame.wavetable),"spectral transition ends on new engine");
            require(close(actual.modal,newFrame.modal),"modal transition ends on new engine");
        }
    }

    // Rapid controls are serialized: the newest snapshot waits until the active
    // fade finishes, then begins from the exact continuation of the audible one.
    auto laterSettings=newSettings;
    laterSettings.f0=197;
    ++laterSettings.reset;
    const auto laterBank=stoch::makeBank(laterSettings);
    stoch::Engine laterReference;
    laterReference.configure(laterBank);
    spectral.configure(laterBank);
    spectral.configure(oldBank); // newest pending snapshot supersedes the prior one
    require(spectral.hasPending(),"rapid spectral update retained");
    for(uint64_t n=0;n<spectralFade;++n) {
        spectral.sample();
        laterReference.sample();
    }
    spectral.servicePending();
    require(spectral.transitioning(),"pending spectral transition starts at vector service");
    const auto pendingFirst=spectral.sample();
    const auto audibleContinuation=laterReference.sample();
    require(close(pendingFirst.wavetable,audibleContinuation.wavetable),"pending spectral update preserves continuity");

    // The envelope's most severe boundary is unity bypass -> a new gamma packet,
    // whose first raw sample is zero. The crossfade must start at unity instead.
    stoch::packet::Settings bypassSettings;
    bypassSettings.sr=8000;
    bypassSettings.mode=0;
    const auto bypassBank=stoch::packet::makeBank(bypassSettings);
    auto gammaSettings=bypassSettings;
    gammaSettings.mode=1;
    ++gammaSettings.reset;
    const auto gammaBank=stoch::packet::makeBank(gammaSettings);

    stoch::packet::ClickFreeEngine envelope;
    stoch::packet::Engine bypassReference,gammaReference;
    envelope.configure(bypassBank);
    bypassReference.configure(bypassBank);
    gammaReference.configure(gammaBank);
    envelope.configure(gammaBank);
    const uint64_t envelopeFade=envelope.transitionSamples();
    require(envelopeFade==160,"20 ms envelope transition at 8 kHz");
    for(uint64_t n=0;n<envelopeFade;++n) {
        const auto actual=envelope.sample();
        const auto oldFrame=bypassReference.sample();
        const auto newFrame=gammaReference.sample();
        require(std::isfinite(actual.envelope),"finite envelope transition");
        if(n==0) {
            require(close(oldFrame.envelope,1),"bypass reference is unity");
            require(close(newFrame.envelope,0),"new gamma packet begins at zero");
            require(close(actual.envelope,1),"envelope transition prevents unity-to-zero jump");
        }
        if(n+1==envelopeFade)
            require(close(actual.envelope,newFrame.envelope),"envelope transition ends on new engine");
    }

    std::cout << "PASS click-free reconfiguration: 20 ms spectral/modal and envelope crossfades,\n"
                 "exact transition endpoints, and serialized rapid control snapshots.\n";
}
