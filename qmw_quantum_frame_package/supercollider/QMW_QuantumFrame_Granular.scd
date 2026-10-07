(
// QMW 2048 QuantumFrame -> granular receiver
// Python OSC default: 127.0.0.1:7405
// Set ~qmwSoundFile to any audio file you want to granulate.

s.waitForBoot {
    ~qmwSoundFile = Platform.resourceDir +/+ "sounds/a11wlk01.wav";
    ~qmwBuf = Buffer.read(s, ~qmwSoundFile);

    SynthDef(\qmwQuantumGrain, {
        |out=0, buf=0, pos=0.5, durMs=80, rate=1, amp=0.2, pan=0, density=10|
        var trig = Dust.ar(density.max(0.1));
        var dur = (durMs * 0.001).clip(0.005, 1.0);
        var sig = GrainBuf.ar(
            numChannels: 2,
            trigger: trig,
            dur: dur,
            sndbuf: buf,
            rate: rate,
            pos: pos.clip(0, 1),
            interp: 4,
            pan: pan.clip(-1, 1)
        );
        Out.ar(out, sig * amp.clip(0, 1));
    }).add;

    s.sync;

    ~qmwGrain = Synth(\qmwQuantumGrain, [
        \buf, ~qmwBuf,
        \pos, 0.5,
        \durMs, 80,
        \rate, 1,
        \amp, 0.2,
        \pan, 0,
        \density, 10
    ]);

    // /qmw/grain:
    // index, simTime, position, durationMs, rate, amplitude, pan, densityHz
    OSCdef(\qmwGrainControl, { |msg|
        ~qmwGrain.set(
            \pos, msg[3],
            \durMs, msg[4],
            \rate, msg[5],
            \amp, msg[6],
            \pan, msg[7],
            \density, msg[8]
        );
    }, '/qmw/grain', recvPort: 7405);

    // Optional raw telemetry:
    // index, simTime, p0 p1 p2 p3, j01 j12 j23
    OSCdef(\qmwFrameTelemetry, { |msg|
        // Uncomment for inspection:
        // msg.postln;
    }, '/qmw/frame', recvPort: 7405);

    OSCdef(\qmwEnd, { |msg|
        ("QMW frame complete: " ++ msg[1] ++ " samples").postln;
    }, '/qmw/end', recvPort: 7405);

    "QMW granular receiver ready on UDP 7405".postln;
};
)
