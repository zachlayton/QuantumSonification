/* Opt-in actual-session acceptance wrapper; production bootstrap stays intact. */
(
var adapter="QMW_NOTE_TIMBRE_SC_FILE".getenv;
var harness=thisProcess.nowExecutingPath.dirname +/+ "routed_live_acceptance.scd";
var output="QMW_ROUTED_ACCEPTANCE_DIR".getenv, attempts=0;
if(adapter.isNil or: { output.isNil }, { Error("Acceptance requires explicit adapter and output directory").throw });
File.mkdir(output);
File.use(output +/+ "status.txt","w", { |f| f.write("BOOTSTRAP: waiting for actual native source and routed receiver\n") });
thisProcess.interpreter.executeFile(adapter.dirname +/+ "qmw_note_timbre_live_bootstrap.scd");
AppClock.sched(0.2, {
    attempts=attempts+1;
    if((~qntInstalled ? false) and: { ~qntLastAcceptedPacket.notNil }, {
        thisProcess.interpreter.executeFile(harness);nil
    }, {
        if(attempts>=300, {
            File.use(output +/+ "status.txt","w", { |f| f.write("FAILED: no actual accepted native source within60seconds\n") });
            "QNT_ACCEPTANCE_FAILED bootstrap timeout".warn;nil
        }, { 0.2 })
    })
});
)
