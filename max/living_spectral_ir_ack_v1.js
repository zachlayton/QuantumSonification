// living_spectral_ir_ack_v1.js
// Max-side coordinator for two-phase Living Spectral Geometry IR activation.
//
// inlet 0: candidate <revision> <path> <crossfade_ms>
//          crossfade_start <revision> <crossfade_ms>
// inlet 1: ready <revision>
//          failed <revision> <reason...>
// inlet 2: committed <revision>
//
// outlet 0: load <revision> <path>        (to inactive convolution loader)
// outlet 1: start <revision> <ms>         (to convolution crossfader)
// outlet 2: ready|committed|failed ...    (route to OSC formatters)
// outlet 3: status <state> <revision>

autowatch = 1;
inlets = 3;
outlets = 4;

var pendingRevision = -1;
var pendingPath = "";
var pendingCrossfadeMs = 0.0;
var pendingState = "idle";
var activeRevision = -1;

function _number(value, label) {
    var result = Number(value);
    if (!isFinite(result)) {
        throw new Error(label + " must be numeric");
    }
    return result;
}

function _revision(value) {
    return Math.floor(_number(value, "revision"));
}

function _status(state, revision) {
    outlet(3, ["status", state, revision]);
}

function _reject(message, revision) {
    outlet(3, ["error", message, revision]);
}

function candidate(revision, path, crossfadeMs) {
    if (inlet !== 0) {
        _reject("candidate_wrong_inlet", revision);
        return;
    }
    try {
        var rev = _revision(revision);
        if (rev <= activeRevision || pendingRevision >= 0) {
            _reject("candidate_out_of_order", rev);
            return;
        }
        pendingRevision = rev;
        pendingPath = String(path);
        pendingCrossfadeMs = Math.max(0.0, _number(crossfadeMs, "crossfade_ms"));
        pendingState = "loading";
        outlet(0, ["load", pendingRevision, pendingPath]);
        _status(pendingState, pendingRevision);
    } catch (error) {
        _reject(String(error), revision);
    }
}

function crossfade_start(revision, crossfadeMs) {
    if (inlet !== 0) {
        _reject("crossfade_start_wrong_inlet", revision);
        return;
    }
    try {
        var rev = _revision(revision);
        if (rev !== pendingRevision || pendingState !== "ready") {
            _reject("crossfade_start_without_ready", rev);
            return;
        }
        pendingCrossfadeMs = Math.max(
            0.0,
            _number(crossfadeMs, "crossfade_ms")
        );
        pendingState = "crossfading";
        outlet(1, ["start", pendingRevision, pendingCrossfadeMs]);
        _status(pendingState, pendingRevision);
    } catch (error) {
        _reject(String(error), revision);
    }
}

function ready(revision) {
    if (inlet !== 1) {
        _reject("ready_wrong_inlet", revision);
        return;
    }
    var rev = _revision(revision);
    if (rev !== pendingRevision || pendingState !== "loading") {
        _reject("ready_out_of_order", rev);
        return;
    }
    pendingState = "ready";
    outlet(2, ["ready", rev]);
    _status(pendingState, rev);
}

function failed() {
    if (inlet !== 1) {
        _reject("failed_wrong_inlet", -1);
        return;
    }
    var args = arrayfromargs(arguments);
    var rev = _revision(args.shift());
    if (rev !== pendingRevision) {
        _reject("failed_out_of_order", rev);
        return;
    }
    var reason = args.length ? args.join(" ") : "inactive_loader_failed";
    outlet(2, ["failed", rev, reason]);
    _status("failed", rev);
    _clearPending();
}

function committed(revision) {
    if (inlet !== 2) {
        _reject("committed_wrong_inlet", revision);
        return;
    }
    var rev = _revision(revision);
    if (rev !== pendingRevision || pendingState !== "crossfading") {
        _reject("committed_before_crossfade_complete", rev);
        return;
    }
    activeRevision = rev;
    outlet(2, ["committed", rev]);
    _status("committed", rev);
    _clearPending();
}

function _clearPending() {
    pendingRevision = -1;
    pendingPath = "";
    pendingCrossfadeMs = 0.0;
    pendingState = "idle";
}

function reset() {
    pendingRevision = -1;
    pendingPath = "";
    pendingCrossfadeMs = 0.0;
    pendingState = "idle";
    activeRevision = -1;
    _status("reset", -1);
}

function status() {
    outlet(3, [
        "status",
        pendingState,
        pendingRevision,
        "active",
        activeRevision,
        "path",
        pendingPath
    ]);
}
