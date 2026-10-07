/* QMW V4.4: V4.3 preserved beneath an independent GPE material layer. */
(
// Set before V4.3 builds its panel so that its additive UI can present the
// V4.4 pulse-first layout without changing the V4.3 runtime path.
~qmwQFTV44Enabled = true;
// Start from the inherited safe controls. A recalled performance preset can
// re-enable sound and restore aggressive nonlinear settings, defeating the
// pulse-first silent baseline before the performer has made a choice.
~qmwQFTV3StartupPresetSlot = nil;
~qmwQFTV3StartupMuted = true;
thisProcess.interpreter.executeFile(thisProcess.nowExecutingPath.dirname +/+ "qmw_scalar_field_observer_v4_3.scd");
~qmwQFTDisplayVersion = "4.4";
// V4.4 is pulse-first: mute V4.3's inherited continuous-flow bed by default.
// Its panel may still enable that preserved layer explicitly if desired.
~qmwQFTV43FlowEnabled = 0;
~qmwQFTV43UpdateFlowAudio !? _.value;
// V4.4's four pulse faders should start with no inherited continuous
// resonator bed beneath them. The V3 vacuum reference remains available as
// an explicit adapter control, but is off in this pulse-first boundary.
~qmwQFTV3VacuumMix = 0;
~qmwQFTV3Synth !? { |synth| synth.set(\vacuumMix, 0) };
// V4.3's original function writes a Qt view directly when it is invoked by
// an OSC handler. V4.4 keeps the tuning math but schedules that view update
// on AppClock, as Qt requires. V4.3 tuning source remains unchanged.
~qmwQFTV43ApplyTuning = {
    var rootRatio, siteCount = (~qmwQFTSiteCount ? 16).asInteger;
    if(~qmwQFTV43Family == 0, {
        ~qmwQFTV43Description = "%-EDO".format(~qmwQFTV43EDO);
        ~qmwQFTV43Degrees = Array.fill(~qmwQFTV43EDO, { |degree|
            2.pow(degree / ~qmwQFTV43EDO)
        });
        ~qmwQFTV43Period = 2.0
    });
    rootRatio = ~qmwQFTV43ScaleRatioAt.(~qmwQFTV43DegreeOffset).max(1e-12);
    ~qmwQFTV3PitchMode = 3;
    ~qmwQFTV3SitePitchRatios = Array.fill(siteCount, { |site|
        ~qmwQFTV43ScaleRatioAt.(site + ~qmwQFTV43DegreeOffset) / rootRatio
    });
    if(~qmwQFTV3AudioReady) {
        ~qmwQFTV3Synth !? { |synth| synth.setn(\sitePitchRatios, ~qmwQFTV3SitePitchRatios) };
        ~qmwQFTV43FlowSynth !? { |synth| synth.setn(\flowPitchRatios, ~qmwQFTV3SitePitchRatios.copyRange(0, 7)) }
    };
    { ~qmwQFTV43TuningStatus !? { |view|
        view.string_("SCALE ACTIVE / % / offset %".format(~qmwQFTV43Description, ~qmwQFTV43DegreeOffset))
    } }.defer;
};
thisProcess.interpreter.executeFile(thisProcess.nowExecutingPath.dirname +/+ "qmw_gpe_material_v4_4_addon.scd");
thisProcess.interpreter.executeFile(thisProcess.nowExecutingPath.dirname +/+ "qmw_gpe_field_frame_geometry_v4_4_addon.scd");
)
