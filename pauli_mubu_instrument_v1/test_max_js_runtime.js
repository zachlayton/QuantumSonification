"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = __dirname;

function loadMaxJs(filename, extra = {}) {
    const output = [];
    const context = {
        Math,
        Number,
        String,
        Array,
        Infinity,
        Date,
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
    const { context, output } = loadMaxJs("qmw_pauli_mubu_scheduler_v1.js");
    context.density(1);
    context.width(40);
    context.particles(4);
    context.initialize();

    assert(output.some((message) => message[0] === 0 && message[1] === "microtiming" && message[2] === 1));
    assert(output.some((message) => message[0] === 0 && message[1] === "outputposition" && message[2] === 1));
    const occupied = lastOutlet(output, 1)[1];
    assert.strictEqual(occupied.reduce((sum, value) => sum + value, 0), 4);
    assert(occupied.every((value) => value === 0 || value === 1));

    const bangs = output.filter((message) => message[0] === 0 && message[1] === "bang");
    assert.strictEqual(bangs.length, 4);
    const gains = output.filter((message) => message[0] === 0 && message[1] === "outputgains");
    assert.strictEqual(gains.length, 4);
    assert(gains.every((message) => message.slice(2).reduce((sum, value) => sum + value, 0) === 1));
    const levels = output.filter((message) => message[0] === 0 && message[1] === "level");
    assert.strictEqual(levels.length, 4);
    assert(levels.every((message) => message[2] > 0 && message[2] <= 100));
    assert(output.some((message) => message[0] === 0 && message[1] === "resamplingvar"));

    const stateAppend = lastOutlet(output, 4);
    assert.strictEqual(stateAppend[1], "append");
    assert.strictEqual(stateAppend.length, 15);
    const grainAppends = output.filter((message) => message[0] === 5 && message[1] === "append");
    assert.strictEqual(grainAppends.length, 4);
    assert(grainAppends.every((message) => message.length === 9));

    const bangCount = bangs.length;
    context.particles(7);
    assert(lastOutlet(output, 1)[1].every((value) => value === 0));
    assert(lastOutlet(output, 2).join(" ").includes("EXCLUDED OVERFILL"));
    assert.strictEqual(output.filter((message) => message[0] === 0 && message[1] === "bang").length, bangCount);
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
    const { context, output } = loadMaxJs("qmw_mubu_wavetable_atlas_v1.js", { Buffer });
    context.seed();
    context.render(11);
    assert.strictEqual(buffers.qmw_pauli_mubu_atlas_B.length, 98304);
    assert.deepStrictEqual(lastOutlet(output, 2).slice(1), ["commit", 11, 1, "qmw_pauli_mubu_atlas_B", 98304]);
    context.render(12);
    assert.strictEqual(buffers.qmw_pauli_mubu_atlas_A.length, 98304);
    assert.deepStrictEqual(lastOutlet(output, 2).slice(1), ["commit", 12, 0, "qmw_pauli_mubu_atlas_A", 98304]);
}

testScheduler();
testAtlas();
console.log("MuBu scheduler, corpus messages, and atlas runtime harness passed");
