// Address one vb.mi.rngs~ poly~ voice, then deliver its parameter frame.
autowatch = 1;
inlets = 1;
outlets = 1;

function voice(index) {
    var args = Array.prototype.slice.call(arguments, 1);
    var target = Math.max(1, Math.floor(Number(index)));
    outlet(0, "target", target);
    outlet.apply(this, [0, "params"].concat(args));
}
