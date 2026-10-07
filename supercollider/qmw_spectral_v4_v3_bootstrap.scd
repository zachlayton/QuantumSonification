/*
QMW V4 spectral bridge bootstrap
================================

This file composes a complete V3 session from QMW_V3_SC_FILE with the V4
bridge from QMW_V4_SPECTRAL_BRIDGE_FILE.  It belongs to the launcher rather
than the quantum core: the bridge remains a read-only musical observer.
*/

(
// Environment lookup is a String method in SuperCollider 3.13, not a
// Platform method.  Keeping this form makes the launcher work on macOS SC.
var v3File = "QMW_V3_SC_FILE".getenv;
var bridgeFile = "QMW_V4_SPECTRAL_BRIDGE_FILE".getenv;
var attempts = 0;

if(v3File.isNil or: { File.exists(v3File).not }, {
    Error("QMW V4 bootstrap requires QMW_V3_SC_FILE to name a V3 .scd file.")
        .throw;
});
if(bridgeFile.isNil or: { File.exists(bridgeFile).not }, {
    Error("QMW V4 bootstrap requires QMW_V4_SPECTRAL_BRIDGE_FILE.").throw;
});

thisProcess.interpreter.executeFile(v3File);

// V3 allocates ~qriFXSendBus during its server-ready callback.  Polling this
// one public runtime seam avoids assuming an incidental V3 callback order.
s.waitForBoot({
    AppClock.sched(0.1, {
        attempts = attempts + 1;
        if(~qriFXSendBus.notNil, {
            thisProcess.interpreter.executeFile(bridgeFile);
            "QMW V4 spectral bridge attached to the V3 FX bus.".postln;
            nil;
        }, {
            if(attempts >= 100, {
                "QMW V4 spectral bridge timed out waiting for ~qriFXSendBus."
                    .warn;
                nil;
            }, {
                0.1;
            });
        });
    });
});
)
