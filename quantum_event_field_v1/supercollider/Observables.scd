/* Read-only projections of the SAME one-excitation state used by Model.scd.
Basis, in order: |1000>, |0100>, |0010>, |0001>. No independent evolution.
Dirac representation: beta = Z tensor I; alpha_i = X tensor sigma_i.
These are algebraic observables of this XX state, not a relativistic model. */
(
~qefPairs = [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]];
~qefPairLookup = [[0,0,1,2], [0,0,3,4], [1,3,0,5], [2,4,5,0]];
~qefOperators = [
    (name: "beta", formula: "Z tensor I", re: [[1,0,0,0],[0,1,0,0],[0,0,-1,0],[0,0,0,-1]], im: Array.fill(4, { 0!4 })),
    (name: "alpha_x", formula: "X tensor X", re: [[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]], im: Array.fill(4, { 0!4 })),
    (name: "alpha_y", formula: "X tensor Y", re: Array.fill(4, { 0!4 }), im: [[0,0,0,-1],[0,0,1,0],[0,-1,0,0],[1,0,0,0]]),
    (name: "alpha_z", formula: "X tensor Z", re: [[0,0,1,0],[0,0,0,-1],[1,0,0,0],[0,-1,0,0]], im: Array.fill(4, { 0!4 }))
];
~qefObservables = { |frame|
    var re=frame[\re], im=frame[\im], rhoRe, rhoIm, p, bloch, purity, pairs, dirac;
    rhoRe = Array.fill(4, { |i| Array.fill(4, { |j| (re[i]*re[j]) + (im[i]*im[j]) }) });
    rhoIm = Array.fill(4, { |i| Array.fill(4, { |j| (im[i]*re[j]) - (re[i]*im[j]) }) });
    p = Array.fill(4, { |i| rhoRe[i][i] });
    // Partial trace in a fixed one-excitation sector has zero local X and Y.
    bloch = p.collect { |value| [0.0, 0.0, 1-(2*value)] };
    purity = p.collect { |value| value.squared + (1-value).squared };
    pairs = ~qefPairs.collect { |pair|
        var r=rhoRe[pair[0]][pair[1]], q=rhoIm[pair[0]][pair[1]];
        var magnitude=(r.squared + q.squared).sqrt;
        (sites: pair, re: r, im: q, magnitude: magnitude,
            phase: if(magnitude > 1e-9, { q.atan2(r) }, { 0.0 }),
            phaseValid: magnitude > 1e-9)
    };
    dirac = ~qefOperators.collect { |op|
        // Tr(rho A); Hermiticity makes the expectation real.
        (0..3).sum { |i| (0..3).sum { |j|
            (rhoRe[i][j]*op[\re][j][i]) - (rhoIm[i][j]*op[\im][j][i])
        } }
    };
    (rhoRe: rhoRe, rhoIm: rhoIm, bloch: bloch, localPurity: purity,
        coherences: pairs, dirac: dirac,
        // Server control bus: six Re rho_ab, six Im rho_ab, beta/alpha_x/y/z.
        audio: pairs.collect { |pair| pair[\re] } ++ pairs.collect { |pair| pair[\im] } ++ dirac)
};
)
