/* QMW Physics Prototype v0.1 — evaluate this entire block in SuperCollider.
   Receive localhost OSC at 17900. Audio server execution has not been validated
   in the build environment. The Python offline WAV is the validated preview.
   Sound policy supplies Hz/seconds/gain. No physical state evolves in SC. */
(
s.waitForBoot {
    SynthDef(\qmwPhysicsPluck, { |out=0, freq=110, amp=0.18, decay=1.5, pan=0|
        var harmonics = (1..8);
        var frequencies = freq * harmonics;
        var allowed = frequencies < (SampleRate.ir * 0.45);
        var weights = allowed / harmonics;
        var decays = decay / harmonics.sqrt;
        var elapsed = Line.ar(0, decay * 8, decay * 8, doneAction:2);
        var envelopes = (-elapsed / decays).exp * (1 - (-elapsed / 0.002).exp);
        var signal = Mix(SinOsc.ar(frequencies) * weights * envelopes);
        signal = signal * amp / weights.sum.max(1);
        Out.ar(out, Pan2.ar(signal, pan));
    }).add;
    SynthDef(\qmwPhysicsMaster, { |in=0, out=0|
        Out.ar(out, Limiter.ar(In.ar(in, 2), 0.9));
    }).add;
    s.sync;
    if (~qmwPhysicsGroup.notNil) { ~qmwPhysicsGroup.free; };
    if (~qmwPhysicsMaster.notNil) { ~qmwPhysicsMaster.free; };
    if (~qmwPhysicsBus.notNil) { ~qmwPhysicsBus.free; };
    ~qmwPhysicsBus = Bus.audio(s, 2);
    ~qmwPhysicsGroup = Group.head(s);
    ~qmwPhysicsMaster = Synth.after(~qmwPhysicsGroup, \qmwPhysicsMaster,
        [\in, ~qmwPhysicsBus.index, \out, 0]);
    thisProcess.openUDPPort(17900);
    ~qmwSeenEventIDs = Set.new;
    ~qmwRecentEventIDs = List.new;
    ~qmwVoiceControls = IdentityDictionary.new;
    OSCdef(\qmwPhysicsFrame, { |message|
        ~qmwPhysicsSequence = message[1];
        ~qmwPhysicsTime = message[2];
        ~qmwPhysicsModel = message[3];
    }, '/qmw/v01/frame', recvPort:17900);
    OSCdef(\qmwPhysicsVoice, { |message|
        ~qmwVoiceControls[message[2]] = message.copyRange(3,6);
    }, '/qmw/v01/voice', recvPort:17900);
    OSCdef(\qmwPhysicsPluck, { |message|
        var eventID = message[2].asString;
        if (~qmwSeenEventIDs.includes(eventID).not) {
            ~qmwSeenEventIDs.add(eventID);
            ~qmwRecentEventIDs.add(eventID);
            if (~qmwRecentEventIDs.size > 8192) {
                ~qmwSeenEventIDs.remove(~qmwRecentEventIDs.removeAt(0));
            };
            Synth(\qmwPhysicsPluck, [
                \out, ~qmwPhysicsBus.index,
                \freq, message[6].clip(10,18000),
                \amp, message[7].clip(0,0.95),
                \decay, message[8].clip(0.01,30),
                \pan, message[9].clip(-1,1)
            ], ~qmwPhysicsGroup);
        };
    }, '/qmw/v01/pluck', recvPort:17900);
    "QMW physics receiver listening on UDP 17900".postln;
};
)

// Stop the receiver (evaluate when wanted):
// [\qmwPhysicsFrame, \qmwPhysicsVoice, \qmwPhysicsPluck].do { |key| OSCdef(key).free };
// ~qmwPhysicsGroup.free; ~qmwPhysicsMaster.free; ~qmwPhysicsBus.free;
