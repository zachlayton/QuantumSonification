inlets = 1;
outlets = 1;

var parameterNames = [
    "q", "energy",
    "cm5r", "cm5i", "cm4r", "cm4i", "cm3r", "cm3i",
    "cm2r", "cm2i", "cm1r", "cm1i", "c0r", "c0i",
    "cp1r", "cp1i", "cp2r", "cp2i", "cp3r", "cp3i",
    "cp4r", "cp4i", "cp5r", "cp5i"
];

function list() {
    var values = arrayfromargs(arguments);
    if (values.length !== parameterNames.length) {
        post("Bloch state: expected 24 values, received " + values.length + "\n");
        return;
    }
    for (var index = 0; index < parameterNames.length; index++)
        outlet(0, [parameterNames[index], Number(values[index])]);
}
