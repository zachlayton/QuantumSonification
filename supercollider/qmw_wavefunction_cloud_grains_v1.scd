/*
QMW 3D wavefunction cloud grain renderer v1

Each /qmw/wavefunction/cloud/grain packet creates one self-freeing synth.
The default decay is exactly 5 ms. There is no persistent chord in this file.

Start the OSC streamer with:
    python examples/wavefunction_cloud_osc_v1.py --decay-ms 5
*/

(
s.waitForBoot {
    SynthDef(\qmwWavefunctionCloudGrainV1, {
        |out = 0, x = 0, y = 0, z = 0, amplitude = 0.2, phase = 0,
        currentX = 0, currentY = 0, currentZ = 0,
        energy = 0.5, decayMs = 5|

        var decaySeconds = decayMs.max(0.1) * 0.001;
        var envelope = EnvGen.ar(
            Env([0, 1, 0], [0.00025, decaySeconds], [4, -8]),
            doneAction: Done.freeSelf
        );
        var frequency = energy.clip(0, 1).linexp(0, 1, 70, 7200);
        var currentMagnitude = (currentX.squared + currentY.squared + currentZ.squared).sqrt.clip(0, 1);
        var directedFrequency = frequency * (1 + (0.025 * currentZ));
        var tonal = SinOsc.ar(directedFrequency, phase.clip(-1, 1) * pi);
        var particulate = BPF.ar(
            WhiteNoise.ar(0.18 * currentMagnitude),
            directedFrequency.clip(40, SampleRate.ir * 0.42),
            currentMagnitude.linlin(0, 1, 0.015, 0.32)
        );
        var signal = (tonal + particulate) * envelope * amplitude.clip(0, 1);
        var pan = (x + (0.35 * currentX)).clip(-1, 1);

        signal = LeakDC.ar(signal);
        signal = Limiter.ar(signal, 0.72, 0.001);
        Out.ar(out, Pan2.ar(signal, pan));
    }).add;

    s.sync;
    ~qmwWavefunctionGrainCount = 0;

    OSCdef(\qmwWavefunctionCloudGrain, { |message|
        if(message.size >= 13) {
            Synth(\qmwWavefunctionCloudGrainV1, [
                \x, message[3].asFloat,
                \y, message[4].asFloat,
                \z, message[5].asFloat,
                \amplitude, message[6].asFloat,
                \phase, message[7].asFloat,
                \currentX, message[8].asFloat,
                \currentY, message[9].asFloat,
                \currentZ, message[10].asFloat,
                \energy, message[11].asFloat,
                \decayMs, message[12].asFloat
            ]);
            ~qmwWavefunctionGrainCount = ~qmwWavefunctionGrainCount + 1;
        };
    }, '/qmw/wavefunction/cloud/grain');

    OSCdef(\qmwWavefunctionCloudFrame, { |message|
        if((message[1].asInteger % 30) == 0) {
            "Wavefunction cloud frame % | norm % | grains rendered %"
                .format(message[1], message[4].round(0.000001), ~qmwWavefunctionGrainCount)
                .postln;
        };
    }, '/qmw/wavefunction/cloud/frame');

    ~qmwWavefunctionCloudStop = {
        OSCdef(\qmwWavefunctionCloudGrain).free;
        OSCdef(\qmwWavefunctionCloudFrame).free;
        "QMW wavefunction cloud grain renderer stopped.".postln;
    };

    "QMW wavefunction cloud grains listening on port 57120; decay default = 5 ms.".postln;
};
)
