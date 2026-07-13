autowatch = 1;
inlets = 2;
outlets = 1;

var lastPath = "";

function anything() {
    var path = messagename;
    if (arguments.length > 0) {
        path = [messagename].concat(arrayfromargs(arguments)).join(" ");
    }
    emitIfChanged(path);
}

function list() {
    emitIfChanged(arrayfromargs(arguments).join(" "));
}

function reset() {
    lastPath = "";
}

function emitIfChanged(path) {
    if (!path || path === lastPath) {
        return;
    }
    lastPath = path;
    outlet(0, path);
}
