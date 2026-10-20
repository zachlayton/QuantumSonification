/*
    qmw_craive_source_router16_v9.js

    Converts the QMW spatial tuple

        voice azimuth elevation distance [spread]

    into the IRCAM Spat message

        /source/N/aed azimuth elevation distance

    Default QMW voice numbering is 0...15; Spat source numbering is 1...16.
    Send "indexbase 1" when the upstream voice numbers are already 1...16.

    inlet 0:
      - bare tuple: voice azimuth elevation distance [spread]
      - source/aed tuple with the same arguments
      - /qks/spat, /qqt/spat, or /qmw/spat followed by the tuple
      - native /source/... or /listener/... Spat messages
      - indexbase 0|1
      - distancerange minimum maximum
      - ring radius [elevation]
      - dump, clear, status

    outlet 0: native Spat control messages
    outlet 1: normalized source_spatial metadata, including spread
    outlet 2: status and validation messages

    Spread is intentionally metadata-only. CRAIVE's reference WFS patch fixes
    every source window size at 100; mapping an unrelated spread scale into
    that aperture without an explicit artistic decision would change the
    renderer.
*/

autowatch = 1;
inlets = 1;
outlets = 3;

setinletassist(0, "voice azimuth elevation distance [spread], OSC, or control");
setoutletassist(0, "IRCAM Spat /source/N/aed and native OSC messages");
setoutletassist(1, "normalized source_spatial metadata, including spread");
setoutletassist(2, "router status and validation messages");

var SOURCE_COUNT = 16;
var indexBase = 0;
var minimumDistance = 0.01;
var maximumDistance = 100.0;
var azimuths = new Array(SOURCE_COUNT);
var elevations = new Array(SOURCE_COUNT);
var distances = new Array(SOURCE_COUNT);
var spreads = new Array(SOURCE_COUNT);
var hasPosition = new Array(SOURCE_COUNT);

clearState();

function numeric(value) {
    var converted = Number(value);
    return isFinite(converted) ? converted : 0.0;
}

function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, numeric(value)));
}

function wrapAzimuth(value) {
    var wrapped = (numeric(value) + 180.0) % 360.0;
    if (wrapped < 0.0) {
        wrapped += 360.0;
    }
    return wrapped - 180.0;
}

function clearState() {
    var index;
    for (index = 0; index < SOURCE_COUNT; index++) {
        azimuths[index] = 0.0;
        elevations[index] = 0.0;
        distances[index] = 1.0;
        spreads[index] = 0.0;
        hasPosition[index] = 0;
    }
}

function sourceIdForVoice(value) {
    var voice = Math.floor(numeric(value));
    var sourceId = voice - indexBase + 1;

    if (sourceId < 1 || sourceId > SOURCE_COUNT) {
        outlet(2, [
            "error", "voice_out_of_range", voice,
            "indexbase", indexBase,
            "valid_voice_min", indexBase,
            "valid_voice_max", indexBase + SOURCE_COUNT - 1
        ]);
        return 0;
    }
    return sourceId;
}

function emitPosition(sourceId, azimuth, elevation, distance, spread, reason) {
    var index = sourceId - 1;
    var safeAzimuth = wrapAzimuth(azimuth);
    var safeElevation = clamp(elevation, -90.0, 90.0);
    var safeDistance = clamp(distance, minimumDistance, maximumDistance);
    var safeSpread = numeric(spread);
    var address = "/source/" + sourceId + "/aed";

    azimuths[index] = safeAzimuth;
    elevations[index] = safeElevation;
    distances[index] = safeDistance;
    spreads[index] = safeSpread;
    hasPosition[index] = 1;

    outlet(0, [address, safeAzimuth, safeElevation, safeDistance]);
    outlet(1, [
        "source_spatial", sourceId,
        safeAzimuth, safeElevation, safeDistance, safeSpread
    ]);
    outlet(2, [
        "position", reason,
        "source", sourceId,
        "azimuth", safeAzimuth,
        "elevation", safeElevation,
        "distance", safeDistance,
        "spread_metadata", safeSpread
    ]);
}

function routeTuple(values, reason) {
    var sourceId;
    var spread;

    if (values.length < 4 || values.length > 5) {
        outlet(2, [
            "error", "spatial_tuple_expected_4_or_5_values",
            "received", values.length
        ]);
        post("qmw craive router: expected voice azimuth elevation distance"
            + " [spread]; received " + values.length + " values\n");
        return;
    }

    sourceId = sourceIdForVoice(values[0]);
    if (sourceId === 0) {
        return;
    }
    spread = values.length === 5 ? values[4] : spreads[sourceId - 1];
    emitPosition(sourceId, values[1], values[2], values[3], spread, reason);
}

function list() {
    var values = arrayfromargs(arguments);
    var first;
    var second;

    if (values.length > 0 && typeof values[0] === "string") {
        first = String(values[0]);
        second = values.length > 1 ? String(values[1]) : "";

        if ((first === "qks" || first === "qqt" || first === "qmw")
                && second === "spat") {
            routeTuple(values.slice(2), first + "_spat_list");
            return;
        }
        if (first.charAt(0) === "/") {
            handleAddress(first, values.slice(1));
            return;
        }
    }
    routeTuple(values, "list");
}

function source() {
    routeTuple(arrayfromargs(arguments), "source");
}

function aed() {
    routeTuple(arrayfromargs(arguments), "aed");
}

function indexbase(value) {
    var requested = Math.floor(numeric(value));
    if (requested !== 0 && requested !== 1) {
        outlet(2, ["error", "indexbase_must_be_0_or_1", requested]);
        return;
    }
    indexBase = requested;
    outlet(2, ["indexbase", indexBase]);
}

function distancerange(minimum, maximum) {
    var safeMinimum = Math.max(0.0001, numeric(minimum));
    var safeMaximum = Math.max(safeMinimum, numeric(maximum));

    minimumDistance = safeMinimum;
    maximumDistance = safeMaximum;
    outlet(2, [
        "distancerange", minimumDistance, maximumDistance
    ]);
}

function ring(radius, elevation) {
    var safeRadius = clamp(radius, minimumDistance, maximumDistance);
    var safeElevation = arguments.length > 1
        ? clamp(elevation, -90.0, 90.0)
        : 0.0;
    var index;
    var azimuth;

    for (index = 0; index < SOURCE_COUNT; index++) {
        azimuth = -180.0 + (360.0 * index / SOURCE_COUNT);
        emitPosition(index + 1, azimuth, safeElevation, safeRadius, 0.0, "ring");
    }
}

function dump() {
    var index;
    for (index = 0; index < SOURCE_COUNT; index++) {
        if (hasPosition[index]) {
            emitPosition(
                index + 1,
                azimuths[index],
                elevations[index],
                distances[index],
                spreads[index],
                "dump"
            );
        }
    }
    emitStatus("dump");
}

function clear() {
    clearState();
    outlet(2, ["clear", "positions_forget_only", "no_spat_messages_sent"]);
}

function emitStatus(reason) {
    var known = 0;
    var index;
    for (index = 0; index < SOURCE_COUNT; index++) {
        known += hasPosition[index] ? 1 : 0;
    }
    outlet(2, [
        "router_status", reason,
        "sources", SOURCE_COUNT,
        "indexbase", indexBase,
        "known_positions", known,
        "distance_min", minimumDistance,
        "distance_max", maximumDistance,
        "spread_mapping", "metadata_only"
    ]);
}

function status() {
    emitStatus("query");
}

function handleAddress(address, values) {
    if (address === "/qks/spat"
            || address === "/qqt/spat"
            || address === "/qmw/spat") {
        routeTuple(values, address);
        return;
    }

    if (address.indexOf("/source/") === 0
            || address.indexOf("/listener/") === 0) {
        outlet(0, [address].concat(values));
        outlet(2, ["native_passthrough", address]);
        return;
    }

    outlet(2, ["error", "unsupported_address", address].concat(values));
}

function anything() {
    handleAddress(messagename, arrayfromargs(arguments));
}

function msg_int(value) {
    outlet(2, ["error", "tuple_required", value]);
}

function msg_float(value) {
    outlet(2, ["error", "tuple_required", value]);
}
