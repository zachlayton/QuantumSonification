// Run with node. Execute the actual Max JS in a mocked Max runtime.
const fs = require("fs");
const vm = require("vm");
const assert = require("assert");
const path = require("path");
let messages = [];
let now = 1000;
const context = {
    outlet: (...args) => messages.push(args),
    arrayfromargs: args => Array.from(args),
    Date: { now: () => now },
    messagename: "test"
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname, "../QMW_Hilbert_Suite/qmw_yang_mills_modal_v1.js"), "utf8"), context);
const vector = value => Array(16).fill(value);
const send = revision => {
    context.begin(revision, 0.1, 16);
    context.magnitude(revision, ...vector(0.4));
    context.speed(revision, ...vector(0.2));
    context.diagnostics(revision, 4, 0.00001, 1e-15, 1e-15, 1e-15);
    context.end(revision);
};
send(1);
assert.equal(messages.filter(m => m[0] === 0).length, 32);
assert(messages.filter(m => m[0] === 0).every(m => /^[ms]\d+$/.test(m[1])));
assert.equal(messages.find(m => m[1] === "m0")[2], 0.4);
messages = [];
context.begin(2, 0.2, 16);
context.magnitude(2, ...vector(0.5));
context.end(2); // missing speed and diagnostics
assert.equal(messages.filter(m => m[0] === 0).length, 0);
messages = [];
send(1); // stale committed revision
assert.equal(messages.length, 0);
context.begin(3, 0.3, 16);
context.begin(2, 0.2, 16); // old begin cannot replace revision 3
context.magnitude(3, ...vector(0.5));
context.speed(3, ...vector(0.2));
context.diagnostics(3, 4, 0, 0, 0, 0);
context.end(3);
assert.equal(context.committed, 3);
messages = [];
context.begin(4, 0.4, 16);
context.magnitude(4, NaN, ...vector(0.5).slice(1));
context.speed(4, ...vector(0.2));
context.diagnostics(4, 4, 0, 0, 0, 0);
context.end(4);
assert.equal(messages.filter(m => m[0] === 0).length, 0);
messages = [];
context.coupling(0.5);
send(5);
assert.equal(messages.find(m => m[1] === "m0")[2], 0.2);
messages = [];
now += 800;
context.bang(); // watchdog must release excitation
assert.equal(messages.filter(m => m[0] === 0).length, 32);
assert(messages.filter(m => m[0] === 0).every(m => m[2] === 0));
messages = [];
context.reset();
send(0); // explicit reset permits sender restart
assert.equal(context.committed, 0);
context.coupling(0);
messages = [];
send(1);
assert(messages.filter(m => m[0] === 0).every(m => m[2] === 0));
console.log("Max receiver: atomic commits, stale/incomplete/invalid rejection, gain, watchdog, reset passed");
