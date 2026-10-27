/* Independent full 16-state Pauli and complex-matrix checks of SC projections. */
(
var here=thisProcess.nowExecutingPath.dirname, check, kron, multiply, evaluate;
var identity=[[1,0],[0,1]], x=[[0,1],[1,0]], y, z=[[1,0],[0,-1]], operators;
var maxError=0.0, cases=0;
y=[[0,Complex(0,-1)],[Complex(0,1),0]];
check={ |ok, why| if(ok.not, { ("FAIL: " ++ why).postln; 1.exit }) };
thisProcess.interpreter.executeFile(here +/+ "../supercollider/Model.scd");
thisProcess.interpreter.executeFile(here +/+ "../supercollider/Observables.scd");
kron={ |a,b| Array.fill(4, { |i| Array.fill(4, { |j| a[i.div(2)][j.div(2)] * b[i%2][j%2] }) }) };
multiply={ |a,b| Array.fill(4, { |i| Array.fill(4, { |j| (0..3).sum { |k| a[i][k]*b[k][j] } }) }) };
operators=[kron.(z,identity),kron.(x,x),kron.(x,y),kron.(x,z)];
operators.do { |a,m|
    4.do { |i| 4.do { |j|
        var actual=Complex(~qefOperators[m][\re][i][j],~qefOperators[m][\im][i][j]);
        check.((actual-a[i][j]).abs < 1e-12, "Dirac tensor representation");
        check.((actual-Complex(~qefOperators[m][\re][j][i],~qefOperators[m][\im][j][i]).conjugate).abs < 1e-12, "Hermitian operator");
    } };
    operators.do { |b,n|
        var anticommutator=multiply.(a,b)+multiply.(b,a);
        4.do { |i| 4.do { |j|
            check.((anticommutator[i][j] - if((m==n) and: { i==j },{2},{0})).abs < 1e-12, "Clifford anticommutation");
        } };
    };
};
evaluate={ |frame|
    var obs=~qefObservables.(frame), psi, full=Array.fill(16,{Complex(0,0)}), phase=0.73, shifted, changed;
    psi=Array.fill(4,{ |i| Complex(frame[\re][i],frame[\im][i]) });
    [8,4,2,1].do { |index,i| full[index]=psi[i] };
    4.do { |site|
        var mask=1 << (3-site), px, py, pz, expected;
        px=(0..15).sum { |j| full[j].conjugate * full[j.bitXor(mask)] };
        py=(0..15).sum { |j| full[j].conjugate * full[j.bitXor(mask)] * Complex(0,if(j.bitAnd(mask)==0,{-1},{1})) };
        pz=(0..15).sum { |j| full[j].abs.squared * if(j.bitAnd(mask)==0,{1},{-1}) };
        expected=[px.real,py.real,pz];
        maxError=maxError.max((obs[\bloch][site]-expected).abs.maxItem);
        check.((obs[\localPurity][site]-((1+expected.squared.sum)/2)).abs < 1e-12, "local purity");
    };
    operators.do { |a,m|
        var expected=(0..3).sum { |i| (0..3).sum { |j| psi[i].conjugate*a[i][j]*psi[j] } };
        check.(expected.imag.abs < 1e-12, "real expectation");
        maxError=maxError.max((obs[\dirac][m]-expected.real).abs);
        check.(obs[\dirac][m].abs <= (1+1e-12), "Dirac expectation bound");
    };
    check.(obs[\audio].size==16, "packed observable channels");
    ~qefPairs.do { |pair,k|
        var expected=psi[pair[0]] * psi[pair[1]].conjugate;
        var c=obs[\coherences][k];
        check.((Complex(c[\re],c[\im])-expected).abs < 1e-12, "pair orientation");
        check.((c[\magnitude]-expected.abs).abs < 1e-12, "pair magnitude");
        check.(c[\magnitude] <= (0.5+1e-12), "coherence bound");
        if((pair[1]-pair[0])==1 and: { frame[\j].notNil }, {
            check.((2*c[\im]-frame[\j][pair[0]]).abs < 1e-12, "current/coherence identity");
        });
    };
    shifted=psi.collect { |a| a*Complex(phase.cos,phase.sin) };
    changed=~qefObservables.((re:shifted.collect(_.real),im:shifted.collect(_.imag)));
    check.((obs[\audio]-changed[\audio]).abs.maxItem < 1e-12, "global phase invariance");
    cases=cases+1;
};
4.do { |initial| 41.do { |n| evaluate.(~qefFrame.(n*0.25,initial)) } };
// Exercise nonzero real AND imaginary coherences beyond the special XX trajectory.
64.do { |n|
    var re=Array.fill(4,{ |i| ((i+1)*(n+1)*0.37).sin });
    var im=Array.fill(4,{ |i| ((i+2)*(n+1)*0.53).cos });
    var norm=(re.squared.sum+im.squared.sum).sqrt;
    evaluate.((re:re/norm,im:im/norm));
};
check.(~qefObservables.(~qefFrame.(0))[\coherences].every { |c| c[\phaseValid].not }, "undefined phase at zero coherence");
check.(maxError < 1e-12, "independent expectation agreement");
"OBSERVABLES PASS: % states; max full-state / matrix error %".format(cases,maxError).postln;
0.exit;
)
