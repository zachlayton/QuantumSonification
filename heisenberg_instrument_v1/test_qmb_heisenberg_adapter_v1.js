"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

class MockJitterMatrix {
    constructor(planecount, type, width, height) {
        this.planecount = planecount;
        this.type = type;
        this.dim = [width, height];
        this.name = "mock_" + MockJitterMatrix.nextName++;
        this.data = new Float64Array(planecount * width * height);
    }

    copyarraytomatrix(values) {
        const expected = this.planecount * this.dim[0] * this.dim[1];
        assert.strictEqual(values.length, expected);
        this.data = new Float64Array(values);
    }

    setcell2d(column, row) {
        const values = Array.from(arguments).slice(2);
        const expected = this.planecount * this.dim[0] * this.dim[1];
        if (this.data.length !== expected) {
            const resized = new Float64Array(expected);
            resized.set(this.data.slice(0, Math.min(this.data.length, expected)));
            this.data = resized;
        }
        const base = (row * this.dim[0] + column) * this.planecount;
        for (let plane = 0; plane < this.planecount; plane++) {
            this.data[base + plane] = values[plane] === undefined ? 0 : values[plane];
        }
    }
}
MockJitterMatrix.nextName = 0;

function loadAdapter() {
    const events = [];
    const context = {
        JitterMatrix: MockJitterMatrix,
        Float64Array,
        Number,
        Math,
        Array,
        Object,
        String,
        isFinite,
        outlet: function () { events.push(Array.from(arguments)); }
    };
    const source = fs.readFileSync(
        path.join(__dirname, "qmb_heisenberg_adapter_v1.js"), "utf8"
    );
    vm.createContext(context);
    vm.runInContext(source, context, {filename: "qmb_heisenberg_adapter_v1.js"});
    return {context, events};
}

function sendCompleteFrame(context, revision, realValues) {
    context.begin(revision, 2);
    context.real.apply(null, realValues);
    context.imag(0.0, 0.5, -0.5, 0.0);
    context.magnitude(1.0, 0.5, 0.5, 1.0);
    context.phase(0.0, Math.PI / 2, -Math.PI / 2, Math.PI);
    context.frequency_hz(110.0, 440.0, 440.0, 165.0);
    context.pan(-0.8, -0.45, 0.45, 0.8);
    context.end(revision);
}

{
    const {context, events} = loadAdapter();
    sendCompleteFrame(context, 7, [1.0, 2.0, 3.0, 4.0]);

    const commit = events.find(event => event[0] === 5 && event[1] === "commit");
    assert.deepStrictEqual(commit, [5, "commit", 7, 2, 1]);

    const active = context.banks[context.activeBank];
    assert.deepStrictEqual(
        Array.from(active.contributions.data),
        [1.0, 0.0, 2.0, 0.5, 3.0, -0.5, 4.0, 0.0]
    );
    assert.deepStrictEqual(Array.from(active.contributions.dim), [2, 2]);
}

{
    const {context, events} = loadAdapter();
    sendCompleteFrame(context, 1, [1.0, 0.0, 0.0, -1.0]);
    const firstBank = context.activeBank;
    const firstData = Array.from(context.banks[firstBank].contributions.data);

    context.begin(2, 2);
    context.real(9.0, 9.0, 9.0, 9.0);
    context.end(2);

    assert.strictEqual(context.activeBank, firstBank, "rejected frame changed active bank");
    assert.deepStrictEqual(Array.from(context.banks[firstBank].contributions.data), firstData);
    assert(events.some(event => event[0] === 6 && event[1] === "rejected" && event[2] === "missing_fields"));
}

{
    const {context, events} = loadAdapter();
    sendCompleteFrame(context, 10, [1.0, 0.0, 0.0, -1.0]);
    const firstBank = context.activeBank;
    sendCompleteFrame(context, 11, [2.0, 0.0, 0.0, -2.0]);

    assert.notStrictEqual(context.activeBank, firstBank, "successive commits did not swap banks");
    const commits = events.filter(event => event[0] === 5 && event[1] === "commit");
    assert.strictEqual(commits.length, 2);
}

console.log("qmb_heisenberg_adapter_v1: all tests passed");
