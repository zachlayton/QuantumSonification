(
// Shared native DSP definition for the live receiver and non-realtime tests.
~qmwYMBuildSynthDef = {
SynthDef(\qmwYangMillsModal16, {
    |out = 0, baseFreq = 55, amp = 0, coupling = 1, ringSeconds = 1.25,
    smoothingSeconds = 0.08, motionDrive = 0.12,
    strikeThreshold = 0.0005, spread = 0.85, gate = 1|
    // A conservative warp may concentrate several bounded source lanes.
    // The theoretical amplitude bound is sqrt(sum(source amplitude^2)) <= 4.
    var magnitude = NamedControl.kr(\magnitude, Array.fill(16, 0.0)).clip(0, 4);
    var speed = NamedControl.kr(\speed, Array.fill(16, 0.0)).clip(0, 1);
    var smoothed = Lag.kr(magnitude, smoothingSeconds.max(0.001));
    var movement = HPZ1.kr(magnitude).abs;
    var triggers = Trig1.kr(movement > strikeThreshold.max(1e-6), ControlDur.ir);
    var strikes = Decay2.kr(triggers, 0.004, 0.18) * Latch.kr(magnitude, triggers);
    var sustained = Lag.kr(speed, smoothingSeconds.max(0.001)) * smoothed * motionDrive.clip(0, 1);
    var frequencies = (baseFreq * (1..16)).clip(20, SampleRate.ir * 0.44);
    var decay = ringSeconds.clip(0.02, 12);
    var excitation = PinkNoise.ar(1 ! 16) * (strikes + sustained) * Lag.kr(coupling.clip(0, 1), 0.05);
    var modes = Ringz.ar(excitation, frequencies, decay) / (frequencies * decay).sqrt.max(1);
    var signal = Splay.ar(modes, spread.clip(0, 1), 1, 0, true);
    var envelope = EnvGen.kr(Env.asr(0.02, 1, 0.3), gate, doneAction: Done.freeSelf);
    signal = LeakDC.ar(signal) * Lag.kr(amp.clip(0, 1), 0.05);
    Out.ar(out, Limiter.ar(signal, 0.95, 0.01) * envelope);
})
};
)

