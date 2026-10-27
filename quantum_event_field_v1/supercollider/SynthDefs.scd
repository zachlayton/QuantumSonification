/* Four harmonic modal wavelets; all nonlinear processing is downstream of physics.
FX equations below are retained from the v4.2b-loaded v3 pulse voice. */
(
~qefDefine = {
    var voice = SynthDef(\qefWaveletV1, {
        |out=0, popBus=0, site=0, source=1, duration=0.3, strength=0.5|
        var p = In.kr(popBus, 4).max(0);
        var pa = Select.kr(site, p), pb = Select.kr(source, p);
        var morph = Lag.kr(pb / (pa + pb).max(1e-9), 0.01);
        var weightsA = \weightsA.kr([0.25, 0.25, 0.25, 0.25]);
        var weightsB = \weightsB.kr([0.25, 0.25, 0.25, 0.25]);
        var weights = ((weightsA * (1-morph)) + (weightsB * morph)).max(0).sqrt;
        var life = EnvGen.ar(Env([0, 1, 0], [0.003, duration], [0, -6.9]),
            doneAction: Done.freeSelf);
        var partials = SinOsc.ar(110 * (site+1) * (1..4), 0) * weights;
        // Different sites may share frequencies; the state label is its base harmonic.
        var mono = Mix(partials) * 0.5 * life * strength.clip(0, 1);
        Out.ar(out, Pan2.ar(mono, (site/3*1.6)-0.8));
    });
    var mixer = SynthDef(\qefMixerV1, {
        |inBus=0, out=0, fxSendBus=0, gain=0.08, fxSend=0, enabled=1,
        ringMixBus=0, ringFrequencyBus=0, wavefoldMixBus=0, wavefoldDriveBus=0,
        wavefoldWarpAmountBus=0, wavefoldWarpShapeBus=0, fuzzMixBus=0,
        fuzzDriveBus=0, fuzzSecondBus=0, fuzzThirdBus=0, fuzzHigherBus=0,
        fuzzBiasBus=0, fuzzToneBus=0|
        var dry = In.ar(inBus, 2);
        var ringMix = Lag.kr(In.kr(ringMixBus).clip(0, 1), 0.03);
        var ringFrequency = In.kr(ringFrequencyBus).clip(
            0.1, SampleRate.ir * 0.45
        );
        // sqrt(2) approximately loudness-compensates bipolar multiplication.
        var ringed = dry * SinOsc.ar(ringFrequency) * 2.sqrt;
        var ringOutput = XFade2.ar(dry, ringed, (ringMix * 2) - 1);
        var wavefoldMix = Lag.kr(
            In.kr(wavefoldMixBus).clip(0, 1), 0.03
        );
        var wavefoldDrive = Lag.kr(
            In.kr(wavefoldDriveBus).clip(1, 32), 0.03
        );
        var warpAmount = Lag.kr(In.kr(wavefoldWarpAmountBus).clip(0, 1), 0.03);
        var warpShape = In.kr(wavefoldWarpShapeBus).clip(0, 3).round;
        var bentPositive = ringOutput + (ringOutput.squared * 0.8);
        var bentNegative = ringOutput - (ringOutput.squared * 0.8);
        var sineWarp = (ringOutput * (pi * 0.5)).sin;
        var foldedWarp = (ringOutput * 2.5).fold(-1, 1);
        var warped = Select.ar(warpShape, [
            bentPositive, bentNegative, sineWarp, foldedWarp
        ]);
        // Warp is an exact bypass at zero. It changes the fold input shape,
        // while drive independently controls how densely that input is folded.
        var warpOutput = XFade2.ar(ringOutput, warped, (warpAmount * 2) - 1);
        // Pulse-only nonlinear chain: ring -> warp -> wavefolder -> fuzz.
        var folded = LeakDC.ar(
            (warpOutput * wavefoldDrive).fold(-1, 1)
        ) / wavefoldDrive.sqrt;
        var wavefoldOutput = XFade2.ar(
            ringOutput, folded, (wavefoldMix * 2) - 1
        );
        var fuzzMix = Lag.kr(In.kr(fuzzMixBus).clip(0, 1), 0.03);
        var fuzzDrive = Lag.kr(In.kr(fuzzDriveBus).clip(0.25, 12), 0.03);
        var fuzzSecond = Lag.kr(In.kr(fuzzSecondBus).clip(0, 2), 0.03);
        var fuzzThird = Lag.kr(In.kr(fuzzThirdBus).clip(0, 2), 0.03);
        var fuzzHigher = Lag.kr(In.kr(fuzzHigherBus).clip(0, 2), 0.03);
        var fuzzBias = Lag.kr(In.kr(fuzzBiasBus).clip(-0.75, 0.75), 0.03);
        var fuzzTone = Lag.kr(In.kr(fuzzToneBus).clip(0, 1), 0.03);
        // Big Muff-inspired topology: polynomial coloration provides explicit
        // 2nd/3rd/5th/7th-order content, then four coupling-capacitor-like
        // gain stages sustain and thicken it before the passive-style tone
        // stack. This is an audio adapter only, not quantum evolution.
        var fuzzInput = (HPF.ar(wavefoldOutput, 30) + fuzzBias).clip(-1, 1);
        var fuzzColor = fuzzInput + (fuzzInput.squared * fuzzSecond)
            + (fuzzInput.cubed * fuzzThird)
            + (fuzzInput.pow(5) * fuzzHigher * 0.55)
            + (fuzzInput.pow(7) * fuzzHigher * 0.24);
        var muffStage1 = (fuzzColor * (1.8 + fuzzDrive)).tanh;
        var muffStage2 = (HPF.ar(muffStage1, 48) * (2.4 + fuzzDrive * 0.8)).tanh;
        var muffStage3 = (LPF.ar(muffStage2, 7200) * (2.0 + fuzzDrive * 0.55)).tanh;
        var muffStage4 = (HPF.ar(muffStage3, 38) * (1.7 + fuzzDrive * 0.42)).tanh;
        // A low branch retains the woolly body while the high branch is the
        // familiar Muff tone network. Their equal-power weights prevent the
        // midpoint from collapsing into a thin, scooped-only sound.
        var muffLow = LPF.ar(muffStage4, 520 + ((1 - fuzzTone) * 2300));
        var muffHigh = HPF.ar(muffStage4, 420 + (fuzzTone * 2500));
        var muffBody = LPF.ar(muffStage4, 420) * 0.42;
        var muffToneStack = (muffLow * (1 - fuzzTone).sqrt)
            + (muffHigh * fuzzTone.sqrt) + muffBody;
        var fuzzed = LeakDC.ar(
            (muffToneStack * (1.25 + (fuzzDrive * 0.16))).tanh
        ) * 1.18;
        var emitted = XFade2.ar(wavefoldOutput, fuzzed, (fuzzMix * 2) - 1);

        // Gate AFTER the biased fuzz: Sound off cannot leave a DC/bias-derived tone.
        var safe = Limiter.ar(LeakDC.ar(emitted), 0.8)
            * Lag.kr(gain.clip(0, 0.3), 0.03) * Lag.kr(enabled, 0.01);
        Out.ar(out, safe);
        Out.ar(fxSendBus, safe * Lag.kr(fxSend.clip(0, 1), 0.03));
    });
    [voice, mixer]
};
)
