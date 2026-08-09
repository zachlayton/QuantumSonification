// qac_qasm_sender_v1.js
// Reliable OpenQASM transfer from The QAC Toolkit to QuantumSonification.
//
// Inlet messages:
//   qasm <complete QASM text>  -- replace buffer and transmit
//   append <QASM text>         -- append text without transmitting
//   clear                      -- clear buffer
//   send                       -- transmit current buffer
//   bang                       -- transmit current buffer
//   revision <positive int>    -- set the next revision explicitly
//
// Any message beginning with OPENQASM is treated as complete QASM and sent.
// Other unrecognized QAC outlet messages are ignored. This prevents
// statevector/count/memory output from contaminating the last QASM buffer.
// Line-oriented QASM can still be supplied deliberately with `append` + `send`.
//
// Outlets connect to:
//   0 -> [oscformat qmw qac begin]
//   1 -> [oscformat qmw qac chunk]
//   2 -> [oscformat qmw qac end]
//   3 -> status/diagnostics

autowatch = 1;
inlets = 1;
outlets = 4;

var buffer = "";
// Use Unix seconds as the session base so reloading the Max patch does not
// restart at revision 1 while a long-running Python bridge remembers a newer
// revision. Unix seconds remain within OSC's signed 32-bit integer range
// until 2038; subsequent sends increment locally.
var nextRevision = Math.floor((new Date()).getTime() / 1000);
var chunkCharacters = 700;

function atomsToText(args, includeName) {
    var items = [];
    if (includeName) items.push(messagename);
    for (var i = 0; i < args.length; i++) items.push(String(args[i]));
    return items.join(" ");
}

function setText(text) {
    buffer = String(text);
    outlet(3, ["buffer_chars", buffer.length]);
}

function qasm() {
    setText(atomsToText(arrayfromargs(arguments), false));
    transmit();
}

function append() {
    var text = atomsToText(arrayfromargs(arguments), false);
    buffer += (buffer.length ? "\n" : "") + text;
    outlet(3, ["buffer_chars", buffer.length]);
}

function clear() {
    buffer = "";
    outlet(3, "cleared");
}

function revision(value) {
    var candidate = Math.floor(Number(value));
    if (!isFinite(candidate) || candidate < 0) {
        outlet(3, ["error", "revision_must_be_nonnegative"]);
        return;
    }
    nextRevision = candidate;
    outlet(3, ["next_revision", nextRevision]);
}

function chunksize(value) {
    var candidate = Math.floor(Number(value));
    if (!isFinite(candidate) || candidate < 64 || candidate > 4000) {
        outlet(3, ["error", "chunksize_range_64_4000"]);
        return;
    }
    chunkCharacters = candidate;
}

function send() {
    transmit();
}

function bang() {
    transmit();
}

function anything() {
    var args = arrayfromargs(arguments);
    var text = atomsToText(args, true);
    if (/^OPENQASM\b/i.test(text)) {
        setText(text);
        transmit();
    } else {
        outlet(3, ["ignored", messagename, args.length]);
    }
}

function transmit() {
    if (!buffer.length) {
        outlet(3, ["error", "empty_qasm_buffer"]);
        return;
    }
    var encoded = encodeURIComponent(buffer);
    var total = Math.ceil(encoded.length / chunkCharacters);
    var current = nextRevision++;
    outlet(0, [current, total]);
    for (var index = 0; index < total; index++) {
        var start = index * chunkCharacters;
        var chunk = encoded.substring(start, start + chunkCharacters);
        outlet(1, [current, index, total, chunk]);
    }
    outlet(2, current);
    outlet(3, ["sent", current, total, buffer.length]);
}
