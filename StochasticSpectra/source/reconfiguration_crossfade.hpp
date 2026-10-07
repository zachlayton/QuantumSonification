#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>

namespace stoch::transition {

// Keeps parameter snapshots out of the sample loop while preventing a new
// engine state from replacing an old one at a single sample. Configuration is
// serviced at vector boundaries; the sample path only advances two fixed-size
// engines and mixes their frames during the short transition.
template<class Engine,class Bank,class Mixer>
class ReconfigurationCrossfade {
    Engine current_{};
    Engine previous_{};
    Bank pending_{};
    Mixer mixer_{};
    double fadeMs_=20;
    uint64_t total_=0;
    uint64_t remaining_=0;
    bool initialized_=false;
    bool hasPending_=false;

    void begin(const Bank& bank) {
        previous_=current_;
        current_.configure(bank);
        total_=std::max<uint64_t>(2,uint64_t(std::llround(
            std::clamp(fadeMs_,1.0,200.0)*0.001*bank.s.sr)));
        remaining_=total_;
    }

public:
    explicit ReconfigurationCrossfade(double fadeMs=20):fadeMs_(fadeMs) {}

    void configure(const Bank& bank) {
        if(!initialized_) {
            current_.configure(bank);
            initialized_=true;
            return;
        }
        if(remaining_>0) {
            pending_=bank;
            hasPending_=true;
            return;
        }
        hasPending_=false;
        begin(bank);
    }

    // Call once per signal vector. A control received during a transition is
    // reduced to the newest complete snapshot and begins after the active fade.
    void servicePending() {
        if(initialized_ && remaining_==0 && hasPending_) {
            hasPending_=false;
            begin(pending_);
        }
    }

    auto sample(double input=0) {
        auto currentFrame=current_.sample(input);
        if(remaining_==0) return currentFrame;
        const auto previousFrame=previous_.sample(input);
        const uint64_t elapsed=total_-remaining_;
        const double u=total_>1 ? double(elapsed)/double(total_-1) : 1.0;
        const double weight=u*u*(3-2*u);
        --remaining_;
        return mixer_(previousFrame,currentFrame,weight);
    }

    bool transitioning() const { return remaining_>0; }
    bool hasPending() const { return hasPending_; }
    uint64_t transitionSamples() const { return total_; }
};

} // namespace stoch::transition
