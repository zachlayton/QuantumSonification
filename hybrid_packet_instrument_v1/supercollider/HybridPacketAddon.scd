/* Additive hybrid v1. Load after v4.2b audio is ready. No factory presets modified.
Hamiltonian quadrature carrier is a sonification mapping, not direct phonon audio.
Spatial tap is 16 dry displacement pickups, not a WFS loudspeaker decoder. */
(
~hybridShutdown !? { ~hybridShutdown.() };
~hybridDiagnostics = nil;
~hybridState = (density: 8, duration: 0.08, carrier: 165, center: 0.5,
    width: 0.15, f0: 55, decay: 2, gain: 0.03, blend: 0, attack: 0.1,
    release: 1, envelopeDepth: 0, densityDepth: 0, normalize: 1, fxSend: 0,
    spatial: 0, phase: 0);
~hybridRanges = (density: [0, 4000], duration: [0.002, 2], carrier: [1, 12000],
    center: [0, 1], width: [0.01, 1], f0: [15, 1000], decay: [0.02, 20],
    gain: [0, 0.2], blend: [0, 1], attack: [0.001, 10], release: [0.005, 20],
    envelopeDepth: [0, 1], densityDepth: [0, 1], normalize: [0, 1],
    fxSend: [0, 1], spatial: [0, 1], phase: [-pi, pi]);
~hybridStop = {
    ~hybridStartRoutine !? { |r| r.stop }; ~hybridStartRoutine = nil;
    ~hybridGroup !? { |g| g.free };
    ~hybridEnv !? { |b| b.free };
    ~hybridGroup = nil; ~hybridNode = nil; ~hybridEnv = nil;
};
~hybridOnQuit = {
    // IDs belong to the old server generation; never free them on a new server.
    ~hybridStartRoutine !? { |r| r.stop }; ~hybridStartRoutine = nil;
    ~hybridGroup = nil; ~hybridNode = nil; ~hybridEnv = nil;
};
s.onQuitAdd(~hybridOnQuit);
~hybridDefine = {
    SynthDef(\qmwHybridBodyV1, {
        |out=0, fxSendBus=0, envBuf=0, density=8, duration=0.08, carrier=165,
        center=0.5, width=0.15, f0=55, decay=2, gain=0.03, blend=0,
        attack=0.1, release=1, envelopeDepth=0, densityDepth=0, normalize=1,
        fxSend=0, spatial=0, spatialAvailable=0, phase=0, t_burst=0, alive=0, baseEnabled=1,
        ringMixBus=0, ringFrequencyBus=0, wavefoldMixBus=0, wavefoldDriveBus=0,
        wavefoldWarpAmountBus=0, wavefoldWarpShapeBus=0, fuzzMixBus=0,
        fuzzDriveBus=0, fuzzSecondBus=0, fuzzThirdBus=0, fuzzHigherBus=0,
        fuzzBiasBus=0, fuzzToneBus=0|
        var re = Lag.kr(\re.kr(0 ! 16), 0.04);
        var im = Lag.kr(\im.kr(0 ! 16), 0.04);
        var ad = EnvGen.kr(Env([0, 1, 0], [attack, release], [-2, -4]), t_burst);
        // Grain pool bound: density is capped to 256 / packet duration (512 slots).
        var rate = density.min(256 / duration) * ((1-densityDepth) + (densityDepth * ad));
        var trigger = Dust.ar(rate);
        // Shared trigger and Gaussian envelope preserve relative quadrature phase.
        var grainCos = GrainIn.ar(1, trigger, duration,
            SinOsc.ar(carrier, phase + (pi/2)), 0, envBuf, 512);
        var grainSin = GrainIn.ar(1, trigger, duration,
            SinOsc.ar(carrier, phase), 0, envBuf, 512);
        // Coherent carrier: compensate mean overlap, not independent-grain power.
        var power = Select.kr(normalize.round, [1, (rate * duration).max(1).reciprocal]);
        var coupling = (1-envelopeDepth) + (envelopeDepth * ad);
        var live = Lag.kr(alive, 0.1);
        var modes = Array.fill(16, { |j|
            var k = (j+1) * pi;
            var overlap = (k*center).sin * ((k*width).squared * -0.5).exp;
            var synthetic = grainCos * overlap * power;
            var quantum = ((re[j] * grainCos) - (im[j] * grainSin)) * live * power;
            var force = ((synthetic * (1-blend)) + (quantum * blend))
                * coupling * Lag.kr(baseEnabled, 0.03);
            Ringz.ar(force * 0.01, (f0*(j+1)).clip(15, SampleRate.ir*0.4), decay)
        });
        var pickups = Array.fill(16, { |p|
            Mix(Array.fill(16, { |j| modes[j] * (((p+1)/17) * (j+1)*pi).sin })) / 4
        });
        var dry = [pickups[4], pickups[11]] * Lag.kr(gain, 0.05);
        var ringMix = Lag.kr(In.kr(ringMixBus).clip(0, 1), 0.03);
        var ringFrequency = In.kr(ringFrequencyBus).clip(
            0.1, SampleRate.ir * 0.45
        );
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
        var warped = Select.ar(warpShape, [
            ringOutput + (ringOutput.squared * 0.8),
            ringOutput - (ringOutput.squared * 0.8),
            (ringOutput * (pi * 0.5)).sin,
            (ringOutput * 2.5).fold(-1, 1)
        ]);
        var warpOutput = XFade2.ar(ringOutput, warped, (warpAmount * 2) - 1);
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
        var fuzzInput = (HPF.ar(wavefoldOutput, 30) + fuzzBias).clip(-1, 1);
        var fuzzColor = fuzzInput + (fuzzInput.squared * fuzzSecond)
            + (fuzzInput.cubed * fuzzThird)
            + (fuzzInput.pow(5) * fuzzHigher * 0.55)
            + (fuzzInput.pow(7) * fuzzHigher * 0.24);
        var muffStage1 = (fuzzColor * (1.8 + fuzzDrive)).tanh;
        var muffStage2 = (HPF.ar(muffStage1, 48) * (2.4 + fuzzDrive * 0.8)).tanh;
        var muffStage3 = (LPF.ar(muffStage2, 7200) * (2.0 + fuzzDrive * 0.55)).tanh;
        var muffStage4 = (HPF.ar(muffStage3, 38) * (1.7 + fuzzDrive * 0.42)).tanh;
        var muffLow = LPF.ar(muffStage4, 520 + ((1 - fuzzTone) * 2300));
        var muffHigh = HPF.ar(muffStage4, 420 + (fuzzTone * 2500));
        var muffBody = LPF.ar(muffStage4, 420) * 0.42;
        var muffToneStack = (muffLow * (1 - fuzzTone).sqrt)
            + (muffHigh * fuzzTone.sqrt) + muffBody;
        var fuzzed = LeakDC.ar(
            (muffToneStack * (1.25 + (fuzzDrive * 0.16))).tanh
        ) * 1.18;
        var emitted = XFade2.ar(wavefoldOutput, fuzzed, (fuzzMix * 2) - 1);

        Out.ar(out, Limiter.ar(emitted, 0.8));
        Out.ar(fxSendBus, Limiter.ar(emitted, 0.8) * Lag.kr(fxSend, 0.05));
        // Never write to private buses masquerading as hardware: compiled optional tap.
        if(~hybridSpatialConfigured == true, {
            Out.ar(4, Limiter.ar(pickups * Lag.kr(gain, 0.05), 0.8)
                * spatial * spatialAvailable * (NumOutputBuses.ir >= 20));
        });
    }).add;
};
~hybridSet = { |name, value|
    var range = ~hybridRanges[name];
    if(range.notNil and: { value.isNumber } and: { value.isNaN.not } and: { value.abs < 1e12 }, {
        value = value.clip(range[0], range[1]);
        ~hybridState[name] = value;
        ~hybridNode !? { |n| n.set(name, value) };
    });
};
~hybridStart = {
    if(s.serverRunning and: { ~qmwQFTV3AudioReady == true }
        and: { ~qmwQFTV3SourceGroup.notNil }
        and: { ~qmwQFTV42BFXSendBus.notNil }, {
        ~hybridStop.();
        ~hybridStartRoutine = Routine({
            var args;
            ~hybridSpatialConfigured = (~hybridEnableSpatial == true)
                and: { s.options.numOutputBusChannels >= 20 };
            ~hybridDefine.(); s.sync;
            ~hybridEnv = Buffer.sendCollection(s, Array.fill(1024, { |i|
                var x = ((i/1023)*8)-4;
                ((x.squared * -0.5).exp - (-8).exp).max(0)
            }), 1); s.sync;
            ~hybridBaseGroup = ~qmwQFTV3SourceGroup;
            ~hybridGroup = Group.tail(~hybridBaseGroup);
            args = [\out, ~qmwQFTV3SourceBus.index,
                \fxSendBus, ~qmwQFTV42BFXSendBus.index, \envBuf, ~hybridEnv.bufnum,
                \spatialAvailable, ~hybridSpatialConfigured.asInteger,
                \baseEnabled, ~qmwQFTV3SoundEnabled ? 1];
            [ [\ringMixBus, ~qmwQFTV3RingModMixBus],
              [\ringFrequencyBus, ~qmwQFTV3RingModFrequencyBus],
              [\wavefoldMixBus, ~qmwQFTV3WavefoldMixBus],
              [\wavefoldDriveBus, ~qmwQFTV3WavefoldDriveBus],
              [\wavefoldWarpAmountBus, ~qmwQFTV3WavefoldWarpAmountBus],
              [\wavefoldWarpShapeBus, ~qmwQFTV3WavefoldWarpShapeBus],
              [\fuzzMixBus, ~qmwQFTV3FuzzMixBus], [\fuzzDriveBus, ~qmwQFTV3FuzzDriveBus],
              [\fuzzSecondBus, ~qmwQFTV3FuzzSecondBus], [\fuzzThirdBus, ~qmwQFTV3FuzzThirdBus],
              [\fuzzHigherBus, ~qmwQFTV3FuzzHigherBus], [\fuzzBiasBus, ~qmwQFTV3FuzzBiasBus],
              [\fuzzToneBus, ~qmwQFTV3FuzzToneBus]
            ].do { |pair| args = args ++ [pair[0], pair[1].index] };
            ~hybridState.keysValuesDo { |key, value| args = args ++ [key, value] };
            ~hybridNode = Synth.tail(~hybridGroup, \qmwHybridBodyV1, args);
            ~hybridLastFrame = -1e9; ~hybridLastSeq = -1;
            "Hybrid started: stereo -> existing source/FX bus; spatial pickups %".format(
                ~hybridSpatialConfigured).postln;
        }).play(AppClock);
    }, { "Start base v4.2b audio first, then Hybrid Start.".warn });
};
thisProcess.openUDPPort(17920);
~hybridOSCNames = List.new;
~hybridRanges.keysDo { |key|
    var defName = ("hybrid_" ++ key).asSymbol;
    ~hybridOSCNames.add(defName);
    OSCdef(defName, { |msg| if(msg.size == 2, { ~hybridSet.(key, msg[1]) }) },
        ("/qmw/hybrid/control/" ++ key).asSymbol, recvPort: 17920);
};
OSCdef(\hybridStartOSC, { { ~hybridStart.() }.defer }, '/qmw/hybrid/start', recvPort: 17920);
OSCdef(\hybridStopOSC, { { ~hybridStop.() }.defer }, '/qmw/hybrid/stop', recvPort: 17920);
OSCdef(\hybridBurst, { ~hybridNode !? { |n| n.set(\t_burst, 1) } },
    '/qmw/hybrid/burst', recvPort: 17920);
OSCdef(\hybridProjection, { |msg|
    if(msg.size == 39 and: { ~hybridNode.notNil }
        and: { msg.copyRange(1,38).every { |v| v.isNumber and: { v.isNaN.not } and: { v.abs < 1e12 } } }, {
        if((msg[1] > ~hybridLastSeq) or: { (Main.elapsedTime - ~hybridLastFrame) > 1 }, {
            ~hybridLastSeq = msg[1]; ~hybridLastFrame = Main.elapsedTime;
            ~hybridNode.setn(\re, msg.copyRange(7,22));
            ~hybridNode.setn(\im, msg.copyRange(23,38));
            ~hybridNode.set(\alive, 1);
            ~hybridDiagnostics = msg.copyRange(1,6);
        });
    });
}, '/qmw/hybrid/projection', recvPort: 17920);
~hybridWatch = Routine({ loop {
    if(~hybridNode.notNil, {
        if((~qmwQFTV3SourceGroup !== ~hybridBaseGroup)
            or: { ~qmwQFTV3AudioReady != true }, {
            ~hybridStop.(); "Hybrid stopped: base routing changed. Press Start again.".warn;
        }, {
            ~hybridNode.set(\baseEnabled, ~qmwQFTV3SoundEnabled ? 1);
            if((Main.elapsedTime - ~hybridLastFrame) > 0.5, { ~hybridNode.set(\alive, 0) });
        });
    });
    ~hybridStatus !? { |view|
        var state = if(~hybridNode.isNil, { "stopped" }, {
            if((Main.elapsedTime - ~hybridLastFrame) > 0.5, { "H stale / muted" }, { "H live" })
        });
        var effective = ~hybridState[\density].min(256 / ~hybridState[\duration]);
        var metrics = if(~hybridDiagnostics.isNil, { "no Hamiltonian frame" }, {
            "norm %   E %   K %   V %".format(*~hybridDiagnostics.copyRange(2,5).round(0.001))
        });
        view.string_("% | max cloud rate %/s | spatial enabled %\n%".format(
            state, effective.round(0.1), ~hybridSpatialConfigured ? false, metrics));
    };
    0.2.wait;
} }).play(AppClock);
~hybridWindow = Window("QMW hybrid packet excitation v1", Rect(70, 70, 560, 720)).front;
Button(~hybridWindow, Rect(10,10,100,28)).states_([["Start"]]).action_({ ~hybridStart.() });
Button(~hybridWindow, Rect(120,10,100,28)).states_([["Stop"]]).action_({ ~hybridStop.() });
Button(~hybridWindow, Rect(230,10,100,28)).states_([["AD burst"]]).action_({
    ~hybridNode !? { |n| n.set(\t_burst,1) }
});
StaticText(~hybridWindow, Rect(10,42,540,42)).string_(
    "Blend 0: synthesis; 1: Hamiltonian (requires Python).\nRing/fold/fuzz and Clouds/VST controls remain in base windows.");
~hybridState.keys.asArray.sort.do { |key, i|
    var range = ~hybridRanges[key];
    StaticText(~hybridWindow, Rect(10,90+(i*28),140,24)).string_(key.asString);
    NumberBox(~hybridWindow, Rect(155,90+(i*28),120,24))
        .value_(~hybridState[key]).clipLo_(range[0]).clipHi_(range[1])
        .action_({ |view| ~hybridSet.(key, view.value) });
};
~hybridShutdown = {
    ~hybridStop.(); ~hybridWatch !? { |r| r.stop };
    s.onQuitRemove(~hybridOnQuit);
    ~hybridOSCNames !? { |names| names.do { |name| OSCdef(name).free } };
    OSCdef(\hybridBurst).free; OSCdef(\hybridProjection).free;
    OSCdef(\hybridStartOSC).free; OSCdef(\hybridStopOSC).free;
    ~hybridWindow !? { |w| w.onClose = nil; w.close }; ~hybridWindow = nil; ~hybridStatus = nil;
};
~hybridStatus = StaticText(~hybridWindow, Rect(10, 660, 540, 50)).string_("Stopped");
~hybridWindow.onClose = { ~hybridShutdown.() };
"Hybrid ready. Start base audio, then press Hybrid Start.".postln;
)
