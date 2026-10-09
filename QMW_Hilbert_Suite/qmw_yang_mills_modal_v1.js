// Atomic field-energy adapter. Outputs only m0..m15 and s0..s15.
// Never writes pitch, quantum phase, purity, entropy, coherence or damping.
autowatch = 1;
inlets = 1;
outlets = 4; // Gen params, magnitudes, diagnostic list, status

var committed = -1;
var pending = null;
var gain = 1;
var lastReceived = 0;
var timedOut = true;
var timeoutMs = 750;

function validNumber(value) {
    return typeof value === "number" && isFinite(value);
}
function validRevision(value) {
    return validNumber(value) && value >= 0 && value < 2147483648 && Math.floor(value) === value;
}
function begin(revision, time, count) {
    if (!validRevision(revision) || revision <= committed || !validNumber(time) || time < 0 || count !== 16) return;
    // UDP can be reordered: an older begin must not destroy a newer pending frame.
    if (pending && revision <= pending.revision) return;
    pending = {revision: revision, magnitude: null, speed: null, diagnostics: null};
}
function acceptVector(name, args) {
    if (!pending || args.length !== 17 || args[0] !== pending.revision) return;
    var result = [];
    for (var i = 1; i < args.length; i++) {
        if (!validNumber(args[i]) || args[i] < 0 || args[i] > 1) {
            pending[name] = null;
            return;
        }
        result.push(args[i]);
    }
    pending[name] = result;
}
function magnitude() { acceptVector("magnitude", arrayfromargs(arguments)); }
function speed() { acceptVector("speed", arrayfromargs(arguments)); }
function diagnostics() {
    var args = arrayfromargs(arguments);
    if (!pending || args.length !== 6 || args[0] !== pending.revision) return;
    for (var i = 1; i < args.length; i++) {
        if (!validNumber(args[i])) { pending.diagnostics = null; return; }
    }
    pending.diagnostics = args.slice(1);
}
function end(revision) {
    if (!pending || revision !== pending.revision) return;
    if (!pending.magnitude || !pending.speed || !pending.diagnostics) {
        outlet(3, "incomplete", revision);
        pending = null;
        return;
    }
    var magnitudes = [];
    for (var i = 0; i < 16; i++) {
        magnitudes.push(gain * pending.magnitude[i]);
        outlet(0, "m" + i, magnitudes[i]);
        outlet(0, "s" + i, gain * pending.speed[i]);
    }
    outlet(1, magnitudes);
    outlet(2, pending.diagnostics);
    committed = revision;
    pending = null;
    lastReceived = Date.now();
    timedOut = false;
    outlet(3, "frame", revision);
}
function coupling(value) {
    if (!validNumber(value)) return;
    gain = Math.max(0, Math.min(1, value));
    if (gain === 0) silence();
}
function silence() {
    var zeros = [];
    for (var i = 0; i < 16; i++) {
        outlet(0, "m" + i, 0);
        outlet(0, "s" + i, 0);
        zeros.push(0);
    }
    outlet(1, zeros);
    timedOut = true;
}
function reset() {
    committed = -1;
    pending = null;
    silence();
    outlet(3, "reset");
}
function bang() {
    if (!timedOut && Date.now() - lastReceived > timeoutMs) {
        silence();
        pending = null;
        outlet(3, "timeout");
    }
}
function anything() {
    outlet(3, "unknown", messagename);
}
