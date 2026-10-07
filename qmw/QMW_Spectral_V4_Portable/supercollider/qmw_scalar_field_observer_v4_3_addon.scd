/* V4.3 additive geometric-tuning and inherited-voice companion. */
(
var repoRoot = thisProcess.nowExecutingPath.dirname.dirname;
var siteCount = (~qmwQFTSiteCount ? 16).asInteger;
var bundledScalaDirectory = repoRoot +/+ "tunings/scala_archive/scl";
var scalaDirectory = (~qmwQFTV43ScalaDirectory ? (
    if(PathName(bundledScalaDirectory).isFolder, {
        bundledScalaDirectory
    }, {
        repoRoot +/+ "Quantum_Resonant_Membrane_v1/tunings/scala_archive/scl"
    })
)).asString;
var baseStop = ~qmwQFTV3Stop;
var baseBuildAudio = ~qmwQFTV3BuildAudio;

~qmwQFTV43FamilyNames = [
    "n-EDO", "Wilson", "Tenney", "La Monte Young", "Scala dictionary"
];
// These are pitch-source adapters, not changes to the scalar-field evolution.
// "field normal modes" uses the periodic Klein-Gordon lattice frequencies;
// the two harmonic choices are deliberately idealized series.  A geometry
// source is accepted only when an actual geometry eigenspectrum is supplied.
~qmwQFTV43PitchSourceNames = [
    "equal division (n-EDO)", "Scala dictionary", "field normal modes",
    "harmonics 1-16", "odd harmonics 1-31", "geometry spectrum"
];
~qmwQFTV43PitchSource = 0;
~qmwQFTV43GeometryPitchRatios = nil;
~qmwQFTV43GeometryDescription = "no geometry eigenspectrum received";
~qmwQFTV43Family = 0;
~qmwQFTV43EDO = 19;
~qmwQFTV43DegreeOffset = 0;
~qmwQFTV43Filter = "";
~qmwQFTV43ScalePaths = if(PathName(scalaDirectory).isFolder, {
    PathName(scalaDirectory).files.select { |path|
        path.extension.asString.toLower == "scl"
    }.collect(_.fullPath).sort
}, { [] });
// A performance panel must not construct a thousands-item popup. Scala is
// instead indexed under 1-9/A-Z, with a bounded page for each subtable.
~qmwQFTV43ScalaBrowseLimit = 128;
~qmwQFTV43ArchiveBrowseMode = 0;
~qmwQFTV43ScalaIndexNames = ["1-9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
~qmwQFTV43ScalaIndex = "A";
~qmwQFTV43ScalaIndexPage = 0;
~qmwQFTV43ScalaIndexPageCount = 1;
~qmwQFTV43SelectedScalePath = "";
~qmwQFTV43Degrees = [1.0];
~qmwQFTV43Period = 2.0;
~qmwQFTV43Description = "19-EDO";
~qmwQFTV43MembraneRoot = "/qmw/qft/v4_3/membrane";
~qmwQFTV43MembraneRevision = -1;
~qmwQFTV43MembraneStageValid = false;
~qmwQFTV43MembraneAvailable = false;
~qmwQFTV43RhoReal = Array.fill(16, 0.0);
~qmwQFTV43RhoImag = Array.fill(16, 0.0);
~qmwQFTV43StageRhoReal = ~qmwQFTV43RhoReal.copy;
~qmwQFTV43StageRhoImag = ~qmwQFTV43RhoImag.copy;
~qmwQFTV43OmegaMax = 0.0;
~qmwQFTV43SpectralLimit = 0.0;
~qmwQFTV43EffectiveCap = 0.0;
~qmwQFTV43Substeps = 0;
~qmwQFTV43ActualSubstep = 0.0;
~qmwQFTV43ProbabilityRoot = "/qmw/qft/v4_2/probability_flow";
~qmwQFTV43ProbabilityRevision = -1;
~qmwQFTV43ProbabilityStageValid = false;
~qmwQFTV43ProbabilityMaxFlux = 0.0;
~qmwQFTV43ProbabilitySignedFlux = 0.0;
~qmwQFTV43ProbabilityTotalFlux = 0.0;
~qmwQFTV43ProbabilityFlowEnergy = 0.0;
~qmwQFTV43ProbabilityCoherenceFlow = 0.0;
~qmwQFTV43TerrainMaxFlux = 0.0;
~qmwQFTV43TerrainSignedFlux = 0.0;
~qmwQFTV43TerrainTotalFlux = 0.0;
~qmwQFTV43TerrainFlowEnergy = 0.0;
~qmwQFTV43TerrainCoherenceFlow = 0.0;
~qmwQFTV43ProbabilityMix = 0.32;
~qmwQFTV43TerrainMix = 0.32;
~qmwQFTV43FlowSensitivity = 180.0;
~qmwQFTV43SineSquareDepth = 1.0;
~qmwQFTV43FlowEnabled = 1;
~qmwQFTV42TerrainSonify = 1;
~qmwQFTV43FlowSynth = nil;

~qmwQFTV43UpdateFlowAudio = {
    var sensitivityScale = ~qmwQFTV43FlowSensitivity / 180.0;
    // The continuous-space probability current and rho-terrain current have
    // different physical units/scales. Preserve that distinction rather than
    // normalizing the providers into one falsely shared observable.
    var probabilityAmount = (~qmwQFTV43ProbabilityMaxFlux
        * sensitivityScale * 1.5).tanh.clip(0, 1);
    var terrainAmount = (~qmwQFTV43TerrainMaxFlux
        * ~qmwQFTV43FlowSensitivity).tanh.clip(0, 1);
    var probabilityDirection = if(~qmwQFTV43ProbabilityTotalFlux > 1e-12, {
        (~qmwQFTV43ProbabilitySignedFlux
            / ~qmwQFTV43ProbabilityTotalFlux).clip(-1, 1)
    }, { 0 });
    var terrainDirection = if(~qmwQFTV43TerrainTotalFlux > 1e-12, {
        (~qmwQFTV43TerrainSignedFlux
            / ~qmwQFTV43TerrainTotalFlux).clip(-1, 1)
    }, { 0 });
    var coherence = ((~qmwQFTV43ProbabilityCoherenceFlow
        * sensitivityScale * 0.75)
        + (~qmwQFTV43TerrainCoherenceFlow
            * ~qmwQFTV43FlowSensitivity * 0.25)).tanh.clip(0, 1);
    ~qmwQFTV43FlowSynth !? { |synth|
        synth.set(
            \probabilityMix, ~qmwQFTV43ProbabilityMix,
            \terrainMix, ~qmwQFTV43TerrainMix,
            \probabilityAmount, probabilityAmount,
            \terrainAmount, terrainAmount,
            \probabilityDirection, probabilityDirection,
            \terrainDirection, terrainDirection,
            \sineSquare, coherence * ~qmwQFTV43SineSquareDepth,
            \soundEnabled, ~qmwQFTV43FlowEnabled,
            \fundamental, ~qmwQFTV3Fundamental
        )
    };
    {
        ~qmwQFTV43FlowStatus !? { |view|
            view.string_(
                "LIVE  P flux % -> % Hz / terrain % -> % Hz / direction P:% T:% / shape %"
                .format(
                    ~qmwQFTV43ProbabilityMaxFlux.round(0.00001),
                    probabilityAmount.linexp(0, 1, 140, 9000).round(1),
                    ~qmwQFTV43TerrainMaxFlux.round(0.00001),
                    terrainAmount.linexp(0, 1, 110, 6500).round(1),
                    probabilityDirection.round(0.01),
                    terrainDirection.round(0.01),
                    coherence.round(0.01)
                )
            ).stringColor_(if((probabilityAmount + terrainAmount) > 0.001, {
                Color.green(0.78)
            }, { Color.yellow(0.76) }))
        }
    }.defer
};

~qmwQFTV43BuildFlowAudio = {
    SynthDef(\qmwQFTV43ContinuousFlow, {
        |out=0, fundamental=72, probabilityMix=0.32, terrainMix=0.32,
        probabilityAmount=0, terrainAmount=0,
        probabilityDirection=0, terrainDirection=0,
        sineSquare=0, soundEnabled=1, gate=1|
        var ratios = NamedControl.kr(
            \flowPitchRatios, Array.series(8, 1, 1), 0.15
        ).clip(0.25, 16);
        var frequencies = (fundamental * ratios).clip(20, 12000);
        var pAmount = VarLag.kr(probabilityAmount.clip(0, 1), 0.18);
        var tAmount = VarLag.kr(terrainAmount.clip(0, 1), 0.18);
        var shape = VarLag.kr(sineSquare.clip(0, 1), 0.22);
        var sineField = SinOsc.ar(frequencies, Array.series(8, 0, pi / 5));
        var squareField = Pulse.ar(frequencies, 0.5, 0.72);
        var oscillatorField = (sineField * (1 - shape)) + (squareField * shape);
        var pCutoff = pAmount.linexp(0, 1, 140, 9000);
        var tCutoff = tAmount.linexp(0, 1, 110, 6500);
        var probability = RLPF.ar(
            oscillatorField,
            pCutoff.clip(40, SampleRate.ir * 0.42),
            pAmount.linlin(0, 1, 0.72, 0.16)
        );
        var terrain = RLPF.ar(
            oscillatorField.reverse,
            tCutoff.clip(40, SampleRate.ir * 0.42),
            tAmount.linlin(0, 1, 0.82, 0.22)
        );
        var pStereo = Balance2.ar(
            Mix(probability[[0, 2, 4, 6]]) * 0.25,
            Mix(probability[[1, 3, 5, 7]]) * 0.25,
            VarLag.kr(probabilityDirection.clip(-1, 1), 0.2)
        );
        var tStereo = Balance2.ar(
            Mix(terrain[[0, 2, 4, 6]]) * 0.25,
            Mix(terrain[[1, 3, 5, 7]]) * 0.25,
            VarLag.kr(terrainDirection.clip(-1, 1), 0.2)
        );
        // This is a persistent flow layer owned by the scalar-field source
        // group. It receives ongoing OSC control updates and is explicitly
        // freed with that group; self-freeing would leave a stale node handle
        // and flood the server with /n_set errors.
        var envelope = EnvGen.kr(Env.asr(0.05, 1, 0.25), gate);
        var signal = (pStereo * pAmount.sqrt * probabilityMix)
            + (tStereo * tAmount.sqrt * terrainMix);
        Out.ar(out, Limiter.ar(
            LeakDC.ar(signal) * 0.13 * soundEnabled * envelope, 0.9
        ))
    }).add;
    s.sync;
    if(~qmwQFTV3SourceGroup.notNil and: { ~qmwQFTV3SourceBus.notNil }) {
        ~qmwQFTV43FlowSynth !? _.free;
        // Create and acknowledge the persistent flow node before its first
        // array/control update.  A bundled creation here could leave the
        // client holding an ID that scsynth had not installed.
        ~qmwQFTV43FlowSynth = Synth.tail(
            ~qmwQFTV3SourceGroup,
            \qmwQFTV43ContinuousFlow,
            [\out, ~qmwQFTV3SourceBus, \fundamental, ~qmwQFTV3Fundamental]
        );
        s.sync;
        ~qmwQFTV43FlowSynth.setn(
            \flowPitchRatios,
            ~qmwQFTV3SitePitchRatios.copyRange(0, 7)
        );
        s.sync;
        ~qmwQFTV43UpdateFlowAudio.value
    }
};

~qmwQFTV3BuildAudio = {
    baseBuildAudio.value;
    ~qmwQFTV43BuildFlowAudio.value
};

OSCdef(\qmwQFTV43ProbabilityBegin, { |msg|
    ~qmwQFTV43ProbabilityRevision = msg[1].asInteger;
    ~qmwQFTV43ProbabilityStageValid = true;
    ~qmwQFTV43ProbabilityMaxFlux = 0.0;
    ~qmwQFTV43ProbabilitySignedFlux = 0.0;
    ~qmwQFTV43ProbabilityTotalFlux = 0.0
}, ~qmwQFTV43ProbabilityRoot ++ "/frame/begin", recvPort: 17863);
OSCdef(\qmwQFTV43ProbabilityBoundary, { |msg|
    if(~qmwQFTV43ProbabilityStageValid and: {
        msg[1].asInteger == ~qmwQFTV43ProbabilityRevision
    }) {
        ~qmwQFTV43ProbabilitySignedFlux = ~qmwQFTV43ProbabilitySignedFlux
            + msg[6].asFloat;
        ~qmwQFTV43ProbabilityTotalFlux = ~qmwQFTV43ProbabilityTotalFlux
            + msg[7].asFloat.abs;
        ~qmwQFTV43ProbabilityMaxFlux = ~qmwQFTV43ProbabilityMaxFlux
            .max(msg[7].asFloat.abs)
    }
}, ~qmwQFTV43ProbabilityRoot ++ "/boundary", recvPort: 17863);
OSCdef(\qmwQFTV43ProbabilityGlobal, { |msg|
    if(~qmwQFTV43ProbabilityStageValid and: {
        msg[1].asInteger == ~qmwQFTV43ProbabilityRevision
    }) {
        ~qmwQFTV43ProbabilityFlowEnergy = msg[3].asFloat;
        ~qmwQFTV43ProbabilityCoherenceFlow = msg[5].asFloat
    }
}, ~qmwQFTV43ProbabilityRoot ++ "/global", recvPort: 17863);
OSCdef(\qmwQFTV43ProbabilityEnd, { |msg|
    if(~qmwQFTV43ProbabilityStageValid and: {
        msg[1].asInteger == ~qmwQFTV43ProbabilityRevision
    }) {
        ~qmwQFTV43ProbabilityStageValid = false;
        ~qmwQFTV43UpdateFlowAudio.value
    }
}, ~qmwQFTV43ProbabilityRoot ++ "/frame/end", recvPort: 17863);

OSCdef(\qmwQFTV43MembraneBegin, { |msg|
    ~qmwQFTV43MembraneRevision = msg[1].asInteger;
    ~qmwQFTV43MembraneStageValid = true;
}, ~qmwQFTV43MembraneRoot ++ "/frame/begin", recvPort: 17863);
OSCdef(\qmwQFTV43MembraneAvailable, { |msg|
    if(~qmwQFTV43MembraneStageValid and: {
        msg[1].asInteger == ~qmwQFTV43MembraneRevision
    }) { ~qmwQFTV43MembraneAvailable = msg[2].asInteger > 0 }
}, ~qmwQFTV43MembraneRoot ++ "/available", recvPort: 17863);
OSCdef(\qmwQFTV43MembraneRhoReal, { |msg|
    if(~qmwQFTV43MembraneStageValid and: {
        msg[1].asInteger == ~qmwQFTV43MembraneRevision
    }) { ~qmwQFTV43StageRhoReal = msg.copyRange(2, 17).collect(_.asFloat) }
}, ~qmwQFTV43MembraneRoot ++ "/rho/real", recvPort: 17863);
OSCdef(\qmwQFTV43MembraneRhoImag, { |msg|
    if(~qmwQFTV43MembraneStageValid and: {
        msg[1].asInteger == ~qmwQFTV43MembraneRevision
    }) { ~qmwQFTV43StageRhoImag = msg.copyRange(2, 17).collect(_.asFloat) }
}, ~qmwQFTV43MembraneRoot ++ "/rho/imag", recvPort: 17863);
OSCdef(\qmwQFTV43MembraneStability, { |msg|
    if(~qmwQFTV43MembraneStageValid and: {
        msg[1].asInteger == ~qmwQFTV43MembraneRevision
    }) {
        ~qmwQFTV43OmegaMax = msg[2].asFloat;
        ~qmwQFTV43SpectralLimit = msg[3].asFloat;
        ~qmwQFTV43EffectiveCap = msg[4].asFloat;
        ~qmwQFTV43Substeps = msg[5].asInteger;
        ~qmwQFTV43ActualSubstep = msg[6].asFloat
    }
}, ~qmwQFTV43MembraneRoot ++ "/stability", recvPort: 17863);
OSCdef(\qmwQFTV43MembraneFlow, { |msg|
    if(~qmwQFTV43MembraneStageValid and: {
        msg[1].asInteger == ~qmwQFTV43MembraneRevision
    }) {
        ~qmwQFTV43TerrainFlowEnergy = msg[2].asFloat;
        ~qmwQFTV43TerrainCoherenceFlow = msg[3].asFloat;
        ~qmwQFTV43TerrainMaxFlux = msg[4].asFloat.abs;
        ~qmwQFTV43TerrainSignedFlux = msg[5].asFloat;
        ~qmwQFTV43TerrainTotalFlux = msg[7].asFloat
    }
}, ~qmwQFTV43MembraneRoot ++ "/flow", recvPort: 17863);
OSCdef(\qmwQFTV43MembraneEnd, { |msg|
    if(~qmwQFTV43MembraneStageValid and: {
        msg[1].asInteger == ~qmwQFTV43MembraneRevision
    }) {
        ~qmwQFTV43RhoReal = ~qmwQFTV43StageRhoReal.copy;
        ~qmwQFTV43RhoImag = ~qmwQFTV43StageRhoImag.copy;
        ~qmwQFTV43MembraneStageValid = false;
        ~qmwQFTV43UpdateFlowAudio.value;
        {
            ~qmwQFTV43RhoView !? _.refresh;
            ~qmwQFTV43StabilityStatus !? { |view|
                view.string_(
                    "ADAPTIVE TERRAIN LIVE / omega max % / spectral h<% / cap % / % substeps @ % s"
                    .format(
                        ~qmwQFTV43OmegaMax.round(0.001),
                        ~qmwQFTV43SpectralLimit.round(0.00001),
                        ~qmwQFTV43EffectiveCap.round(0.00001),
                        ~qmwQFTV43Substeps,
                        ~qmwQFTV43ActualSubstep.round(0.00001)
                    )
                ).stringColor_(Color.green(0.76))
            }
        }.defer
    }
}, ~qmwQFTV43MembraneRoot ++ "/frame/end", recvPort: 17863);

~qmwQFTV43ParseScala = { |path|
    var source, lines, description, declaredCount, pitchLines, ratios, degrees;
    var token, pieces, ratio, period;
    source = File.readAllString(path);
    lines = source.split(Char.nl).collect { |line| line.stripWhiteSpace }
        .select { |line| line.notEmpty and: { line.beginsWith("!").not } };
    if(lines.size < 2) { Error("invalid Scala file: missing description/count").throw };
    description = lines[0];
    declaredCount = lines[1].asInteger;
    pitchLines = lines.copyRange(2, (1 + declaredCount).min(lines.size - 1));
    if(pitchLines.size != declaredCount) {
        Error("invalid Scala file: declared degree count does not match data").throw
    };
    ratios = [1.0] ++ pitchLines.collect { |line|
        token = line.split($ )[0];
        if(token.contains("/"), {
            pieces = token.split($/);
            ratio = pieces[0].asFloat / pieces[1].asFloat
        }, {
            ratio = if(token.contains("."), {
                2.pow(token.asFloat / 1200)
            }, { token.asFloat })
        });
        if(ratio.isNaN or: { ratio == inf } or: { ratio == -inf } or: { ratio <= 0 }) {
            Error("invalid Scala interval: " ++ token).throw
        };
        ratio
    };
    period = if(ratios.last > 1.0, { ratios.last }, { 2.0 });
    degrees = if(ratios.last > 1.0 and: { ratios.size > 1 }, {
        ratios.copyRange(0, ratios.size - 2)
    }, { ratios });
    if(degrees.isEmpty) { degrees = [1.0] };
    (description: description, degrees: degrees, period: period, path: path)
};

~qmwQFTV43LoadScale = { |path|
    var scale;
    try {
        scale = ~qmwQFTV43ParseScala.(path);
        ~qmwQFTV43SelectedScalePath = path;
        ~qmwQFTV43Description = scale[\description];
        ~qmwQFTV43Degrees = scale[\degrees];
        ~qmwQFTV43Period = scale[\period];
        ~qmwQFTV43TuningStatus !? { |view|
            view.string_("% / % degrees / period %".format(
                ~qmwQFTV43Description,
                ~qmwQFTV43Degrees.size,
                ~qmwQFTV43Period.round(0.00001)
            ))
        }
    } { |error|
        ~qmwQFTV43TuningStatus !? { |view| view.string_("Scala error: " ++ error) };
        error.warn
    }
};

~qmwQFTV43ScaleRatioAt = { |degree|
    var degrees = ~qmwQFTV43Degrees;
    var count = degrees.size.max(1);
    var index = degree.asInteger;
    var cycles = (index / count).floor;
    degrees[index.mod(count)] * (~qmwQFTV43Period ** cycles)
};

~qmwQFTV43ApplyTuning = {
    var rootRatio;
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
        ~qmwQFTV3Synth !? { |synth|
            synth.setn(\sitePitchRatios, ~qmwQFTV3SitePitchRatios)
        };
        ~qmwQFTV43FlowSynth !? { |synth|
            synth.setn(\flowPitchRatios,
                ~qmwQFTV3SitePitchRatios.copyRange(0, 7))
        }
    };
    ~qmwQFTV43TuningStatus !? { |view|
        view.string_("SCALE ACTIVE / % / offset %".format(
            ~qmwQFTV43Description, ~qmwQFTV43DegreeOffset
        ))
    }
};

~qmwQFTV43ApplyPitchSource = {
    var geometryRatios;
    case
    { ~qmwQFTV43PitchSource == 0 } {
        ~qmwQFTV43Family = 0;
        ~qmwQFTV43FamilyMenu !? { |menu| menu.value_(0) };
        ~qmwQFTV43RefreshChoices.value
    }
    { ~qmwQFTV43PitchSource == 1 } {
        var enteringScala = ~qmwQFTV43Family != 4;
        ~qmwQFTV43Family = 4;
        // Initialise the first alphabetical subtable only when crossing into
        // Scala from another source. Reapplying Scala must retain the letter,
        // page, and filter the performer has already selected.
        if(enteringScala, {
            ~qmwQFTV43ScalaIndex = "A";
            ~qmwQFTV43ScalaIndexPage = 0;
            ~qmwQFTV43Filter = "";
        });
        ~qmwQFTV43FamilyMenu !? { |menu| menu.value_(4) };
        ~qmwQFTV43RefreshChoices.value
    }
    { ~qmwQFTV43PitchSource == 2 } {
        ~qmwQFTV3PitchMode = 0;
        ~qmwQFTV43BaseUpdatePitchRatios.value;
        ~qmwQFTV43TuningStatus !? { |view|
            view.string_("FIELD NORMAL MODES / periodic Klein-Gordon omega_k / omega_0")
        }
    }
    { ~qmwQFTV43PitchSource == 3 } {
        ~qmwQFTV3PitchMode = 1;
        ~qmwQFTV43BaseUpdatePitchRatios.value;
        ~qmwQFTV43TuningStatus !? { |view|
            view.string_("HARMONICS 1-16 / ideal integer series")
        }
    }
    { ~qmwQFTV43PitchSource == 4 } {
        ~qmwQFTV3PitchMode = 2;
        ~qmwQFTV43BaseUpdatePitchRatios.value;
        ~qmwQFTV43TuningStatus !? { |view|
            view.string_("ODD HARMONICS 1-31 / ideal odd-integer series")
        }
    }
    {
        geometryRatios = ~qmwQFTV43GeometryPitchRatios;
        if(geometryRatios.notNil and: { geometryRatios.size == siteCount }, {
            ~qmwQFTV3PitchMode = 3;
            ~qmwQFTV3SitePitchRatios = geometryRatios.copy;
            ~qmwQFTV3Synth !? { |synth|
                synth.setn(\sitePitchRatios, ~qmwQFTV3SitePitchRatios)
            };
            ~qmwQFTV43TuningStatus !? { |view|
                view.string_("GEOMETRY SPECTRUM ACTIVE / " ++ ~qmwQFTV43GeometryDescription)
            }
        }, {
            ~qmwQFTV43TuningStatus !? { |view|
                view.string_("GEOMETRY SPECTRUM UNAVAILABLE / no geometry eigenspectrum received")
            }
        })
    }
};

~qmwQFTV43BaseUpdatePitchRatios = ~qmwQFTV3UpdatePitchRatios;
~qmwQFTV3UpdatePitchRatios = {
    if(~qmwQFTV3PitchMode == 3, {
        ~qmwQFTV43ApplyTuning.value
    }, {
        ~qmwQFTV43BaseUpdatePitchRatios.value
    })
};

~qmwQFTV43RefreshChoices = {
    var paths = ~qmwQFTV43ScalePaths;
    var filter = ~qmwQFTV43Filter.toLower;
    var preferred, matches, indexed, pageSize, pageStart, pageEnd, indexName;
    pageSize = ~qmwQFTV43ScalaBrowseLimit;
    paths = case
    { ~qmwQFTV43Family == 1 } {
        preferred = "wilson7.scl";
        paths.select { |path| PathName(path).fileName.toLower.contains("wilson") }
    }
    { ~qmwQFTV43Family == 2 } {
        preferred = "tenney1.scl";
        paths.select { |path| PathName(path).fileName.toLower.contains("tenney") }
    }
    { ~qmwQFTV43Family == 3 } {
        preferred = "young-lm_piano.scl";
        paths.select { |path| PathName(path).fileName.toLower.beginsWith("young-lm_") }
    }
    { ~qmwQFTV43Family == 4 } {
        if(filter.notEmpty, {
            matches = paths.select { |path| PathName(path).fileName.toLower.contains(filter) };
            ~qmwQFTV43ScalaIndexPage = 0;
            ~qmwQFTV43ScalaIndexPageCount = (matches.size / pageSize).ceil.asInteger.max(1);
            if(matches.isEmpty, { [] }, { matches.copyRange(0, (pageSize - 1).min(matches.size - 1)) })
        }, {
            // Each index entry is a subtable. Numeric-leading scale names
            // live under 1-9; letter entries are case-insensitive.
            indexName = ~qmwQFTV43ScalaIndex;
            indexed = paths.select { |path|
                var name = PathName(path).fileNameWithoutExtension.toLower;
                if(name.isEmpty, { false }, {
                    if(indexName == "1-9", {
                        "0123456789".includes(name[0])
                    }, {
                        name.beginsWith(indexName.toLower)
                    })
                })
            };
            ~qmwQFTV43ScalaIndexPageCount = (indexed.size / pageSize).ceil.asInteger.max(1);
            ~qmwQFTV43ScalaIndexPage = ~qmwQFTV43ScalaIndexPage.clip(
                0, ~qmwQFTV43ScalaIndexPageCount - 1
            );
            pageStart = (~qmwQFTV43ScalaIndexPage * pageSize).asInteger;
            pageEnd = ((pageStart + pageSize - 1).min(indexed.size - 1)).asInteger;
            if(indexed.isEmpty, { [] }, { indexed.copyRange(pageStart, pageEnd) })
        })
    }
    {
        // The scale subtable belongs to Scala only. Do not present a hidden
        // full dictionary while the active source is n-EDO or another native
        // QFT pitch mode; choosing Scala enters its A-Z index explicitly.
        []
    };
    ~qmwQFTV43VisibleScalePaths = paths;
    ~qmwQFTV43ScaleMenu !? { |menu|
        menu.items_(if(paths.isEmpty, { ["no matching scales"] }, {
            paths.collect { |path| PathName(path).fileNameWithoutExtension }
        }));
        menu.value_(0)
    };
    ~qmwQFTV43ScalaIndexStatus !? { |view|
        view.string_(if(~qmwQFTV43Family == 4 and: { filter.isEmpty }, {
            "INDEX %  /  subtable % of %  /  % scales per page".format(
                ~qmwQFTV43ScalaIndex,
                ~qmwQFTV43ScalaIndexPage + 1,
                ~qmwQFTV43ScalaIndexPageCount,
                pageSize
            )
        }, {
            "FILTER RESULTS  /  % pages of % scales".format(
                ~qmwQFTV43ScalaIndexPageCount, pageSize
            )
        }))
    };
    if(paths.notEmpty and: { ~qmwQFTV43Family != 0 }, {
        var selected = paths.detect { |path| PathName(path).fileName == preferred } ? paths[0];
        ~qmwQFTV43ScaleMenu !? { |menu| menu.value_(paths.indexOfEqual(selected) ? 0) };
        ~qmwQFTV43LoadScale.(selected);
        ~qmwQFTV43ApplyTuning.value
    }, {
        if(~qmwQFTV43Family == 0) { ~qmwQFTV43ApplyTuning.value }
    })
};

~qmwQFTV43OpenPanel = {
    var window, makeSlider, voiceSliders, voiceNames, tuningY, sourceY;
    ~qmwQFTV43Window !? _.close;
    window = Window(
        "QMW QFT V4.3 — Adaptive Membrane + Tuning",
        Rect(180, 34, 780, 780),
        resizable: true,
        scroll: true
    );
    ~qmwQFTV43Window = window;
    window.background_(Color.grey(0.105));
    window.view.autohidesScrollers_(false).hasHorizontalScroller_(false)
        .hasVerticalScroller_(true);
    makeSlider = { |label, rect, spec, initial, action, labelWidth=90|
        EZSlider(window, rect, label, spec, action, initial,
            labelWidth: labelWidth, numberWidth: 58).setColors(
                Color.grey(0.17), Color.grey(0.78), Color.cyan(0.7),
                Color.grey(0.45), Color.grey(0.9), Color.cyan(0.8)
            )
    };
    StaticText(window, Rect(20, 14, 720, 28))
        .string_(if(~qmwQFTV44Enabled == true, {
            "V4.4 ADDITIVE MEMBRANE — pulse-first material layer"
        }, {
            "V4.3 ADDITIVE LAYER — complete V4.2 instrument remains underneath"
        }))
        .font_(Font("Helvetica Neue", 15, true)).stringColor_(Color.cyan(0.8));
    StaticText(window, Rect(20, 50, 720, 40))
        .string_(if(~qmwQFTV44Enabled == true, {
            "The main window owns the four-voice mixer. This panel adds scale pitch, membrane diagnostics, and GPE onset material."
        }, {
            "The main window retains its field display, clocks, presets, effects, and four pulse SynthDefs. This panel mirrors their live gains and adds scale pitch."
        }))
        .stringColor_(Color.grey(0.78));
    if(~qmwQFTV44Enabled == true, {
        StaticText(window, Rect(20, 112, 720, 54)).string_(
            "V4.4 keeps only discrete pulses audible. The V4.3 continuous P-flow / terrain / sine-square bed is muted, so its legacy mix controls are intentionally not shown here."
        ).stringColor_(Color.grey(0.72));
    }, {
    StaticText(window, Rect(20, 100, 720, 20)).string_("INHERITED 4-VOICE MIXER — LIVE GAIN")
        .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.yellow(0.82));
    voiceNames = ["Simple", "Gaussian", "Layered", "FM"];
    voiceSliders = Array.fill(4, { |voice|
        makeSlider.(voiceNames[voice], Rect(20 + (voice * 180), 126, 170, 30),
            ControlSpec(0, 2, \lin, 0.001, ~qmwQFTV3VoiceGains[voice]),
            ~qmwQFTV3VoiceGains[voice], { |view|
                ~qmwQFTV3VoiceGains[voice] = view.value;
                ~qmwQFTV3PulseVoiceMode = 4;
                ~qmwQFTV3UpdateVoiceMixer.value
            }, 64)
    });
    StaticText(window, Rect(20, 170, 720, 20))
        .string_("CONTINUOUS FLOW SONIFICATION — independent of crossing pulses")
        .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.yellow(0.82));
    ~qmwQFTV43FlowButton = Button(window, Rect(20, 196, 170, 28)).states_([
        ["FLOW SOUND OFF", Color.grey(0.7), Color.grey(0.2)],
        ["FLOW SOUND ON", Color.black, Color.green(0.72)]
    ]).value_(~qmwQFTV43FlowEnabled).action_({ |button|
        ~qmwQFTV43FlowEnabled = button.value;
        ~qmwQFTV43UpdateFlowAudio.value
    });
    ~qmwQFTV43CrossingButton = Button(window, Rect(202, 196, 190, 28)).states_([
        ["CROSSING PULSES OFF", Color.grey(0.7), Color.grey(0.2)],
        ["CROSSING PULSES ON", Color.black, Color.magenta(0.72)]
    ]).value_(~qmwQFTV42TerrainSonify).action_({ |button|
        ~qmwQFTV42TerrainSonify = button.value
    });
    makeSlider.("P-flow mix", Rect(410, 196, 330, 30),
        ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV43ProbabilityMix),
        ~qmwQFTV43ProbabilityMix, { |view|
            ~qmwQFTV43ProbabilityMix = view.value;
            ~qmwQFTV43UpdateFlowAudio.value
        }, 82);
    makeSlider.("terrain mix", Rect(20, 236, 350, 30),
        ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV43TerrainMix),
        ~qmwQFTV43TerrainMix, { |view|
            ~qmwQFTV43TerrainMix = view.value;
            ~qmwQFTV43UpdateFlowAudio.value
        }, 82);
    makeSlider.("sensitivity", Rect(390, 236, 350, 30),
        ControlSpec(1, 2000, \exp, 0.1, ~qmwQFTV43FlowSensitivity),
        ~qmwQFTV43FlowSensitivity, { |view|
            ~qmwQFTV43FlowSensitivity = view.value;
            ~qmwQFTV43UpdateFlowAudio.value
        }, 82);
    makeSlider.("sine→square", Rect(20, 276, 350, 30),
        ControlSpec(0, 1, \lin, 0.001, ~qmwQFTV43SineSquareDepth),
        ~qmwQFTV43SineSquareDepth, { |view|
            ~qmwQFTV43SineSquareDepth = view.value;
            ~qmwQFTV43UpdateFlowAudio.value
        }, 92);
    StaticText(window, Rect(390, 276, 350, 34)).string_(
        "flux magnitude → cutoff + amplitude\ncoherence → sine/square; signed flux → pan"
    ).stringColor_(Color.grey(0.74));
    ~qmwQFTV43FlowStatus = StaticText(window, Rect(20, 316, 720, 48))
        .string_("WAITING FOR CONTINUOUS P-FLOW + TERRAIN FLOW ON UDP 17863")
        .font_(Font("Menlo", 10)).stringColor_(Color.yellow(0.76));
    StaticText(window, Rect(20, 370, 720, 42)).string_(
        "P-flow is the independent quantum-probability provider. Terrain flow is the "
        ++ "mesoscopic rho→Lagrangian interpretation. Both are downstream sound controls."
    ).stringColor_(Color.grey(0.72));
    });

    // V4.4 has no duplicate mixer or continuous-flow controls above. Reclaim
    // that space so Scala selection and application are immediately visible.
    tuningY = if(~qmwQFTV44Enabled == true, { 190 }, { 420 });
    StaticText(window, Rect(20, tuningY, 720, 20)).string_(
        if(~qmwQFTV44Enabled == true, {
            "PITCH SOURCES + SCALA DICTIONARY"
        }, { "SCALE PITCH" })
    )
        .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.yellow(0.82));
    if(~qmwQFTV44Enabled == true, {
        ~qmwQFTV43PitchSourceMenu = PopUpMenu(window, Rect(20, tuningY + 26, 330, 28))
            .items_(~qmwQFTV43PitchSourceNames).value_(~qmwQFTV43PitchSource)
            .action_({ |menu|
                ~qmwQFTV43PitchSource = menu.value;
                ~qmwQFTV43TuningStatus !? { |view|
                    view.string_("PITCH SOURCE SELECTED / " ++ menu.items[menu.value] ++ " / press APPLY PITCH SOURCE")
                }
            });
        Button(window, Rect(362, tuningY + 26, 176, 28)).states_([["APPLY PITCH SOURCE"]])
            .action_({ ~qmwQFTV43ApplyPitchSource.value });
        StaticText(window, Rect(548, tuningY + 28, 192, 24)).string_(
            "geometry = supplied potential eigenspectrum"
        ).stringColor_(Color.grey(0.66)).font_(Font("Helvetica Neue", 9));
    });
    sourceY = tuningY + if(~qmwQFTV44Enabled == true, { 36 }, { 0 });
    ~qmwQFTV43FamilyMenu = PopUpMenu(window, Rect(20, sourceY + 26, 210, 28))
        .items_(~qmwQFTV43FamilyNames).value_(~qmwQFTV43Family)
        .action_({ |menu|
            ~qmwQFTV43Family = menu.value;
            if(~qmwQFTV44Enabled == true, {
                ~qmwQFTV43PitchSource = if(menu.value == 0, { 0 }, { 1 });
                ~qmwQFTV43PitchSourceMenu !? { |sourceMenu|
                    sourceMenu.value_(~qmwQFTV43PitchSource)
                }
            });
            if(menu.value == 4, {
                // Entering Scala always opens the first alphabetical
                // subtable, rather than retaining an old whole-archive view.
                ~qmwQFTV43ScalaIndex = "A";
                ~qmwQFTV43ScalaIndexPage = 0;
                ~qmwQFTV43Filter = "";
                ~qmwQFTV43FilterField !? { |field| field.string_("") };
                ~qmwQFTV43ScalaIndexMenu !? { |indexMenu|
                    indexMenu.value_(~qmwQFTV43ScalaIndexNames.indexOfEqual("A"))
                };
            });
            ~qmwQFTV43RefreshChoices.value
        });
    ~qmwQFTV43EDOSlider = makeSlider.("n-EDO", Rect(244, sourceY + 26, 230, 30),
        ControlSpec(5, 72, \lin, 1, ~qmwQFTV43EDO), ~qmwQFTV43EDO,
        { |view|
            ~qmwQFTV43EDO = view.value.round.asInteger;
            if(~qmwQFTV43Family == 0) { ~qmwQFTV43ApplyTuning.value }
        }, 58);
    ~qmwQFTV43OffsetSlider = makeSlider.("degree", Rect(488, sourceY + 26, 252, 30),
        ControlSpec(0, 127, \lin, 1, ~qmwQFTV43DegreeOffset),
        ~qmwQFTV43DegreeOffset, { |view|
            ~qmwQFTV43DegreeOffset = view.value.round.asInteger;
            ~qmwQFTV43ApplyTuning.value
        }, 58);
    ~qmwQFTV43FilterField = TextField(window, Rect(20, sourceY + 70, 360, 28))
        .string_(~qmwQFTV43Filter);
    Button(window, Rect(390, sourceY + 70, 130, 28)).states_([["FILTER"]]).action_({
        ~qmwQFTV43Filter = ~qmwQFTV43FilterField.string;
        ~qmwQFTV43Family = 4;
        ~qmwQFTV43ArchiveBrowseMode = 1;
        ~qmwQFTV43FamilyMenu.value_(4);
        ~qmwQFTV43PitchSource = 1;
        ~qmwQFTV43PitchSourceMenu !? { |sourceMenu| sourceMenu.value_(1) };
        ~qmwQFTV43RefreshChoices.value
    });
    Button(window, Rect(534, sourceY + 70, 206, 28)).states_([[
        "CLEAR FILTER / USE INDEX", Color.black, Color.green(0.62)
    ]]).action_({
        ~qmwQFTV43Filter = "";
        ~qmwQFTV43FilterField.string_("");
        ~qmwQFTV43ScalaIndexPage = 0;
        ~qmwQFTV43Family = 4;
        ~qmwQFTV43FamilyMenu.value_(4);
        ~qmwQFTV43PitchSource = 1;
        ~qmwQFTV43PitchSourceMenu !? { |sourceMenu| sourceMenu.value_(1) };
        ~qmwQFTV43RefreshChoices.value
    });
    ~qmwQFTV43ScalaIndexMenu = PopUpMenu(window, Rect(20, sourceY + 104, 120, 26))
        .items_(~qmwQFTV43ScalaIndexNames)
        .value_(~qmwQFTV43ScalaIndexNames.indexOfEqual(~qmwQFTV43ScalaIndex) ? 0)
        .action_({ |menu|
            ~qmwQFTV43ScalaIndex = ~qmwQFTV43ScalaIndexNames[menu.value];
            ~qmwQFTV43ScalaIndexPage = 0;
            ~qmwQFTV43Filter = "";
            ~qmwQFTV43FilterField.string_("");
            ~qmwQFTV43Family = 4;
            ~qmwQFTV43FamilyMenu.value_(4);
            ~qmwQFTV43RefreshChoices.value
        });
    Button(window, Rect(150, sourceY + 104, 70, 26)).states_([["PREV"]]).action_({
        ~qmwQFTV43ScalaIndexPage = (~qmwQFTV43ScalaIndexPage - 1).max(0);
        ~qmwQFTV43RefreshChoices.value
    });
    Button(window, Rect(228, sourceY + 104, 70, 26)).states_([["NEXT"]]).action_({
        ~qmwQFTV43ScalaIndexPage = (~qmwQFTV43ScalaIndexPage + 1).min(
            ~qmwQFTV43ScalaIndexPageCount - 1
        );
        ~qmwQFTV43RefreshChoices.value
    });
    ~qmwQFTV43ScalaIndexStatus = StaticText(window, Rect(310, sourceY + 106, 430, 22))
        .string_("SCALA INDEX / choose 1-9 or A-Z").stringColor_(Color.cyan(0.72));
    ~qmwQFTV43ScaleMenu = PopUpMenu(window, Rect(20, sourceY + 138, 404, 28))
        .items_(["select a Scala scale"]).action_({ |menu|
            if(~qmwQFTV43VisibleScalePaths.notNil and: {
                menu.value < ~qmwQFTV43VisibleScalePaths.size
            }) {
                ~qmwQFTV43Family = 4;
                ~qmwQFTV43FamilyMenu !? { |familyMenu| familyMenu.value_(4) };
                ~qmwQFTV43PitchSource = 1;
                ~qmwQFTV43PitchSourceMenu !? { |sourceMenu| sourceMenu.value_(1) };
                ~qmwQFTV43LoadScale.(~qmwQFTV43VisibleScalePaths[menu.value]);
                ~qmwQFTV43ApplyTuning.value
            }
        });
    Button(window, Rect(434, sourceY + 138, 144, 28)).states_([["APPLY SCALE"]])
        .action_({ ~qmwQFTV43ApplyTuning.value });
    Button(window, Rect(588, sourceY + 138, 152, 28)).states_([["AUDITION SCALE"]])
        .action_({
            // Bounded listening check: traverse the 16 active pitch ratios.
            // This is an audio adapter only and never changes QFT/GPE state.
            ~qmwQFTV43ApplyTuning.value;
            if(~qmwQFTV3AudioReady and: { ~qmwQFTV3SoundEnabled > 0 }, {
                siteCount.do { |site|
                    AppClock.sched(site * 0.12, {
                        ~qmwQFTV3RenderPulse.value(site, 0.06, 0.35, 0.12, 0.4,
                            0.35, 0.12, 0.05, 1.0, 0.2, 0.05);
                        nil
                    })
                };
                ~qmwQFTV43TuningStatus.string_("SCALA AUDITION / 16 active lane ratios")
            }, {
                ~qmwQFTV43TuningStatus.string_("SCALA AUDITION UNAVAILABLE / sound adapter is off or still booting")
            })
        });
    ~qmwQFTV43TuningStatus = StaticText(window, Rect(20, sourceY + 180, 720, 44))
        .string_("Scala archive: % files / indexed 1-9 and A-Z / FILTER searches every file.".format(
            ~qmwQFTV43ScalePaths.size
        )).stringColor_(Color.cyan(0.72));
    StaticText(window, Rect(20, sourceY + 232, 720, 54)).string_(
        "Scientific boundary: pitch and voice levels are downstream sound adapters. "
        ++ "They do not alter the V4 Gaussian field, the independent probability-flow provider, "
        ++ "rho, or the effective Lagrangian terrain."
    ).stringColor_(Color.grey(0.72));
    StaticText(window, Rect(20, 690, 720, 20))
        .string_("V4.3 ADAPTIVE RESONANT MEMBRANE — density matrix + runtime stability")
        .font_(Font("Helvetica Neue", 11, true)).stringColor_(Color.magenta(0.82));
    ~qmwQFTV43RhoView = UserView(window, Rect(20, 718, 190, 164))
        .background_(Color.grey(0.07));
    ~qmwQFTV43RhoView.drawFunc = {
        var magnitudes = Array.fill(16, { |index|
            (~qmwQFTV43RhoReal[index].squared + ~qmwQFTV43RhoImag[index].squared).sqrt
        });
        var maximum = magnitudes.maxItem.max(1e-9);
        var size = 32;
        Pen.stringAtPoint("rho  |.| / phase", 16@8,
            Font("Helvetica Neue", 10, true), Color.white.alpha_(0.8));
        4.do { |row|
            4.do { |column|
                var index = (row * 4) + column;
                var magnitude = (magnitudes[index] / maximum).clip(0, 1);
                var phase = ~qmwQFTV43RhoImag[index].atan2(~qmwQFTV43RhoReal[index]);
                var hue = phase.linlin(-pi, pi, 0.68, 0.0).wrap(0, 1);
                var rect = Rect(18 + (column * size), 30 + (row * size), size - 3, size - 3);
                Pen.fillColor = Color.hsv(hue, 0.78, 0.14 + (0.86 * magnitude), 0.96);
                Pen.fillRect(rect);
                Pen.strokeColor = if(row == column, {
                    Color.white.alpha_(0.8)
                }, { Color.white.alpha_(0.18) });
                Pen.strokeRect(rect)
            }
        }
    };
    ~qmwQFTV43StabilityStatus = StaticText(window, Rect(228, 726, 512, 80))
        .string_("WAITING FOR V4.3 ADAPTIVE MEMBRANE CAPABILITY ON UDP 17863")
        .font_(Font("Menlo", 10)).stringColor_(Color.yellow(0.76));
    StaticText(window, Rect(228, 814, 512, 58)).string_(
        "The substep cap is derived every frame from the current mass-normalized "
        ++ "stiffness spectrum, then bounded by the 1/240 resolution ceiling."
    ).stringColor_(Color.grey(0.72));
    Button(window, Rect(20, 900, 180, 30)).states_([["SHOW MAIN V4.3"]])
        .action_({ ~qmwQFTV3Window !? _.front });
    window.onClose_({
        if(~qmwQFTV43Window === window) { ~qmwQFTV43Window = nil }
    });
    // Present the panel before populating a potentially large offline archive.
    // A bad archive entry must not prevent the V4.4 material panel itself
    // from appearing.
    window.front;
    { ~qmwQFTV43RefreshChoices.value }.defer
};

~qmwQFTV3Stop = {
    ~qmwQFTV43Window !? _.close;
    ~qmwQFTV43FlowSynth !? _.free;
    ~qmwQFTV43FlowSynth = nil;
    [
        \qmwQFTV43ProbabilityBegin, \qmwQFTV43ProbabilityBoundary,
        \qmwQFTV43ProbabilityGlobal, \qmwQFTV43ProbabilityEnd,
        \qmwQFTV43MembraneBegin, \qmwQFTV43MembraneAvailable,
        \qmwQFTV43MembraneRhoReal, \qmwQFTV43MembraneRhoImag,
        \qmwQFTV43MembraneStability, \qmwQFTV43MembraneFlow,
        \qmwQFTV43MembraneEnd
    ].do { |key| OSCdef(key).free };
    baseStop.value
};

{
    ~qmwQFTV43OpenPanel.value;
    if(s.serverRunning and: { ~qmwQFTV3AudioReady } and: {
        ~qmwQFTV43FlowSynth.isNil
    }) {
        ~qmwQFTV43BuildFlowAudio.value
    };
    "QMW QFT V4.3 addon ready: continuous flow + inherited voices + pitch sources".postln
}.defer;
)
