"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

class MockJitterMatrix {
    constructor(planecount, type, width, height) {
        this.planecount = planecount || 1;
        this.type = type || "float32";
        this.dim = [width || 1, height || 1];
        this._name = "mock_wave_" + MockJitterMatrix.next++;
        this.data = new Float64Array(this.planecount * this.dim[0] * this.dim[1]);
        MockJitterMatrix.registry[this._name] = this;
    }
    set name(value) {
        this._name = String(value);
        if (MockJitterMatrix.registry[this._name]) {
            const source = MockJitterMatrix.registry[this._name];
            this.planecount = source.planecount;
            this.type = source.type;
            this.dim = source.dim.slice();
            this.data = source.data;
        } else {
            MockJitterMatrix.registry[this._name] = this;
        }
    }
    get name() { return this._name; }
    copyarraytomatrix(values) { this.data = new Float64Array(values); MockJitterMatrix.registry[this.name] = this; }
    setcell1d(index, value) { this.data[index] = Number(value); MockJitterMatrix.registry[this.name] = this; }
    setcell2d(column, row, value) {
        const base = (row * this.dim[0] + column) * this.planecount;
        this.data[base] = Number(value);
        MockJitterMatrix.registry[this.name] = this;
    }
    getcell2d(column, row) {
        const base = (row * this.dim[0] + column) * this.planecount;
        if (this.planecount === 1) return this.data[base];
        return Array.from(this.data.slice(base, base + this.planecount));
    }
    getcell(column, row) { return this.getcell2d(column, row); }
}
MockJitterMatrix.next = 0;
MockJitterMatrix.registry = {};

function matrix(name, planes, dimension, values) {
    const result = new MockJitterMatrix(planes, "float64", dimension, dimension);
    result.name = name;
    result.data = new Float64Array(values);
    MockJitterMatrix.registry[name] = result;
    return result;
}

const events = [];
const context = {
    JitterMatrix: MockJitterMatrix, Float32Array, Array, Number, String, Math, isFinite,
    outlet: function () { events.push(Array.from(arguments)); },
    post: function () {}
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname, "qmb_heisenberg_rings_controller_v2.js"), "utf8"), context);

const d = 16;
const complex = [];
const magnitude = [];
const phase = [];
const frequency = [];
const pan = [];
for (let row = 0; row < d; row++) {
    for (let column = 0; column < d; column++) {
        complex.push(row === column ? 0.25 : 0.04, (column - row) * 0.02);
        magnitude.push(row === column ? 0.25 : 0.05);
        phase.push((column - row) * 0.3);
        frequency.push(110 * Math.pow(2, (row + column) / 12));
        pan.push((column - row) / (d - 1));
    }
}

matrix("c", 2, d, complex);
matrix("m", 1, d, magnitude);
matrix("p", 1, d, phase);
matrix("f", 1, d, frequency);
matrix("s", 1, d, pan);
context.rememberMatrix("contributions", ["jit_matrix", "c"]);
context.rememberMatrix("magnitude", ["jit_matrix", "m"]);
context.rememberMatrix("phase", ["jit_matrix", "p"]);
context.rememberMatrix("frequency_hz", ["jit_matrix", "f"]);
context.rememberMatrix("pan", ["jit_matrix", "s"]);
context.commit(7, d);
context.mapping_morph(0.35);
assert.strictEqual(context.mappingMorph, 0.35);
assert(events.some(event => event[0] === 2 && event[1] === "mapping_morph"));
context.phase_depth(0.8);
assert.strictEqual(context.phaseDepth, 0.8);
assert(events.some(event => event[0] === 2 && event[1] === "phase_depth"));
context.voice_map(1, "brightness", "real", 0.8);
assert.strictEqual(context.voiceMaps[0].brightness.real, 0.8);
context.voice_map(0, "position", "imag", 0.4);
assert.strictEqual(context.voiceMaps[15].position.imag, 0.4);
context.voice_map_clear(1);
assert.strictEqual(Object.keys(context.voiceMaps[0]).length, 0);
context.cell_map(3, "brightness", "real", 5, 0.75);
assert.strictEqual(context.cellMaps[2].brightness.real.column, 4);
assert.strictEqual(context.cellMaps[2].brightness.real.amount, 0.75);
context.cell_map_clear(3);
assert.strictEqual(Object.keys(context.cellMaps[2]).length, 0);

const waveEvent = events.find(event => event[0] === 0 && event[1] === "jit_matrix");
assert(waveEvent, "wavetable was not published");
const wave = MockJitterMatrix.registry[waveEvent[2]];
assert.strictEqual(wave.data.length, 2048);
assert(Math.max(...Array.from(wave.data).map(Math.abs)) <= 0.850001);
assert(Math.max(...Array.from(wave.data).map(Math.abs)) > 0.1);

const voices = events.filter(event => event[0] === 1 && event[1] === "voice");
assert.strictEqual(voices.length, d);
for (const voice of voices) {
    assert.strictEqual(voice.length, 10);
    assert(voice[3] >= 38 && voice[3] <= 74);
    assert([0, 3, 5, 7, 10].includes((voice[3] - 38 + 120) % 12));
    for (let i = 4; i <= 8; i++) assert(voice[i] >= 0 && voice[i] <= 1);
}
assert(events.some(event => event[0] === 2 && event[1] === "musical_commit"));

function phaseFrame(offset) {
    const cells = [];
    const magnitudes = [];
    const phases = [];
    const frequencies = [];
    const pans = [];
    for (let row = 0; row < d; row++) {
        for (let column = 0; column < d; column++) {
            const magnitude = row === column ? 0.25 : 0.05;
            const angle = row === column ? 0.0 : offset;
            cells.push([magnitude * Math.cos(angle), magnitude * Math.sin(angle)]);
            magnitudes.push(magnitude);
            phases.push(angle);
            frequencies.push(110 * Math.pow(2, (row + column) / 12));
            pans.push((column - row) / (d - 1));
        }
    }
    return { cells, magnitudes, phases, frequencies, pans };
}

context.phase_depth(1.0);
events.length = 0;
const phaseA = phaseFrame(0.0);
context.publishRows(d, phaseA.cells, phaseA.magnitudes, phaseA.phases, phaseA.frequencies, phaseA.pans);
const voicesA = events.filter(event => event[0] === 1 && event[1] === "voice");
events.length = 0;
const phaseB = phaseFrame(Math.PI / 2);
context.publishRows(d, phaseB.cells, phaseB.magnitudes, phaseB.phases, phaseB.frequencies, phaseB.pans);
const voicesB = events.filter(event => event[0] === 1 && event[1] === "voice");
assert.strictEqual(voicesA.length, d);
assert.strictEqual(voicesB.length, d);
assert(
    Math.abs(voicesA[0][5] - voicesB[0][5]) > 0.2,
    "a quarter-turn phase observation should audibly change voice brightness"
);
assert(
    Math.abs(voicesA[0][7] - voicesB[0][7]) > 0.2,
    "a quarter-turn phase observation should audibly change voice position"
);

console.log("qmb_heisenberg_rings_controller_v2: all tests passed");
