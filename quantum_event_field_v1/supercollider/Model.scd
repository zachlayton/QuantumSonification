/* Exact four-site open XX chain in its one-excitation sector.
H/J has nearest-neighbour entries 1. tau = J*t/hbar. No audio/GUI side effects. */
(
~qefModes = Array.fill(4, { |i|
    Array.fill(4, { |k| (2/5).sqrt * (((i+1)*(k+1)*pi)/5).sin })
});
~qefEnergies = Array.fill(4, { |k| 2 * (((k+1)*pi)/5).cos });
~qefFrame = { |tau, initial=0|
    var re, im, p, j, incoming, outgoing, source;
    re = Array.fill(4, { |i| (0..3).sum { |k|
        ~qefModes[i][k] * ~qefModes[initial][k] * (~qefEnergies[k]*tau).cos
    } });
    im = Array.fill(4, { |i| (0..3).sum { |k|
        ~qefModes[i][k] * ~qefModes[initial][k] * (~qefEnergies[k]*tau).sin.neg
    } });
    p = (re.squared + im.squared).clip(0, 1);
    j = Array.fill(3, { |i| -2 * ((re[i]*im[i+1]) - (im[i]*re[i+1])) });
    incoming = 0.0 ! 4; outgoing = 0.0 ! 4; source = (0..3);
    j.do { |flow, i|
        var from = if(flow >= 0, { i }, { i+1 });
        var to = if(flow >= 0, { i+1 }, { i });
        if(flow.abs > 1e-12, {
            if(flow.abs > incoming[to], { source[to] = from });
            incoming[to] = incoming[to] + flow.abs;
            outgoing[from] = outgoing[from] + flow.abs;
        });
    };
    (tau: tau, re: re, im: im, p: p, j: j, incoming: incoming,
        outgoing: outgoing, source: source)
};
// Each event consumes quantum units of integrated incoming probability current.
// Linear rate interpolation gives sub-frame threshold times, not a pulse grid.
~qefCrossings = { |previous, current, residual, quantum, dt|
    var events = List.new;
    4.do { |i|
        var b = previous[\incoming][i] * dt;
        var a = (current[\incoming][i] - previous[\incoming][i]) * dt * 0.5;
        var mass = (a + b).max(0), needed = quantum - residual[i], count = 0;
        while { (mass > 1e-14) and: { needed <= (mass + 1e-12) } } {
            var fraction;
            fraction = if(a.abs < 1e-14, { needed / b.max(1e-14) }, {
                (2 * needed) / (b + (b.squared + (4*a*needed)).max(0).sqrt).max(1e-14)
            });
            events.add([fraction.clip(0, 1), i]);
            count = count + 1; needed = needed + quantum;
        };
        residual[i] = (residual[i] + mass - (count * quantum)).max(0);
    };
    events.asArray.sort { |a, b| a[0] < b[0] }
};
~qefDuration = { |frame, site, secondsPerTau=0.8, decayScale=1|
    // Local turnover time, not a dissipative lifetime. Bounds are audio choices.
    ((frame[\p][site] / (frame[\incoming][site] + frame[\outgoing][site]).max(1e-9))
        * secondsPerTau * decayScale).clip(0.03, 3.0)
};
)
