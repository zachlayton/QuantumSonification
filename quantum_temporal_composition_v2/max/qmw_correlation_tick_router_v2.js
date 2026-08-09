/* Route a v2 relational tick by kind. No clock is generated in Max. */
autowatch = 1;
inlets = 1;
outlets = 3;

function routeTick(values) {
    if (values.length < 11) {
        outlet(2, ["malformed", values.length]);
        return;
    }
    var kind = String(values[2]);
    if (kind === "correlate") outlet(0, values);
    else if (kind === "differentiate") outlet(1, values);
    outlet(2, values);
}

function list() {
    routeTick(arrayfromargs(arguments));
}

/*
OSC-Route preserves the first OSC argument as Max's message selector when that
argument is a symbol. Tick IDs are symbols (for example t000001668), so without
anything() Max's js object looks for a function having the tick ID as its name.
Restore that selector to the front of the payload and route the complete tick.
*/
function anything() {
    var values = [messagename].concat(arrayfromargs(arguments));
    routeTick(values);
}
