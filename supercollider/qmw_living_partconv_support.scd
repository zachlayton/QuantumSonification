// QMW living spectral IR loader and transactional PartConv crossfader.
// Evaluated by qmw_density_spectral_resonator.scd after its buses/groups exist.

~qmwIRFreeMaterial = { |material|
    if(material.notNil) {
        if(material[\synth].notNil) { material[\synth].free };
        if(material[\spectrumLeft].notNil) {
            material[\spectrumLeft].free
        };
        if(material[\spectrumRight].notNil) {
            material[\spectrumRight].free
        };
    };
};

~qmwIRSendFailure = { |revision, reason|
    "QMW IR revision % failed: %".format(revision, reason).warn;
    ~qmwIRAckAddress.sendMsg(
        '/living/ir/failed', revision.asInteger, reason.asString
    );
};

~qmwIRAbortPending = { |revision, reason|
    ~qmwIRSendFailure.(revision, reason);
    if(
        ~qmwIRPending.notNil
        and: { ~qmwIRPending[\revision] == revision.asInteger }
    ) {
        ~qmwIRFreeMaterial.(~qmwIRPending);
        ~qmwIRPending = nil;
    };
};

~qmwIRLoadCandidate = { |revision, path, crossfadeMs = 250|
    var soundFile = SoundFile.new;
    var channelCount;
    var rightChannel;

    revision = revision.asInteger;
    path = path.asString;
    if(~qmwIRPending.notNil) {
        ~qmwIRSendFailure.(
            revision, "another IR revision is already loading"
        );
    } {
        if(soundFile.openRead(path).not) {
            ~qmwIRSendFailure.(revision, "cannot open IR: " ++ path);
        } {
            channelCount = soundFile.numChannels.max(1);
            rightChannel = if(channelCount > 1) { 1 } { 0 };
            soundFile.close;
            ~qmwIRPending = (
                revision: revision,
                path: path,
                crossfadeMs: crossfadeMs.asFloat.max(0),
                status: \loading,
                spectrumLeft: nil,
                spectrumRight: nil,
                synth: nil
            );

            Routine({
                var timeLeft;
                var timeRight;
                var spectrumLeft;
                var spectrumRight;
                var leftSize;
                var rightSize;

                try {
                    timeLeft = Buffer.readChannel(
                        s, path, channels: [0]
                    );
                    timeRight = Buffer.readChannel(
                        s, path, channels: [rightChannel]
                    );
                    s.sync;
                    leftSize = PartConv.calcBufSize(
                        ~qmwIRFFTSize, timeLeft
                    );
                    rightSize = PartConv.calcBufSize(
                        ~qmwIRFFTSize, timeRight
                    );
                    spectrumLeft = Buffer.alloc(s, leftSize, 1);
                    spectrumRight = Buffer.alloc(s, rightSize, 1);
                    s.sync;
                    spectrumLeft.preparePartConv(
                        timeLeft, ~qmwIRFFTSize
                    );
                    spectrumRight.preparePartConv(
                        timeRight, ~qmwIRFFTSize
                    );
                    s.sync;
                    timeLeft.free;
                    timeRight.free;

                    if(
                        ~qmwIRPending.notNil
                        and: { ~qmwIRPending[\revision] == revision }
                    ) {
                        ~qmwIRPending[\spectrumLeft] = spectrumLeft;
                        ~qmwIRPending[\spectrumRight] = spectrumRight;
                        ~qmwIRPending[\status] = \ready;
                        ~qmwIRAckAddress.sendMsg(
                            '/living/ir/ready', revision
                        );
                        "QMW IR revision % ready: %"
                            .format(revision, path).postln;
                    } {
                        spectrumLeft.free;
                        spectrumRight.free;
                    };
                } { |error|
                    if(timeLeft.notNil) { timeLeft.free };
                    if(timeRight.notNil) { timeRight.free };
                    if(spectrumLeft.notNil) { spectrumLeft.free };
                    if(spectrumRight.notNil) { spectrumRight.free };
                    ~qmwIRAbortPending.(revision, error.asString);
                };
            }).play(SystemClock);
        };
    };
};

~qmwIRStartCrossfade = { |revision, crossfadeMs = 250|
    var pending = ~qmwIRPending;
    var previous = ~qmwIRActive;
    var seconds = crossfadeMs.asFloat.max(1) * 0.001;
    var newSynth;

    if(
        pending.isNil
        or: { pending[\revision] != revision.asInteger }
        or: { pending[\status] != \ready }
    ) {
        ~qmwIRSendFailure.(
            revision, "crossfade requested before IR was ready"
        );
    } {
        newSynth = Synth.tail(
            ~qmwSCFXGroup,
            \qmwLivingPartConvStereo,
            [
                \inBus, ~qmwSCSourceBus,
                \out, 0,
                \irLeft, pending[\spectrumLeft],
                \irRight, pending[\spectrumRight],
                \wet, 0,
                \wetLevel, ~qmwIRWetLevel,
                \fadeTime, seconds
            ]
        );
        pending[\synth] = newSynth;
        pending[\status] = \crossfading;
        newSynth.set(\wet, 1, \fadeTime, seconds);
        if(previous.notNil and: { previous[\synth].notNil }) {
            previous[\synth].set(\wet, 0, \fadeTime, seconds);
        };

        SystemClock.sched(seconds + 0.05, {
            if(previous.notNil) { ~qmwIRFreeMaterial.(previous) };
            pending[\status] = \active;
            ~qmwIRActive = pending;
            ~qmwIRPending = nil;
            ~qmwIRAckAddress.sendMsg(
                '/living/ir/committed', revision.asInteger
            );
            "QMW IR revision % committed.".format(revision).postln;
            nil
        });
    };
};

OSCdef(\qmwIRCandidate, { |message|
    ~qmwIRLoadCandidate.(message[1], message[2], message[3]);
}, '/living/ir/candidate');

OSCdef(\qmwIRCrossfadeStart, { |message|
    ~qmwIRStartCrossfade.(message[1], message[2]);
}, '/living/ir/crossfade/start');

// Manual loading uses the same safe staging path and initiates its own
// crossfade after preparation when no OSC publisher is running.
~qmwSCLoadIR = { |path, crossfadeMs = 500|
    var revision;
    ~qmwIRManualRevision = ~qmwIRManualRevision + 1;
    revision = ~qmwIRManualRevision;
    ~qmwIRLoadCandidate.(revision, path, crossfadeMs);
    Routine({
        while {
            ~qmwIRPending.notNil
            and: { ~qmwIRPending[\revision] == revision }
            and: { ~qmwIRPending[\status] == \loading }
        } {
            0.05.wait;
        };
        if(
            ~qmwIRPending.notNil
            and: { ~qmwIRPending[\revision] == revision }
            and: { ~qmwIRPending[\status] == \ready }
        ) {
            ~qmwIRStartCrossfade.(revision, crossfadeMs);
        };
    }).play(SystemClock);
    revision
};

~qmwSCConvolutionMix = { |dry = 0.72, wet = 0.3, fadeMs = 100|
    var seconds = fadeMs.asFloat.max(1) * 0.001;
    ~qmwIRWetLevel = wet.asFloat.clip(0, 1);
    ~qmwSCDrySynth.set(
        \dry, dry.asFloat.clip(0, 1), \fadeTime, seconds
    );
    if(~qmwIRActive.notNil and: { ~qmwIRActive[\synth].notNil }) {
        ~qmwIRActive[\synth].set(
            \wetLevel, ~qmwIRWetLevel, \fadeTime, seconds
        );
    };
};

~qmwIRStop = {
    OSCdef(\qmwIRCandidate).free;
    OSCdef(\qmwIRCrossfadeStart).free;
    ~qmwIRFreeMaterial.(~qmwIRPending);
    ~qmwIRFreeMaterial.(~qmwIRActive);
    ~qmwIRPending = nil;
    ~qmwIRActive = nil;
};

"QMW living PartConv engine ready (ack port 7461).".postln;
