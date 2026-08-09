"use strict";

const assert = require("assert");
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const ROOT = __dirname;

function loadMaxJs(filename, extra = {}) {
    const output = [];
    const context = {
        Math,
        Number,
        String,
        Array,
        Infinity,
        autowatch: 0,
        inlets: 0,
        outlets: 0,
        outlet(index, ...values) { output.push([index, ...values]); },
        ...extra,
    };
    vm.createContext(context);
    vm.runInContext(fs.readFileSync(path.join(ROOT, filename), "utf8"), context, { filename });
    return { context, output };
}

function lastOutlet(output, index) {
    const values = output.filter((message) => message[0] === index);
    return values[values.length - 1];
}

function testScheduler() {
    const { context, output } = loadMaxJs("qmw_pauli_grainflow_scheduler_v1.js");
    context.initialize();

    const startMessages = output.filter((message) => message[3] === "startPoint");
    assert.deepStrictEqual(startMessages.map((message) => message[2]), [1, 2, 3, 4, 5, 6]);
    assert.deepStrictEqual(startMessages.map((message) => message[4]), [0, 1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6]);

    const addressedStreams = output
        .filter((message) => message[0] === 0 && message[1] === "stream")
        .map((message) => message[2]);
    assert(Math.min(...addressedStreams) === 1 && Math.max(...addressedStreams) === 6);
    assert(output.some((message) => message[0] === 0 && message[3] === "rateRandom"));

    context.statistics("fermion");
    context.width(40);
    context.particles(4);
    const occupied = lastOutlet(output, 1)[1];
    assert.strictEqual(occupied.reduce((sum, value) => sum + value, 0), 4);
    assert(occupied.every((value) => value === 0 || value === 1));

    context.particles(7);
    const excluded = lastOutlet(output, 1)[1];
    assert(excluded.every((value) => value === 0));
    assert(lastOutlet(output, 2).join(" ").includes("EXCLUDED OVERFILL"));
}

function testAtlas() {
    const buffers = { qmw_wavetable: new Array(256).fill(0) };
    function Buffer(name) { this.name = name; }
    Buffer.prototype.peek = function peek(channel, start, count) {
        return (buffers[this.name] || []).slice(start, start + count);
    };
    Buffer.prototype.poke = function poke(channel, start, values) {
        const target = buffers[this.name] || [];
        for (let index = 0; index < values.length; index += 1) target[start + index] = values[index];
        buffers[this.name] = target;
    };

    const { context, output } = loadMaxJs("qmw_quantum_wavetable_atlas_v1.js", { Buffer });
    context.seed();
    assert.strictEqual(buffers.qmw_wavetable.length, 256);
    context.render(41);
    assert.strictEqual(buffers.qmw_pauli_atlas_B.length, 98304);
    assert.deepStrictEqual(lastOutlet(output, 2).slice(1), ["commit", 41, 1, "qmw_pauli_atlas_B", 98304]);
    context.render(42);
    assert.strictEqual(buffers.qmw_pauli_atlas_A.length, 98304);
    assert.deepStrictEqual(lastOutlet(output, 2).slice(1), ["commit", 42, 0, "qmw_pauli_atlas_A", 98304]);
}

testScheduler();
testAtlas();
console.log("Max JS scheduler and atlas runtime harness passed");
