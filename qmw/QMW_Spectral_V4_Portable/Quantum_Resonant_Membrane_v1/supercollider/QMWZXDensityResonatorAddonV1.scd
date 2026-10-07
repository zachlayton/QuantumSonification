/*
Verified ZX density -> Unified Instrument Resonator V3 sound adapter.

Load after V3. It stages complete /qmw/zx/density transactions on UDP 7500
and colors only an event that V1/V2/V3 has already admitted through
~qriRenderEvent. It never creates a pluck, changes event energy, retunes the
20-mode resonator, evolves rho, or sends OSC back upstream.
*/
(
var root = "/qmw/zx/density";
var port = (~qzxPort ? 7500).asInteger;
var modeCount = 20;
var laneCount = 16;
var commitFrame, shapeEvent;

~qzxCleanup !? { ~qzxCleanup.value };
thisProcess.openUDPPort(port);

~qzxPort = port;
~qzxEnabled = ~qzxEnabled ? true;
~qzxLastRevision = -1;
~qzxStage = nil;
~qzxFrame = (
    revision: -1, dimension: 0, weights: Array.fill(modeCount, 0.0),
    phases: Array.fill(modeCount, 0.0), coherence: Array.fill(modeCount, 0.0),
    purity: 1.0, entropy: 0.0, l1Coherence: 0.0
);
~qzxPriorRenderEvent = ~qriRenderEvent;

commitFrame = { |stage|
    var dimension = stage[\dimension];
    var real = stage[\real];
    var imag = stage[\imag];
    var populations = Array.fill(laneCount, { |index| real[index * laneCount + index].clip(0, 1) });
    var reference = populations.maxIndex;
    var weights = Array.fill(modeCount, 0.0);
    var phases = Array.fill(modeCount, 0.0);
    var coherence = Array.fill(modeCount, 0.0);

    laneCount.do { |lane|
        var re = real[lane * laneCount + reference];
        var im = imag[lane * laneCount + reference];
        var denominator = (populations[lane] * populations[reference]).sqrt.max(1e-12);
        weights[lane] = populations[lane].sqrt;
        if(lane != reference and: { (re.squared + im.squared).sqrt > 1e-9 }) {
            phases[lane] = im.atan2(re);
            coherence[lane] = ((re.squared + im.squared).sqrt / denominator).clip(0, 1);
        };
    };
    // The last four V3 modes are the q0-LSB reduced one-qubit descriptors.
    // They are not a new geometry or tuning: they complete the established
    // 16 basis lanes with four declared marginal observers.
    4.do { |qubit|
        var bit = 1 << qubit;
        var occupied = 0.0;
        var empty = 0.0;
        var re = 0.0;
        var im = 0.0;
        dimension.do { |index|
            if(index.bitAnd(bit) == 0) {
                var partner = index + bit;
                empty = empty + real[index * laneCount + index].clip(0, 1);
                if(partner < dimension) {
                    occupied = occupied + real[partner * laneCount + partner].clip(0, 1);
                    re = re + real[partner * laneCount + index];
                    im = im + imag[partner * laneCount + index];
                };
            };
        };
        weights[laneCount + qubit] = occupied.sqrt;
        if((re.squared + im.squared).sqrt > 1e-9) {
            phases[laneCount + qubit] = im.atan2(re);
            coherence[laneCount + qubit] = ((re.squared + im.squared)
                .sqrt / (empty * occupied).sqrt.max(1e-12)).clip(0, 1);
        };
    };
    ~qzxFrame = (
        revision: stage[\revision], dimension: dimension,
        weights: weights, phases: phases, coherence: coherence,
        purity: stage[\purity].clip(0, 1),
        entropy: (stage[\entropy] / dimension.log2).clip(0, 1),
        l1Coherence: (stage[\l1Coherence] / (dimension - 1).max(1)).clip(0, 1)
    );
    ~qzxLastRevision = stage[\revision];
    "ZX density revision % colors Unified Instrument Resonator V3 events; reference |%>"
        .format(stage[\revision], reference).postln;
};

shapeEvent = { |event|
    var sourceWeights;
    var sourcePhases;
    var shapedWeights;
    var shapedPhases;
    var peak;
    if(~qzxEnabled.not or: { ~qzxFrame[\revision] < 0 }, { event }, {
        sourceWeights = event[\weights] ? Array.fill(modeCount, 1.0);
        sourcePhases = event[\phases] ? Array.fill(modeCount, 0.0);
        // Preserve the pre-admitted event and its energy. The ZX descriptor
        // only selects its existing modal color; it cannot become an event.
        shapedWeights = Array.fill(modeCount, { |index|
            sourceWeights[index].asFloat.abs * (0.12 + (0.88 * ~qzxFrame[\weights][index]))
        });
        peak = shapedWeights.maxItem.max(1e-12);
        shapedWeights = shapedWeights / peak;
        shapedPhases = Array.fill(modeCount, { |index|
            sourcePhases[index].asFloat
                + (~qzxFrame[\phases][index] * ~qzxFrame[\coherence][index])
        });
        event.copy
            .put(\weights, shapedWeights)
            .put(\phases, shapedPhases)
            .put(\zxDensityRevision, ~qzxFrame[\revision])
    })
};

// V1/V2/V3 event admission remains upstream. This is the final observer layer.
~qriRenderEvent = { |event, level=1.0|
    ~qzxPriorRenderEvent.value(shapeEvent.value(event), level)
};

OSCdef(\qzxBeginV1, { |message|
    var dimension = message[3].asInteger;
    var revision = message[1].asInteger;
    if(revision > ~qzxLastRevision and: { dimension.inclusivelyBetween(2, laneCount) }) {
        ~qzxStage = (
            revision: revision, dimension: dimension, rows: Array.fill(dimension, nil),
            real: Array.fill(laneCount * laneCount, 0.0), imag: Array.fill(laneCount * laneCount, 0.0),
            purity: 1.0, entropy: 0.0, l1Coherence: 0.0
        );
    } {
        ~qzxStage = nil;
    };
}, root ++ "/begin", recvPort: port);

OSCdef(\qzxMetaV1, { |message|
    var stage = ~qzxStage;
    if(stage.notNil and: { message[1].asInteger == stage[\revision] }) {
        stage[\purity] = message[3].asFloat;
        stage[\l1Coherence] = message[4].asFloat;
        stage[\entropy] = message[5].asFloat;
    };
}, root ++ "/meta", recvPort: port);

OSCdef(\qzxRowV1, { |message|
    var stage = ~qzxStage;
    var row;
    var dimension;
    if(stage.notNil and: { message[1].asInteger == stage[\revision] }) {
        row = message[2].asInteger;
        dimension = stage[\dimension];
        if(row.inclusivelyBetween(0, dimension - 1) and: { message.size >= 3 + (2 * dimension) }) {
            dimension.do { |column|
                stage[\real][row * laneCount + column] = message[3 + column].asFloat;
                stage[\imag][row * laneCount + column] = message[3 + dimension + column].asFloat;
            };
            stage[\rows][row] = true;
        };
    };
}, root ++ "/row", recvPort: port);

OSCdef(\qzxEndV1, { |message|
    var stage = ~qzxStage;
    if(stage.notNil and: { message[1].asInteger == stage[\revision] }) {
        if(stage[\rows].all { |row| row.notNil }) { commitFrame.value(stage) } {
            "ZX density adapter rejected incomplete revision %".format(stage[\revision]).warn;
        };
        ~qzxStage = nil;
    };
}, root ++ "/end", recvPort: port);

OSCdef(\qzxErrorV1, { |message| ("ZX density source error: " ++ message[1]).warn }, root ++ "/error", recvPort: port);

~qzxCleanup = {
    [\qzxBeginV1, \qzxMetaV1, \qzxRowV1, \qzxEndV1, \qzxErrorV1].do { |key| OSCdef(key).free };
    ~qzxStage = nil;
    if(~qzxPriorRenderEvent.notNil) { ~qriRenderEvent = ~qzxPriorRenderEvent };
};

"QMW Unified Instrument Resonator V3 ZX density adapter listening on UDP %".format(port).postln;
)
