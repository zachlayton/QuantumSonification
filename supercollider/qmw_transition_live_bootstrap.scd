/* Explicit opt-in composition; existing V3 and durable V4 files stay unchanged. */
(
var v3="QMW_V3_SC_FILE".getenv, v4="QMW_V4_SPECTRAL_BRIDGE_FILE".getenv;
var adapter="QMW_NOTE_TIMBRE_SC_FILE".getenv, attempts=0;
[v3,v4,adapter].do { |path| if(path.isNil or: { File.exists(path).not }, {
    Error("Note/timbre bootstrap requires explicit existing V3/V4/adapter paths").throw
}) };
thisProcess.interpreter.executeFile(v3);
s.waitForBoot({
    AppClock.sched(0.1,{
        attempts=attempts+1;
        if(~qriFXSendBus.notNil and: { ~qriVoiceGainBus.notNil }, {
            thisProcess.interpreter.executeFile(v4);
            // V4 installs its legacy bridge in a Routine. Wait for it to finish
            // before appending our final stereo router, without rewriting it.
            AppClock.sched(0.5,{thisProcess.interpreter.executeFile(adapter);nil});
            nil
        }, {
            if(attempts>150,{"NOTE/TIMBRE bootstrap timed out waiting for V3 mixer.".warn;nil},{0.1})
        })
    })
});
)
