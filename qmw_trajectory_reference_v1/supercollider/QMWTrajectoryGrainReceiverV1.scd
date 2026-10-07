/*
QMW trajectory-grain receiver v1

Receives the explicit musical projection from
qmw_trajectory_reference_v1.stream_xy_grains on UDP 17905.

This is downstream-only.  It receives position, duration, rate, amplitude,
pan, and density controls; it does not evolve a density matrix or send
controls upstream.

Before evaluation, set ~qmwTrajectorySource to a local sound file.  This file
does not boot a server, start a publisher, or create sound by itself.
*/

(
~qmwTrajectoryOSCPort = 17905;
~qmwTrajectoryRoot = '/qmw/trajectory_grain/v1';
thisProcess.openUDPPort(~qmwTrajectoryOSCPort);

SynthDef(\qmwTrajectoryGrainV1, { |out=0, bufnum=0, position=0.5, duration=0.08,
    rate=1.0, amplitude=0.12, pan=0.0, density=8.0, gate=1|
    var trigger = Impulse.ar(density.clip(0.2, 48.0));
    var signal = GrainBuf.ar(
        2, trigger, duration.clip(0.008, 0.5), bufnum, rate.clip(0.25, 4.0),
        position.clip(0.0, 1.0), 2, pan.clip(-1.0, 1.0), -1, 256,
        amplitude.clip(0.0, 0.8)
    );
    Out.ar(out, signal * LagUD.kr(gate, 0.02, 0.15));
}).add;

~qmwTrajectoryStart = { |sourcePath, out=0|
    if(sourcePath.isNil) {
        Error("QMW trajectory grain receiver needs a local source sound-file path.").throw;
    };
    if(s.serverRunning.not) { s.boot; };
    s.waitForBoot({
        ~qmwTrajectoryBuffer.tryPerform(\free);
        ~qmwTrajectoryVoice.tryPerform(\free);
        ~qmwTrajectoryBuffer = Buffer.read(s, sourcePath, action: { |buffer|
            ~qmwTrajectoryVoice = Synth(\qmwTrajectoryGrainV1, [
                \out, out, \bufnum, buffer.bufnum, \gate, 0
            ]);
            "QMW TRAJECTORY GRAIN RECEIVER READY".postln;
        });
    });
};

~qmwTrajectoryStop = {
    ~qmwTrajectoryVoice.tryPerform(\set, \gate, 0);
    ~qmwTrajectoryVoice = nil;
};

~qmwTrajectoryRevision = -1;
OSCdef(\qmwTrajectoryGrainBegin, { |message|
    var revision = message[1].asInteger;
    if(revision >= ~qmwTrajectoryRevision) {
        ~qmwTrajectoryRevision = revision;
        ~qmwTrajectoryVoice.tryPerform(\set, \gate, 1);
        ("QMW TRAJECTORY BEGIN rev=" ++ revision ++ " retained=" ++ message[4]).postln;
    };
}, ~qmwTrajectoryRoot ++ '/begin', recvPort: ~qmwTrajectoryOSCPort);

OSCdef(\qmwTrajectoryGrainControls, { |message|
    var revision = message[1].asInteger;
    if((revision == ~qmwTrajectoryRevision) and: { ~qmwTrajectoryVoice.notNil }) {
        ~qmwTrajectoryVoice.set(
            \position, message[4].asFloat,
            \duration, message[5].asFloat * 0.001,
            \rate, message[6].asFloat,
            \amplitude, message[7].asFloat,
            \pan, message[8].asFloat,
            \density, message[9].asFloat
        );
    };
}, ~qmwTrajectoryRoot ++ '/grain', recvPort: ~qmwTrajectoryOSCPort);

OSCdef(\qmwTrajectoryGrainEnd, { |message|
    if(message[1].asInteger == ~qmwTrajectoryRevision) {
        ~qmwTrajectoryVoice.tryPerform(\set, \gate, 0);
        ("QMW TRAJECTORY END rev=" ++ message[1]).postln;
    };
}, ~qmwTrajectoryRoot ++ '/end', recvPort: ~qmwTrajectoryOSCPort);
)

// Example: set this explicitly, then start the receiver.
// ~qmwTrajectoryStart.value("/absolute/path/to/a/source.wav");
