/* Convert wrapped QTC radians to continuous cycles and a relational BPM.
   One instance per subsystem; RTT's own local clock makes the phasor. */
autowatch = 1;
inlets = 1;
outlets = 2;

var previous = 0.0;
var continuous = 0.0;
var initialized = false;
var previousMs = 0;
var smoothedBpm = 60.0;
var tempoScale = 4.0;

function msg_float(value) {
    var now = Date.now();
    var cycle = Number(value) / (2.0 * Math.PI);
    cycle = cycle - Math.floor(cycle);
    if (!initialized) {
        previous = cycle;
        continuous = cycle;
        initialized = true;
        previousMs = now;
    } else {
        var delta = cycle - previous;
        if (delta > 0.5) delta -= 1.0;
        if (delta < -0.5) delta += 1.0;
        continuous += delta;
        var elapsed = Math.max(0.001, (now - previousMs) / 1000.0);
        var instantaneous = Math.abs(delta) / elapsed * 60.0 * tempoScale;
        instantaneous = Math.max(8.0, Math.min(480.0, instantaneous));
        smoothedBpm = 0.82 * smoothedBpm + 0.18 * instantaneous;
        previous = cycle;
        previousMs = now;
    }
    outlet(1, smoothedBpm);
    outlet(0, continuous);
}

function reset() {
    initialized = false;
    previous = 0.0;
    continuous = 0.0;
    previousMs = 0;
    smoothedBpm = 60.0;
}
