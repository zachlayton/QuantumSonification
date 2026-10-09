(
// QMW live PhysicsFrame granular receiver v1
//
// Python/QMW sends:
// /qmw/grain
//   revision, simulationTime, position, durationMs,
//   rate, amplitude, pan, densityHz
//
// Default receive port: 7405

s.waitForBoot {
    ~qmwGranularSource = Platform.resourceDir +/+ "sounds/a11wlk01.wav";
    ~qmwGranularBuffer = Buffer.read(s, ~qmwGranularSource);

    SynthDef(\qmwPhysicsFrameGrain, {
        |out=0, buf=0, pos=0.5, durMs=80, rate=1,
         amp=0.2, pan=0, density=8|
        var trigger = Dust.ar(density.max(0.1));
        var duration = (durMs * 0.001).clip(0.005, 1.0);
        var signal = GrainBuf.ar(
            numChannels: 2,
            trigger: trigger,
            dur: duration,
            sndbuf: buf,
            rate: rate,
            pos: pos.clip(0, 1),
            interp: 4,
            pan: pan.clip(-1, 1)
        );
        Out.ar(out, signal * amp.clip(0, 1));
    }).add;

    s.sync;

    ~qmwPhysicsFrameGrain = Synth(\qmwPhysicsFrameGrain, [
        \buf, ~qmwGranularBuffer,
        \pos, 0.5,
        \durMs, 80,
        \rate, 1,
        \amp, 0.2,
        \pan, 0,
        \density, 8
    ]);

    OSCdef(\qmwPhysicsFrameGranular, { |msg|
        ~qmwPhysicsFrameGrain.set(
            \pos, msg[3],
            \durMs, msg[4],
            \rate, msg[5],
            \amp, msg[6],
            \pan, msg[7],
            \density, msg[8]
        );
    }, '/qmw/grain', recvPort: 7405);

    "QMW PhysicsFrame granular receiver ready on UDP 7405".postln;
};
)

// To use a different sound file:
// ~qmwGranularSource = "/absolute/path/to/audio.wav";
// ~qmwGranularBuffer.free;
// ~qmwGranularBuffer = Buffer.read(s, ~qmwGranularSource);
// ~qmwPhysicsFrameGrain.set(\buf, ~qmwGranularBuffer);
