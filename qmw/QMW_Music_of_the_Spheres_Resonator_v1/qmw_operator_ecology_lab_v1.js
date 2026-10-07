// qmw_operator_ecology_lab_v1.js
// Four-candidate audition and transactional IR activation controller for Max.

autowatch = 1;
inlets = 3;
outlets = 10;

// outlets 0..3: replace messages for buffer~ slots A..D
// outlets 4..7: gain ramps for slots A..D
// outlet 8: ready / committed / failed acknowledgments
// outlet 9: human-readable status

// -1 selects automatic C/D ping-pong; nonnegative values force a slot.
var target_slot = -1;
var active_live_slot = -1;
var x_position = 0.0;
var y_position = 0.0;
var default_ramp_ms = 250.0;
var mute_ramp_ms = 40.0;
var pending_revision = -1;
var pending_slot = -1;
var pending_path = "";
var transaction_state = "idle";

function clamp01(value) {
    value = Number(value);
    if (!isFinite(value)) return 0.0;
    return Math.max(0.0, Math.min(1.0, value));
}

function slot_name(slot) {
    return ["A", "B", "C", "D"][Math.max(0, Math.min(3, slot))];
}

function status(message) {
    outlet(9, message);
}

function gain(slot, value, milliseconds) {
    outlet(4 + slot, clamp01(value), Math.max(0.0, Number(milliseconds)));
}

function xy(x, y, milliseconds) {
    x_position = clamp01(x);
    y_position = clamp01(y);
    var ramp = arguments.length > 2 ? Number(milliseconds) : default_ramp_ms;
    // Square roots make the four bilinear power weights sum to unity.
    gain(0, Math.sqrt((1.0 - x_position) * (1.0 - y_position)), ramp);
    gain(1, Math.sqrt(x_position * (1.0 - y_position)), ramp);
    gain(2, Math.sqrt((1.0 - x_position) * y_position), ramp);
    gain(3, Math.sqrt(x_position * y_position), ramp);
}

function audition(slot, milliseconds) {
    slot = Math.max(0, Math.min(3, parseInt(slot, 10)));
    var ramp = arguments.length > 1 ? Number(milliseconds) : default_ramp_ms;
    for (var index = 0; index < 4; index++)
        gain(index, index === slot ? 1.0 : 0.0, ramp);
    status("auditioning slot " + slot_name(slot));
}

function slot(value) {
    value = parseInt(value, 10);
    if (!isFinite(value) || value <= 0) {
        target_slot = -1;
        status("live candidates use automatic C/D ping-pong");
        return;
    }
    target_slot = Math.max(0, Math.min(3, value - 1));
    status("live candidates force target slot " + slot_name(target_slot));
}

function loadslot(slot_index) {
    var args = arrayfromargs(arguments);
    slot_index = Math.max(0, Math.min(3, parseInt(args.shift(), 10)));
    var path = args.join(" ");
    if (!path.length) {
        status("slot " + slot_name(slot_index) + " load ignored: empty path");
        return;
    }
    outlet(slot_index, "replace", path);
    status("loading " + slot_name(slot_index) + ": " + path);
}

function candidate(revision) {
    var args = arrayfromargs(arguments);
    revision = parseInt(args.shift(), 10);
    if (args.length < 2 || !isFinite(revision)) {
        status("invalid candidate message");
        return;
    }
    var crossfade = Number(args.pop());
    var path = args.join(" ");
    pending_revision = revision;
    pending_slot = target_slot >= 0
        ? target_slot
        : (active_live_slot === 2 ? 3 : 2);
    pending_path = path;
    default_ramp_ms = isFinite(crossfade) ? Math.max(0.0, crossfade) : default_ramp_ms;
    transaction_state = "muting";
    // Never replace an IR while its convolution output is audible.  The
    // line~ completion notification calls done(), which starts the load.
    gain(pending_slot, 0.0, mute_ramp_ms);
    status("candidate r" + revision + " preparing inactive slot " + slot_name(pending_slot));
}

function crossfade_start(revision, milliseconds) {
    revision = parseInt(revision, 10);
    if (revision !== pending_revision || transaction_state !== "ready") {
        status("ignored stale crossfade start r" + revision);
        return;
    }
    transaction_state = "crossfading";
    audition(pending_slot, Number(milliseconds));
    status("crossfading to r" + revision + " in slot " + slot_name(pending_slot));
}

function loaded(slot_index) {
    slot_index = parseInt(slot_index, 10);
    if (transaction_state !== "loading" || slot_index !== pending_slot) {
        status("slot " + slot_name(slot_index) + " loaded; convolution matrix ready");
        return;
    }
    transaction_state = "ready";
    outlet(8, "ready", pending_revision);
    status("candidate r" + pending_revision + " ready");
}

function loadfailed(slot_index) {
    var args = arrayfromargs(arguments);
    slot_index = parseInt(args.shift(), 10);
    var reason = args.join(" ") || "HIRT load failed";
    if (slot_index !== pending_slot || pending_revision < 0) return;
    outlet(8, "failed", pending_revision, reason);
    transaction_state = "failed";
    status("candidate r" + pending_revision + " failed: " + reason);
}

function done(slot_index) {
    slot_index = parseInt(slot_index, 10);
    if (transaction_state === "muting" && slot_index === pending_slot) {
        transaction_state = "loading";
        outlet(pending_slot, "replace", pending_path);
        status("candidate r" + pending_revision + " loading into " + slot_name(pending_slot));
        return;
    }
    if (transaction_state !== "crossfading" || slot_index !== pending_slot) return;
    outlet(8, "committed", pending_revision);
    status("candidate r" + pending_revision + " committed");
    if (pending_slot === 2 || pending_slot === 3)
        active_live_slot = pending_slot;
    transaction_state = "idle";
}

function reset() {
    pending_revision = -1;
    pending_slot = -1;
    pending_path = "";
    active_live_slot = -1;
    transaction_state = "idle";
    xy(0.0, 0.0, 0.0);
    status("reset; slot A active");
}

function loadbang() {
    xy(0.0, 0.0, 0.0);
    status("operator ecology lab ready");
}
