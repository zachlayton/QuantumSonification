// qmw_implicit_surface_controller_v1.js
// Real-time implicit-surface probe controller for the QMW Gen~ geometry FDN.

autowatch = 1;
inlets = 1;
outlets = 2;

var surfaceNames = [
    "tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron",
    "sphere", "ellipsoid", "torus", "superellipsoid", "tanglecube",
    "heart", "roman_surface", "cayley",
    "gyroid", "schwarz_p", "schwarz_d", "neovius", "lidinoid", "iwp",
    "fischer_koch_s", "catenoid", "helicoid", "custom"
];

var presets = {
    tetrahedron:{ anchor: 0, depth: 0.54, harmonicity: 0.34, span: 0.30, topology: 0.52, absorb: 0.36, diffusion: 0.62, decay: 0.74 },
    cube:       { anchor: 1, depth: 0.42, harmonicity: 0.24, span: 0.22, topology: 0.64, absorb: 0.34, diffusion: 0.68, decay: 0.76 },
    octahedron: { anchor: 2, depth: 0.50, harmonicity: 0.30, span: 0.26, topology: 0.70, absorb: 0.32, diffusion: 0.72, decay: 0.78 },
    dodecahedron:{ anchor: 3, depth: 0.58, harmonicity: 0.32, span: 0.28, topology: 0.78, absorb: 0.30, diffusion: 0.76, decay: 0.80 },
    icosahedron:{ anchor: 4, depth: 0.64, harmonicity: 0.36, span: 0.32, topology: 0.84, absorb: 0.28, diffusion: 0.80, decay: 0.82 },
    sphere:     { anchor: 4, depth: 0.18, harmonicity: 0.18, span: 0.12, topology: 0.88, absorb: 0.28, diffusion: 0.78, decay: 0.70 },
    ellipsoid:  { anchor: 4, depth: 0.32, harmonicity: 0.22, span: 0.18, topology: 0.82, absorb: 0.30, diffusion: 0.76, decay: 0.73 },
    torus:      { anchor: 3, depth: 0.42, harmonicity: 0.28, span: 0.22, topology: 0.70, absorb: 0.32, diffusion: 0.72, decay: 0.76 },
    superellipsoid:{ anchor: 1, depth: 0.48, harmonicity: 0.30, span: 0.26, topology: 0.72, absorb: 0.33, diffusion: 0.70, decay: 0.78 },
    tanglecube: { anchor: 1, depth: 0.72, harmonicity: 0.38, span: 0.38, topology: 0.58, absorb: 0.38, diffusion: 0.64, decay: 0.82 },
    heart:      { anchor: 0, depth: 0.56, harmonicity: 0.46, span: 0.30, topology: 0.62, absorb: 0.34, diffusion: 0.70, decay: 0.74 },
    roman_surface:{ anchor: 0, depth: 0.66, harmonicity: 0.44, span: 0.40, topology: 0.54, absorb: 0.36, diffusion: 0.66, decay: 0.80 },
    cayley:     { anchor: 0, depth: 0.74, harmonicity: 0.48, span: 0.44, topology: 0.48, absorb: 0.38, diffusion: 0.62, decay: 0.82 },
    gyroid:     { anchor: 4, depth: 0.78, harmonicity: 0.34, span: 0.44, topology: 0.92, absorb: 0.26, diffusion: 0.88, decay: 0.86 },
    schwarz_p:  { anchor: 1, depth: 0.68, harmonicity: 0.26, span: 0.34, topology: 0.84, absorb: 0.30, diffusion: 0.82, decay: 0.80 },
    schwarz_d:  { anchor: 3, depth: 0.82, harmonicity: 0.32, span: 0.48, topology: 0.94, absorb: 0.24, diffusion: 0.90, decay: 0.88 },
    neovius:    { anchor: 2, depth: 0.88, harmonicity: 0.42, span: 0.52, topology: 0.90, absorb: 0.22, diffusion: 0.86, decay: 0.90 },
    lidinoid:   { anchor: 4, depth: 0.84, harmonicity: 0.40, span: 0.50, topology: 0.92, absorb: 0.24, diffusion: 0.88, decay: 0.88 },
    iwp:        { anchor: 2, depth: 0.76, harmonicity: 0.32, span: 0.42, topology: 0.88, absorb: 0.27, diffusion: 0.84, decay: 0.85 },
    fischer_koch_s:{ anchor: 3, depth: 0.86, harmonicity: 0.46, span: 0.54, topology: 0.94, absorb: 0.23, diffusion: 0.90, decay: 0.89 },
    catenoid:   { anchor: 3, depth: 0.62, harmonicity: 0.28, span: 0.36, topology: 0.74, absorb: 0.31, diffusion: 0.76, decay: 0.80 },
    helicoid:   { anchor: 0, depth: 0.72, harmonicity: 0.38, span: 0.46, topology: 0.68, absorb: 0.34, diffusion: 0.72, decay: 0.82 },
    custom:     { anchor: 4, depth: 0.68, harmonicity: 0.36, span: 0.42, topology: 0.80, absorb: 0.30, diffusion: 0.80, decay: 0.84 }
};

var probes = [];
var surfaceA = "sphere";
var surfaceB = "gyroid";
var morphValue = 0.0;
var deformation = 0.35;
var phaseValue = 0.0;
var lastEntropy = 0.0;
var lastPurity = 1.0;
var lastCoherence = 0.0;
var emergentEnabled = 0;
var customExpression = "(1+0.5*deform)*x*x + (1-0.3*deform)*y*y + z*z - 0.72";
var customAst = null;
var expressionError = "";
var expressionTokenLimit = 256;
var emergentState = {
    surface_area: 0.0,
    mean_height: 0.0,
    height_variance: 0.0,
    mean_curvature: 0.0,
    curvature_variance: 0.0,
    pattern_entropy: 0.0,
    anisotropy: 0.0,
    growth_velocity: 0.0
};

function clamp(value, low, high) {
    value = Number(value);
    if (!isFinite(value)) value = low;
    return Math.max(low, Math.min(high, value));
}

// Max's legacy `js` runtime does not implement ES6 Math.tanh.  This bounded
// form is numerically stable for the non-negative growth magnitude used here.
function positiveTanh(value) {
    value = Math.max(0.0, Number(value) || 0.0);
    var decay = Math.exp(-2.0 * value);
    return (1.0 - decay) / (1.0 + decay);
}

function mixValue(a, b, amount) {
    return a + (b - a) * amount;
}

// Convex polyhedra are represented by their outward unit face normals.  The
// implicit field is max(dot(normal, point)) - radius, which gives real facets
// and corners instead of merely selecting a related FDN preset.
var phi = (1.0 + Math.sqrt(5.0)) * 0.5;
var invPhi = 1.0 / phi;
var polyhedronNormals = {
    tetrahedron: [
        [1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]
    ],
    cube: [
        [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0],
        [0, 0, 1], [0, 0, -1]
    ],
    octahedron: [
        [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
        [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]
    ],
    dodecahedron: [
        [0, 1, phi], [0, 1, -phi], [0, -1, phi], [0, -1, -phi],
        [1, phi, 0], [1, -phi, 0], [-1, phi, 0], [-1, -phi, 0],
        [phi, 0, 1], [phi, 0, -1], [-phi, 0, 1], [-phi, 0, -1]
    ],
    icosahedron: [
        [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
        [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1],
        [0, invPhi, phi], [0, invPhi, -phi], [0, -invPhi, phi], [0, -invPhi, -phi],
        [invPhi, phi, 0], [invPhi, -phi, 0], [-invPhi, phi, 0], [-invPhi, -phi, 0],
        [phi, 0, invPhi], [phi, 0, -invPhi], [-phi, 0, invPhi], [-phi, 0, -invPhi]
    ]
};

function polyhedronField(name, x, y, z) {
    var normals = polyhedronNormals[name];
    var maximum = -1000000.0;
    for (var index = 0; index < normals.length; index++) {
        var normal = normals[index];
        var length = Math.sqrt(normal[0] * normal[0] + normal[1] * normal[1]
            + normal[2] * normal[2]);
        var projection = (normal[0] * x + normal[1] * y + normal[2] * z) / length;
        maximum = Math.max(maximum, projection);
    }
    return maximum - 0.68;
}

// Restricted expression compiler for CUSTOM.  It supports arithmetic,
// variables, and a small mathematical function vocabulary without eval() or
// Function(), so formula text cannot execute Max/JavaScript code.
function tokenizeExpression(source) {
    var tokens = [];
    var index = 0;
    while (index < source.length) {
        var rest = source.substring(index);
        var whitespace = rest.match(/^\s+/);
        if (whitespace) {
            index += whitespace[0].length;
            continue;
        }
        var number = rest.match(/^(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?/);
        if (number) {
            tokens.push({ type: "number", value: Number(number[0]) });
            index += number[0].length;
            continue;
        }
        var identifier = rest.match(/^[A-Za-z_][A-Za-z0-9_]*/);
        if (identifier) {
            tokens.push({ type: "identifier", value: identifier[0].toLowerCase() });
            index += identifier[0].length;
            continue;
        }
        var character = source.charAt(index);
        if ("+-*/^(),".indexOf(character) >= 0) {
            tokens.push({ type: character, value: character });
            index++;
            continue;
        }
        throw new Error("unexpected character '" + character + "'");
    }
    if (tokens.length > expressionTokenLimit) throw new Error("expression is too long");
    tokens.push({ type: "end", value: "" });
    return tokens;
}

function ExpressionParser(tokens) {
    this.tokens = tokens;
    this.position = 0;
}

ExpressionParser.prototype.peek = function () {
    return this.tokens[this.position];
};

ExpressionParser.prototype.take = function (type) {
    var token = this.peek();
    if (token.type !== type) throw new Error("expected '" + type + "'");
    this.position++;
    return token;
};

ExpressionParser.prototype.parse = function () {
    var node = this.parseAdditive();
    if (this.peek().type !== "end") throw new Error("unexpected token '" + this.peek().value + "'");
    return node;
};

ExpressionParser.prototype.parseAdditive = function () {
    var node = this.parseMultiplicative();
    while (this.peek().type === "+" || this.peek().type === "-") {
        var operator = this.peek().type;
        this.position++;
        node = { kind: "binary", operator: operator, left: node, right: this.parseMultiplicative() };
    }
    return node;
};

ExpressionParser.prototype.parseMultiplicative = function () {
    var node = this.parseUnary();
    while (this.peek().type === "*" || this.peek().type === "/") {
        var operator = this.peek().type;
        this.position++;
        node = { kind: "binary", operator: operator, left: node, right: this.parseUnary() };
    }
    return node;
};

ExpressionParser.prototype.parseUnary = function () {
    if (this.peek().type === "+" || this.peek().type === "-") {
        var operator = this.peek().type;
        this.position++;
        return { kind: "unary", operator: operator, value: this.parseUnary() };
    }
    return this.parsePower();
};

ExpressionParser.prototype.parsePower = function () {
    var node = this.parsePrimary();
    if (this.peek().type === "^") {
        this.position++;
        node = { kind: "binary", operator: "^", left: node, right: this.parseUnary() };
    }
    return node;
};

ExpressionParser.prototype.parsePrimary = function () {
    var token = this.peek();
    if (token.type === "number") {
        this.position++;
        return { kind: "number", value: token.value };
    }
    if (token.type === "(") {
        this.position++;
        var grouped = this.parseAdditive();
        this.take(")");
        return grouped;
    }
    if (token.type !== "identifier") throw new Error("expected a number, variable, or function");
    this.position++;
    var name = token.value;
    if (this.peek().type !== "(") return { kind: "variable", name: name };
    this.position++;
    var args = [];
    if (this.peek().type !== ")") {
        args.push(this.parseAdditive());
        while (this.peek().type === ",") {
            this.position++;
            args.push(this.parseAdditive());
        }
    }
    this.take(")");
    return { kind: "function", name: name, args: args };
};

var unaryFunctions = {
    sin: Math.sin, cos: Math.cos, tan: Math.tan,
    asin: Math.asin, acos: Math.acos, atan: Math.atan,
    abs: Math.abs, sqrt: Math.sqrt, exp: Math.exp, log: Math.log,
    floor: Math.floor, ceil: Math.ceil
};

function evaluateExpression(node, variables) {
    if (node.kind === "number") return node.value;
    if (node.kind === "variable") {
        if (variables.hasOwnProperty(node.name)) return variables[node.name];
        if (node.name === "pi") return Math.PI;
        if (node.name === "e") return Math.E;
        throw new Error("unknown variable '" + node.name + "'");
    }
    if (node.kind === "unary") {
        var unaryValue = evaluateExpression(node.value, variables);
        return node.operator === "-" ? -unaryValue : unaryValue;
    }
    if (node.kind === "binary") {
        var left = evaluateExpression(node.left, variables);
        var right = evaluateExpression(node.right, variables);
        if (node.operator === "+") return left + right;
        if (node.operator === "-") return left - right;
        if (node.operator === "*") return left * right;
        if (node.operator === "/") return Math.abs(right) < 1e-12 ? 0.0 : left / right;
        return Math.pow(left, right);
    }
    var args = [];
    for (var index = 0; index < node.args.length; index++)
        args.push(evaluateExpression(node.args[index], variables));
    if (unaryFunctions.hasOwnProperty(node.name)) {
        if (args.length !== 1) throw new Error(node.name + " expects one argument");
        return unaryFunctions[node.name](args[0]);
    }
    if (node.name === "min" || node.name === "max") {
        if (args.length < 2) throw new Error(node.name + " expects at least two arguments");
        return node.name === "min" ? Math.min.apply(Math, args) : Math.max.apply(Math, args);
    }
    if (node.name === "pow" || node.name === "mod") {
        if (args.length !== 2) throw new Error(node.name + " expects two arguments");
        return node.name === "pow" ? Math.pow(args[0], args[1]) : args[0] % args[1];
    }
    if (node.name === "clamp") {
        if (args.length !== 3) throw new Error("clamp expects three arguments");
        return clamp(args[0], args[1], args[2]);
    }
    throw new Error("unknown function '" + node.name + "'");
}

function compileExpression(source) {
    source = String(source);
    if (source.length > 512) throw new Error("expression is longer than 512 characters");
    var ast = new ExpressionParser(tokenizeExpression(source)).parse();
    // Validate names and arities immediately instead of waiting for a probe.
    evaluateExpression(ast, { x: 0.2, y: -0.3, z: 0.4, p: 0.0, phase: 0.0, t: 0.0, d: 0.35, deform: 0.35 });
    return ast;
}

function initializeProbes() {
    probes = [];
    var count = 20;
    var golden = Math.PI * (3.0 - Math.sqrt(5.0));
    for (var index = 0; index < count; index++) {
        var y = 1.0 - 2.0 * (index + 0.5) / count;
        var radius = Math.sqrt(Math.max(0.0, 1.0 - y * y));
        var angle = golden * index;
        probes.push([Math.cos(angle) * radius, y, Math.sin(angle) * radius]);
    }
}

function validSurface(name) {
    name = String(name).toLowerCase();
    var aliases = {
        tetra: "tetrahedron", octa: "octahedron",
        dodeca: "dodecahedron", icosa: "icosahedron",
        roman: "roman_surface", fischer_koch: "fischer_koch_s",
        schwarzp: "schwarz_p", schwarzd: "schwarz_d"
    };
    if (aliases.hasOwnProperty(name)) name = aliases[name];
    return presets.hasOwnProperty(name) ? name : null;
}

function rotateProbe(point) {
    var angle = phaseValue;
    var ca = Math.cos(angle);
    var sa = Math.sin(angle);
    var x = point[0] * ca - point[2] * sa;
    var z = point[0] * sa + point[2] * ca;
    var wobble = 0.10 * deformation * Math.sin(angle * 0.37);
    var cb = Math.cos(wobble);
    var sb = Math.sin(wobble);
    return [x, point[1] * cb - z * sb, point[1] * sb + z * cb];
}

function field(name, x, y, z) {
    var x2 = x * x;
    var y2 = y * y;
    var z2 = z * z;
    var k = Math.PI;
    var px = k * x + phaseValue * 0.17;
    var py = k * y - phaseValue * 0.11;
    var pz = k * z + phaseValue * 0.07;

    if (polyhedronNormals.hasOwnProperty(name))
        return polyhedronField(name, x, y, z);

    if (name === "sphere") {
        // A perfect sphere is constant on the spherical probe shell and would
        // collapse to zero after mean-centering. Deformation turns it into a
        // rotating ellipsoid so the default surface has an audible probe field.
        var sx = 1.0 + 0.62 * deformation;
        var sy = 1.0 - 0.38 * deformation;
        var sz = 1.0 + 0.24 * deformation * Math.sin(phaseValue + 0.7);
        return sx * x2 + sy * y2 + sz * z2 - 0.72;
    }
    if (name === "ellipsoid") {
        var ex = 1.0 + 0.75 * deformation;
        var ey = 1.0 - 0.42 * deformation;
        var ez = 1.0 + 0.30 * deformation * Math.cos(phaseValue * 0.71);
        return ex * x2 + ey * y2 + ez * z2 - 0.72;
    }
    if (name === "torus") {
        var major = 0.62;
        var minor = 0.28 + 0.08 * deformation;
        var sum = x2 + y2 + z2 + major * major - minor * minor;
        return sum * sum - 4.0 * major * major * (x2 + y2);
    }
    if (name === "superellipsoid") {
        var power = 2.4 + 3.0 * deformation;
        return Math.pow(Math.abs(x), power) + Math.pow(Math.abs(y), power)
            + Math.pow(Math.abs(z), power) - 0.52;
    }
    if (name === "tanglecube")
        return x2 * x2 - 5.0 * x2 + y2 * y2 - 5.0 * y2 + z2 * z2 - 5.0 * z2 + 10.6;
    if (name === "heart") {
        var heartCore = x2 + 2.25 * y2 + z2 - 1.0;
        return heartCore * heartCore * heartCore - x2 * z * z2 - 0.1125 * y2 * z * z2;
    }
    if (name === "roman_surface")
        return x2 * y2 + y2 * z2 + z2 * x2 - 1.15 * x * y * z;
    if (name === "cayley")
        return x2 + y2 + z2 + 2.0 * x * y * z - 0.82;
    if (name === "gyroid")
        return Math.sin(px) * Math.cos(py) + Math.sin(py) * Math.cos(pz) + Math.sin(pz) * Math.cos(px);
    if (name === "schwarz_p")
        return Math.cos(px) + Math.cos(py) + Math.cos(pz);
    if (name === "schwarz_d")
        return Math.sin(px) * Math.sin(py) * Math.sin(pz)
            + Math.sin(px) * Math.cos(py) * Math.cos(pz)
            + Math.cos(px) * Math.sin(py) * Math.cos(pz)
            + Math.cos(px) * Math.cos(py) * Math.sin(pz);
    if (name === "neovius")
        return 3.0 * (Math.cos(px) + Math.cos(py) + Math.cos(pz))
            + 4.0 * Math.cos(px) * Math.cos(py) * Math.cos(pz);
    if (name === "lidinoid")
        return 0.5 * (
            Math.sin(2.0 * px) * Math.cos(py) * Math.sin(pz)
            + Math.sin(2.0 * py) * Math.cos(pz) * Math.sin(px)
            + Math.sin(2.0 * pz) * Math.cos(px) * Math.sin(py)
        ) - 0.5 * (
            Math.cos(2.0 * px) * Math.cos(2.0 * py)
            + Math.cos(2.0 * py) * Math.cos(2.0 * pz)
            + Math.cos(2.0 * pz) * Math.cos(2.0 * px)
        ) + 0.15;
    if (name === "iwp")
        return 2.0 * (
            Math.cos(px) * Math.cos(py) + Math.cos(py) * Math.cos(pz)
            + Math.cos(pz) * Math.cos(px)
        ) - (Math.cos(2.0 * px) + Math.cos(2.0 * py) + Math.cos(2.0 * pz));
    if (name === "fischer_koch_s")
        return Math.cos(2.0 * px) * Math.sin(py) * Math.cos(pz)
            + Math.cos(px) * Math.cos(2.0 * py) * Math.sin(pz)
            + Math.sin(px) * Math.cos(py) * Math.cos(2.0 * pz);
    if (name === "catenoid") {
        var radial = Math.sqrt(x2 + y2);
        return radial - 0.34 * (Math.exp(z / 0.34) + Math.exp(-z / 0.34)) * 0.5;
    }
    if (name === "helicoid")
        return x * Math.sin(2.4 * z + phaseValue * 0.13)
            - y * Math.cos(2.4 * z + phaseValue * 0.13);
    if (name === "custom") {
        var customValue = evaluateExpression(customAst, {
            x: x, y: y, z: z,
            p: phaseValue, phase: phaseValue, t: phaseValue,
            d: deformation, deform: deformation
        });
        return isFinite(customValue) ? customValue : 0.0;
    }
    return 0.0;
}

function normalizedFieldSamples() {
    var values = [];
    var mean = 0.0;
    for (var index = 0; index < probes.length; index++) {
        var point = rotateProbe(probes[index]);
        var a = field(surfaceA, point[0], point[1], point[2]);
        var b = field(surfaceB, point[0], point[1], point[2]);
        var value = mixValue(a, b, morphValue);
        values.push(value);
        mean += value;
    }
    mean /= Math.max(values.length, 1);
    var maximum = 0.000001;
    for (var centeredIndex = 0; centeredIndex < values.length; centeredIndex++) {
        values[centeredIndex] -= mean;
        maximum = Math.max(maximum, Math.abs(values[centeredIndex]));
    }
    for (var normalizedIndex = 0; normalizedIndex < values.length; normalizedIndex++)
        values[normalizedIndex] = clamp(values[normalizedIndex] / maximum, -1.0, 1.0);
    return values;
}

function emitParameter(name, value) {
    outlet(0, name, Number(value));
}

function emitState() {
    var presetA = presets[surfaceA];
    var presetB = presets[surfaceB];
    var amount = morphValue;
    var values = normalizedFieldSamples();

    emitParameter("solid_a", presetA.anchor);
    emitParameter("solid_b", presetB.anchor);
    emitParameter("geometry_morph", amount);
    var emergentVariance = 1.0 - Math.exp(-20.0 * Math.abs(emergentState.height_variance));
    var emergentCurvature = 1.0 - Math.exp(-5.0 * Math.abs(emergentState.mean_curvature));
    var emergentEntropy = clamp(emergentState.pattern_entropy, 0.0, 1.0);
    var emergentAnisotropy = clamp(emergentState.anisotropy, 0.0, 1.0);
    var emergentGrowth = positiveTanh(
        10.0 * Math.abs(emergentState.growth_velocity)
    );
    var liveAmount = emergentEnabled ? 1.0 : 0.0;
    var liveDepth = clamp(
        0.12 + 0.40 * emergentVariance + 0.25 * emergentCurvature
        + 0.18 * emergentGrowth,
        0.0,
        0.85
    );
    var effectiveDeformation = mixValue(deformation, liveDepth, liveAmount);
    var geometryDepth = mixValue(presetA.depth, presetB.depth, amount);
    geometryDepth = clamp(
        geometryDepth + liveAmount * (0.20 * emergentCurvature + 0.12 * emergentAnisotropy),
        0.0,
        1.0
    );
    var topology = mixValue(presetA.topology, presetB.topology, amount);
    topology = clamp(topology + liveAmount * 0.12 * emergentEntropy, 0.0, 1.0);
    var absorb = mixValue(presetA.absorb, presetB.absorb, amount);
    absorb = clamp(absorb + liveAmount * 0.18 * emergentCurvature, 0.0, 0.95);
    var diffusion = mixValue(presetA.diffusion, presetB.diffusion, amount);
    diffusion = clamp(diffusion + liveAmount * 0.16 * emergentEntropy, 0.0, 1.0);

    emitParameter("surface_depth", effectiveDeformation);
    emitParameter("geometry_depth", geometryDepth);
    emitParameter("harmonicity", mixValue(presetA.harmonicity, presetB.harmonicity, amount));
    emitParameter("harmonic_span", mixValue(presetA.span, presetB.span, amount));
    emitParameter("topology", topology);
    emitParameter("absorb", absorb);
    emitParameter("diffusion", diffusion);
    emitParameter("decay", mixValue(presetA.decay, presetB.decay, amount));
    // Phase still rotates the implicit probe field. Explicit Gen~ XYZ rotation
    // is owned by the manual/Bloch source selector in the Max module, avoiding
    // competing rot_z messages when ANIMATE is enabled.

    for (var index = 0; index < values.length; index++)
        emitParameter("sf" + (index + 1), values[index]);

    // Outlet 1 is presentation text.  Emit the `set` selector ourselves so
    // the Max message box redraws immediately after every state change.
    outlet(1, "set", "surface", surfaceA, surfaceB, amount,
        "deform", effectiveDeformation, "mlx", emergentEnabled,
        "entropy", lastEntropy, "purity", lastPurity,
        "coherence", lastCoherence);
}

function a(name) {
    var valid = validSurface(name);
    if (valid !== null) {
        surfaceA = valid;
        emitState();
    }
}

function b(name) {
    var valid = validSurface(name);
    if (valid !== null) {
        surfaceB = valid;
        emitState();
    }
}

function surface(name) {
    var valid = validSurface(name);
    if (valid !== null) {
        surfaceA = valid;
        surfaceB = valid;
        morphValue = 0.0;
        emitState();
    }
}

function between(first, second) {
    var validA = validSurface(first);
    var validB = validSurface(second);
    if (validA !== null && validB !== null) {
        surfaceA = validA;
        surfaceB = validB;
        emitState();
    }
}

function morph(value) {
    morphValue = clamp(value, 0.0, 1.0);
    emitState();
}

function deform(value) {
    deformation = clamp(value, 0.0, 0.85);
    emitState();
}

function expr() {
    var pieces = arrayfromargs(arguments);
    var source = pieces.join(" ");
    // Some message paths preserve surrounding quote characters.
    if (source.length >= 2 && source.charAt(0) === '"'
            && source.charAt(source.length - 1) === '"')
        source = source.substring(1, source.length - 1);
    try {
        var compiled = compileExpression(source);
        customExpression = source;
        customAst = compiled;
        expressionError = "";
        outlet(1, "set", "expression_ok", customExpression);
        emitState();
    } catch (error) {
        expressionError = String(error.message || error);
        outlet(1, "set", "expression_error", expressionError);
    }
}

function custom_expr() {
    expr.apply(this, arrayfromargs(arguments));
}

function phase(value) {
    phaseValue = Number(value);
    if (!isFinite(phaseValue)) phaseValue = 0.0;
    emitState();
}

function magnitude() {
    var values = arrayfromargs(arguments);
    for (var index = 0; index < 8; index++)
        emitParameter("qm" + index, clamp(values[index] || 0.0, 0.0, 1.0));
}

function harmonics() {
    var values = arrayfromargs(arguments);
    for (var index = 0; index < 8; index++)
        emitParameter("qh" + index, Math.max(0.01, Number(values[index] || (index + 1))));
}

function entropy(value) {
    lastEntropy = clamp(value, 0.0, 1.0);
    emitParameter("noise_spectral_amount", 0.35 + 0.65 * lastEntropy);
}

function purity(value) {
    lastPurity = clamp(value, 0.0, 1.0);
}

function coherence(value) {
    lastCoherence = clamp(value, 0.0, 1.0);
    emitParameter("pauli_depth", 0.05 + 0.25 * lastCoherence);
}

function emergent_enable(value) {
    emergentEnabled = Number(value) !== 0 ? 1 : 0;
    emitState();
}

function emergent(name, value) {
    name = String(name);
    if (emergentState.hasOwnProperty(name)) {
        value = Number(value);
        emergentState[name] = isFinite(value) ? value : 0.0;
        // The MLX bridge publishes descriptors as one ordered frame ending
        // with growth_velocity. Recompute once per frame rather than once per
        // descriptor, keeping Max message traffic bounded at higher rates.
        if (emergentEnabled && name === "growth_velocity") emitState();
    }
}

function emergent_preset(name) {
    name = String(name);
    if (!emergentEnabled) return;
    if (name === "labyrinth") {
        surfaceA = "gyroid";
        surfaceB = "neovius";
    } else if (name === "cellular") {
        surfaceA = "sphere";
        surfaceB = "schwarz_p";
    } else if (name === "coral_growth") {
        surfaceA = "tanglecube";
        surfaceB = "schwarz_d";
    }
    emitState();
}

function reset() {
    surfaceA = "sphere";
    surfaceB = "gyroid";
    morphValue = 0.0;
    deformation = 0.35;
    phaseValue = 0.0;
    emergentEnabled = 0;
    customExpression = "(1+0.5*deform)*x*x + (1-0.3*deform)*y*y + z*z - 0.72";
    customAst = compileExpression(customExpression);
    expressionError = "";
    emitState();
}

function bang() {
    emitState();
}

function loadbang() {
    initializeProbes();
    emitParameter("surface_slew_ms", 250.0);
    emitParameter("morph_slew_ms", 500.0);
    emitParameter("noise_spectral_mode", 0.0);
    emitParameter("noise_spectral_amount", 0.75);
    emitParameter("noise_amount", 0.28);
    emitParameter("noise_floor", 0.008);
    // Match the compact FDN's production defaults.  The earlier conservative
    // values made the wet return roughly 6–7 dB quieter at each gain stage.
    emitParameter("input_gain", 0.65);
    emitParameter("output_gain", 0.72);
    emitState();
}

customAst = compileExpression(customExpression);
initializeProbes();
