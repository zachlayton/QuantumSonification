/* QMW QFT V4.4: GPE-driven timbre for inherited discrete pulse voices. */
(
var baseStop = ~qmwQFTV3Stop;
var baseSpawnPulseVoice = ~qmwQFTV3SpawnPulseVoice;
var baseUpdateFlowAudio = ~qmwQFTV43UpdateFlowAudio;
var baseUpdateRingMod = ~qmwQFTV3UpdateRingMod;
var baseUpdateWavefold = ~qmwQFTV3UpdateWavefold;
var baseUpdateFuzz = ~qmwQFTV3UpdateFuzz;
~qmwQFTV44GPEPort = 17867;
~qmwQFTV44GPERoot = "/qmw/gpe";
~qmwQFTV44GPEControlPort = 17868;
~qmwQFTV44GPEControl = NetAddr("127.0.0.1", ~qmwQFTV44GPEControlPort);
~qmwQFTV44GPEEnabled = 1;
~qmwQFTV44GPEPulseTimbreDepth = 0.42;
~qmwQFTV44ProbabilityPulseMix = 0.35;
~qmwQFTV44TerrainPulseMix = 0.35;
~qmwQFTV44CoherencePulseEdge = 0.20;
~qmwQFTV44GPERevision = -1;
~qmwQFTV44GPEValid = false;
~qmwQFTV44GPEDensity = 0.0;
~qmwQFTV44GPEPeak = 0.0;
~qmwQFTV44GPEFlowX = 0.0;
~qmwQFTV44GPEFlowSpeed = 0.0;
~qmwQFTV44GPEVortexCount = 0;
~qmwQFTV44GPEMagnitudes = Array.fill(8, 0.0);
~qmwQFTV44GPEPhases = Array.fill(8, 0.0);
~qmwQFTV44GPEStageMagnitudes = ~qmwQFTV44GPEMagnitudes.copy;
~qmwQFTV44GPEStagePhases = ~qmwQFTV44GPEPhases.copy;
~qmwQFTV44GPEPulseTimbre = (ringMix: 0.0, ringHarmonic: 1.0,
    ringDetune: 1.0, wavefoldMix: 0.0, wavefoldDrive: 1.0, fuzzMix: 0.0);
~qmwQFTV44UpdateGPEPulseTimbre = {
    var densityAmount = (~qmwQFTV44GPEDensity * 10).tanh;
    var flowAmount = (~qmwQFTV44GPEFlowSpeed * 3).tanh;
    var modalAmount = ~qmwQFTV44GPEMagnitudes.maxItem.clip(0, 1);
    var dominantMode = ~qmwQFTV44GPEMagnitudes.maxIndex ? 0;
    var depth = ~qmwQFTV44GPEPulseTimbreDepth.clip(0, 1)
        * ~qmwQFTV44GPEEnabled;
    // P-flow and terrain flow retain their different source scalings. They
    // are sampled here only as pulse material, never rendered as a carrier.
    var sensitivityScale = ~qmwQFTV43FlowSensitivity / 180.0;
    var probabilityAmount = (~qmwQFTV43ProbabilityMaxFlux
        * sensitivityScale * 1.5).tanh.clip(0, 1);
    var terrainAmount = (~qmwQFTV43TerrainMaxFlux
        * ~qmwQFTV43FlowSensitivity).tanh.clip(0, 1);
    var coherenceAmount = ((~qmwQFTV43ProbabilityCoherenceFlow
        * sensitivityScale * 0.75)
        + (~qmwQFTV43TerrainCoherenceFlow
            * ~qmwQFTV43FlowSensitivity * 0.25)).tanh.clip(0, 1);
    var pFlowRing = probabilityAmount * ~qmwQFTV44ProbabilityPulseMix.clip(0, 1);
    var terrainFold = terrainAmount * ~qmwQFTV44TerrainPulseMix.clip(0, 1);
    var coherenceEdge = coherenceAmount * ~qmwQFTV44CoherencePulseEdge.clip(0, 1);
    // This is a prepared event-timbre state, not a live audio control. The
    // spawn wrapper below snapshots it into private buses for each new pulse,
    // leaving already sounding pulse tails untouched.
    ~qmwQFTV44GPEPulseTimbre = (
        // Carry the inherited V3 GUI effect controls into V4.4's private
        // onset buses.  Without this, V4.4 intercepts a new pulse but the
        // old GUI writes only to buses that that pulse no longer reads.
        ringMix: (~qmwQFTV3RingModBlend + (depth * flowAmount) + pFlowRing).clip(0, 1),
        ringHarmonic: (~qmwQFTV3RingModHarmonic + dominantMode + ~qmwQFTV44GPEVortexCount).clip(1, 16),
        // Preserve the manual ring fine-tune in V4.4's private onset buses;
        // FieldFrame phase detune multiplies this value when enabled.
        ringDetune: 2.pow(~qmwQFTV3RingModFineTuneCents.clip(-100, 100) / 1200),
        wavefoldMix: (~qmwQFTV3WavefoldBlend + (depth * densityAmount * (0.35 + (0.65 * modalAmount))) + terrainFold).clip(0, 1),
        wavefoldDrive: (~qmwQFTV3WavefoldDrive + (10 * depth * modalAmount) + (8 * terrainFold)).clip(1, 32),
        fuzzMix: (~qmwQFTV3FuzzBlend + coherenceEdge).clip(0, 1)
    );
    { ~qmwQFTV44GPEStatus !? { |view|
        view.string_("PULSE MATERIAL / GPE rho % speed % / P-flow % / terrain % / coherence %".format(
            ~qmwQFTV44GPEDensity.round(0.0001), ~qmwQFTV44GPEFlowSpeed.round(0.0001),
            probabilityAmount.round(0.001), terrainAmount.round(0.001), coherenceAmount.round(0.001)))
    } }.defer
};

// Keep V4.3's carrier manually available, but convert each completed flow
// frame into prepared V4.4 pulse material as well.
~qmwQFTV43UpdateFlowAudio = {
    baseUpdateFlowAudio.value;
    ~qmwQFTV44UpdateGPEPulseTimbre.value
};

// V3 effect sliders remain authoritative manual sound-design controls.  Their
// values are sampled by V4.4 at the next pulse onset alongside field material.
~qmwQFTV3UpdateRingMod = {
    baseUpdateRingMod.value;
    ~qmwQFTV44UpdateGPEPulseTimbre.value
};
~qmwQFTV3UpdateWavefold = {
    baseUpdateWavefold.value;
    ~qmwQFTV44UpdateGPEPulseTimbre.value
};
~qmwQFTV3UpdateFuzz = {
    baseUpdateFuzz.value;
    ~qmwQFTV44UpdateGPEPulseTimbre.value
};

~qmwQFTV3SpawnPulseVoice = { |definition, arguments|
    var values = arguments.copy;
    var buses, replacements;
    var voice, frequencyIndex, baseFrequencyIndex, onsetFrequency;
    if((~qmwQFTV44GPEEnabled <= 0) and: {
        (~qmwQFTV44ProbabilityPulseMix + ~qmwQFTV44TerrainPulseMix
            + ~qmwQFTV44CoherencePulseEdge) <= 0
    } and: {
        (~qmwQFTV44FieldFrameEnabled ? 0) <= 0
    }, {
        baseSpawnPulseVoice.value(definition, values)
    }, {
        // Preserve the selected-scale/site tuning already calculated by RenderPulse.
        // Simple voices call it \frequency; Gaussian and FM voices call it
        // \baseFreq. The material ring must follow that tuned frequency rather
        // than a fixed global fundamental, otherwise it perceptually masks the
        // very scale the pulse is meant to articulate.
        frequencyIndex = values.indexOf(\frequency);
        baseFrequencyIndex = values.indexOf(\baseFreq);
        onsetFrequency = if(frequencyIndex.notNil, {
            values[frequencyIndex + 1]
        }, {
            if(baseFrequencyIndex.notNil, {
                values[baseFrequencyIndex + 1]
            }, { ~qmwQFTV3Fundamental })
        }).asFloat.clip(0.1, 16000);
        buses = [Bus.control(s, 1), Bus.control(s, 1), Bus.control(s, 1), Bus.control(s, 1), Bus.control(s, 1)];
        buses[0].set(~qmwQFTV44GPEPulseTimbre[\ringMix]);
        buses[1].set((onsetFrequency * ~qmwQFTV44GPEPulseTimbre[\ringHarmonic]
            * (~qmwQFTV44GPEPulseTimbre[\ringDetune] ? 1.0)).clip(0.1, 16000));
        buses[2].set(~qmwQFTV44GPEPulseTimbre[\wavefoldMix]);
        buses[3].set(~qmwQFTV44GPEPulseTimbre[\wavefoldDrive]);
        buses[4].set(~qmwQFTV44GPEPulseTimbre[\fuzzMix]);
        replacements = [\ringMixBus, buses[0].index, \ringFrequencyBus, buses[1].index,
            \wavefoldMixBus, buses[2].index, \wavefoldDriveBus, buses[3].index,
            \fuzzMixBus, buses[4].index];
        replacements.pairsDo { |key, value|
            var index = values.indexOf(key);
            if(index.notNil) { values[index + 1] = value }
        };
        voice = baseSpawnPulseVoice.value(definition, values);
        if(voice.notNil) { voice.onFree({ { buses.do(_.free) }.defer }) } {
            buses.do(_.free)
        };
        voice
    })
};

OSCdef(\qmwQFTV44GPEBegin, { |msg|
    ~qmwQFTV44GPERevision = msg[1].asInteger;
    ~qmwQFTV44GPEValid = true;
    ~qmwQFTV44GPEStageMagnitudes = Array.fill(8, 0.0);
    ~qmwQFTV44GPEStagePhases = Array.fill(8, 0.0);
    ~qmwQFTV44GPEVortexCount = 0;
}, ~qmwQFTV44GPERoot ++ "/frame/begin", recvPort: ~qmwQFTV44GPEPort);
OSCdef(\qmwQFTV44GPEDensity, { |msg| if(~qmwQFTV44GPEValid and: { msg[1].asInteger == ~qmwQFTV44GPERevision }) { ~qmwQFTV44GPEDensity = msg[2].asFloat } }, ~qmwQFTV44GPERoot ++ "/density/mean", recvPort: ~qmwQFTV44GPEPort);
OSCdef(\qmwQFTV44GPEPeak, { |msg| if(~qmwQFTV44GPEValid and: { msg[1].asInteger == ~qmwQFTV44GPERevision }) { ~qmwQFTV44GPEPeak = msg[2].asFloat } }, ~qmwQFTV44GPERoot ++ "/density/max", recvPort: ~qmwQFTV44GPEPort);
OSCdef(\qmwQFTV44GPEFlowX, { |msg| if(~qmwQFTV44GPEValid and: { msg[1].asInteger == ~qmwQFTV44GPERevision }) { ~qmwQFTV44GPEFlowX = msg[2].asFloat } }, ~qmwQFTV44GPERoot ++ "/flow/x", recvPort: ~qmwQFTV44GPEPort);
OSCdef(\qmwQFTV44GPEFlowSpeed, { |msg| if(~qmwQFTV44GPEValid and: { msg[1].asInteger == ~qmwQFTV44GPERevision }) { ~qmwQFTV44GPEFlowSpeed = msg[2].asFloat } }, ~qmwQFTV44GPERoot ++ "/flow/speed", recvPort: ~qmwQFTV44GPEPort);
OSCdef(\qmwQFTV44GPEVortices, { |msg| if(~qmwQFTV44GPEValid and: { msg[1].asInteger == ~qmwQFTV44GPERevision }) { ~qmwQFTV44GPEVortexCount = msg[2].asInteger } }, ~qmwQFTV44GPERoot ++ "/vortex/count", recvPort: ~qmwQFTV44GPEPort);
8.do { |index|
    OSCdef(("qmwQFTV44GPEMag" ++ index).asSymbol, { |msg| if(~qmwQFTV44GPEValid and: { msg[1].asInteger == ~qmwQFTV44GPERevision }) { ~qmwQFTV44GPEStageMagnitudes[index] = msg[2].asFloat } }, ~qmwQFTV44GPERoot ++ "/mode/" ++ index ++ "/magnitude", recvPort: ~qmwQFTV44GPEPort);
    OSCdef(("qmwQFTV44GPEPhase" ++ index).asSymbol, { |msg| if(~qmwQFTV44GPEValid and: { msg[1].asInteger == ~qmwQFTV44GPERevision }) { ~qmwQFTV44GPEStagePhases[index] = msg[2].asFloat } }, ~qmwQFTV44GPERoot ++ "/mode/" ++ index ++ "/phase", recvPort: ~qmwQFTV44GPEPort);
};
OSCdef(\qmwQFTV44GPEEnd, { |msg|
    if(~qmwQFTV44GPEValid and: { msg[1].asInteger == ~qmwQFTV44GPERevision }) {
        ~qmwQFTV44GPEMagnitudes = ~qmwQFTV44GPEStageMagnitudes.copy;
        ~qmwQFTV44GPEPhases = ~qmwQFTV44GPEStagePhases.copy;
        ~qmwQFTV44GPEValid = false;
        ~qmwQFTV44UpdateGPEPulseTimbre.value
    }
}, ~qmwQFTV44GPERoot ++ "/frame/end", recvPort: ~qmwQFTV44GPEPort);

~qmwQFTV44AttachGPEMaterial = {
    var parent = ~qmwQFTV43Window;
    if(parent.notNil, {
        StaticText(parent, Rect(20, 946, 720, 20)).string_("GPE PULSE MATERIAL — SAMPLED AT ONSET")
            .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.green(0.78));
        StaticText(parent, Rect(20, 972, 720, 38)).string_("Independent 2-D Gross-Pitaevskii phase-collision sidecar. It colors inherited pulse timbre; it creates no continuous GPE sound.").stringColor_(Color.grey(0.78));
        Button(parent, Rect(20, 1020, 180, 28)).states_([["GPE TIMBRE OFF", Color.grey(0.8), Color.grey(0.2)], ["GPE TIMBRE ON", Color.black, Color.green(0.7)]]).value_(~qmwQFTV44GPEEnabled).action_({ |button| ~qmwQFTV44GPEEnabled = button.value; ~qmwQFTV44UpdateGPEPulseTimbre.value });
        EZSlider(parent, Rect(220, 1018, 300, 30), "timbre depth", ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV44GPEPulseTimbreDepth), { |view| ~qmwQFTV44GPEPulseTimbreDepth = view.value; ~qmwQFTV44UpdateGPEPulseTimbre.value }, ~qmwQFTV44GPEPulseTimbreDepth, labelWidth: 92, numberWidth: 52);
        ~qmwQFTV44GPEStatus = StaticText(parent, Rect(20, 1060, 720, 42)).string_("WAITING FOR GPE OBSERVABLES ON UDP 17867").font_(Font("Menlo", 10)).stringColor_(Color.yellow(0.75));
        StaticText(parent, Rect(20, 1110, 720, 42)).string_("GPE timbre is sampled at each onset: flow → ring; density + occupation → folds; mode + vortices → harmonic. Existing tails remain fixed.").stringColor_(Color.grey(0.78));
        StaticText(parent, Rect(20, 1164, 720, 20)).string_("GPE COLLISION PREPARATION — RESETS FIELD TO t=0")
            .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.cyan(0.78));
        EZSlider(parent, Rect(20, 1190, 350, 30), "phase theta", ControlSpec(0, 2pi, \lin, 0.001, 0), { |view|
            ~qmwQFTV44GPEControl.sendMsg("/qmw/gpe/control/phase", view.value)
        }, 0, labelWidth: 92, numberWidth: 52);
        EZSlider(parent, Rect(390, 1190, 350, 30), "interaction g", ControlSpec(-1, 2, \lin, 0.001, 0.3), { |view|
            ~qmwQFTV44GPEControl.sendMsg("/qmw/gpe/control/interaction", view.value)
        }, 0.3, labelWidth: 92, numberWidth: 52);
        StaticText(parent, Rect(20, 1230, 720, 42)).string_("These are explicit controls for the independent GPE preparation, not feedback into the V4 scalar field. The Python phase viewer remains the authoritative full-field image.").stringColor_(Color.grey(0.72));
        StaticText(parent, Rect(20, 1290, 720, 20)).string_("FLOW PULSE MATERIAL — SAMPLED AT ONSET")
            .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.magenta(0.80));
        EZSlider(parent, Rect(20, 1316, 230, 30), "P-flow → ring", ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV44ProbabilityPulseMix), { |view|
            ~qmwQFTV44ProbabilityPulseMix = view.value;
            ~qmwQFTV44UpdateGPEPulseTimbre.value
        }, ~qmwQFTV44ProbabilityPulseMix, labelWidth: 108, numberWidth: 48);
        EZSlider(parent, Rect(270, 1316, 230, 30), "terrain → fold", ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV44TerrainPulseMix), { |view|
            ~qmwQFTV44TerrainPulseMix = view.value;
            ~qmwQFTV44UpdateGPEPulseTimbre.value
        }, ~qmwQFTV44TerrainPulseMix, labelWidth: 108, numberWidth: 48);
        EZSlider(parent, Rect(520, 1316, 220, 30), "coherence → edge", ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV44CoherencePulseEdge), { |view|
            ~qmwQFTV44CoherencePulseEdge = view.value;
            ~qmwQFTV44UpdateGPEPulseTimbre.value
        }, ~qmwQFTV44CoherencePulseEdge, labelWidth: 112, numberWidth: 42);
        StaticText(parent, Rect(20, 1356, 720, 42)).string_("P-flow adds ring color at each pulse's selected-scale/site-tuned frequency; terrain flow adds folds; coherence supplies a bounded pulse edge. Set any depth to 0 to mute that contribution. Existing tails remain fixed.").stringColor_(Color.grey(0.72));
        Button(parent, Rect(20, 1408, 220, 28)).states_([
            ["LEGACY FLOW BED OFF", Color.grey(0.75), Color.grey(0.2)],
            ["LEGACY FLOW BED ON", Color.black, Color.green(0.7)]
        ]).value_(~qmwQFTV43FlowEnabled).action_({ |button|
            ~qmwQFTV43FlowEnabled = button.value;
            ~qmwQFTV43UpdateFlowAudio.value
        });
        StaticText(parent, Rect(254, 1408, 486, 28)).string_("Optional V4.3 carrier; independent of the onset-only pulse mappings above.").stringColor_(Color.grey(0.68));
        StaticText(parent, Rect(20, 1462, 720, 20)).string_("LIVE OBSERVERS — READ-ONLY VIEWS OF STATE, PROCESS, AND FLOW")
            .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.cyan(0.78));
        Button(parent, Rect(20, 1490, 220, 30)).states_([["SHOW STATE + FLOW"]]).action_({
            ~qmwQFTV3Window !? _.front;
        });
        Button(parent, Rect(260, 1490, 220, 30)).states_([["OPEN FIELDFRAME VIEW"]]).action_({
            ~qmwQFTV44OpenFieldFrameGeometryPanel !? _.value;
        });
        Button(parent, Rect(500, 1490, 240, 30)).states_([["OPEN INTERACTION DIAGRAM"]]).action_({
            ~qmwInteractionV1OpenPanel !? _.value;
        });
        StaticText(parent, Rect(20, 1532, 720, 42)).string_("State + Flow presents the scalar-field view; FieldFrame presents one synchronized GPE observer frame; Interaction Diagram is a read-only coherent-process view. The interaction demo remains synthetic until a Hilbert Transport source is attached.").stringColor_(Color.grey(0.72));
    })
};

~qmwQFTV3Stop = {
    [\qmwQFTV44GPEBegin, \qmwQFTV44GPEDensity, \qmwQFTV44GPEPeak, \qmwQFTV44GPEFlowX, \qmwQFTV44GPEFlowSpeed, \qmwQFTV44GPEVortices, \qmwQFTV44GPEEnd].do { |key| OSCdef(key).free };
    8.do { |index| OSCdef(("qmwQFTV44GPEMag" ++ index).asSymbol).free; OSCdef(("qmwQFTV44GPEPhase" ++ index).asSymbol).free };
    baseStop.value
};
{ ~qmwQFTV44AttachGPEMaterial.value; "QMW QFT V4.4 GPE pulse-timbre material attached to additive membrane panel on UDP 17867".postln }.defer;
)
