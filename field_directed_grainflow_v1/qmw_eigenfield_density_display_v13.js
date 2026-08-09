autowatch = 1;
inlets = 1;
outlets = 1;

var density = [0, 0, 0, 0, 0, 0, 0, 0];

function list() {
    var a = arrayfromargs(arguments);
    if (a.length >= 4 && String(a[0]) === "stream" && String(a[2]) === "density") {
        var index = Math.floor(Number(a[1])) - 1;
        if (index >= 0 && index < density.length) {
            density[index] = Math.max(0, Math.min(1, Number(a[3])));
            outlet(0, density);
        }
    }
}

function anything() {
    var a = [messagename].concat(arrayfromargs(arguments));
    list.apply(this, a);
}
