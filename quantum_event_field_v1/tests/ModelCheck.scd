/* sclang ModelCheck.scd — verifies the actual SC model, not a Python port. */
(
var here = thisProcess.nowExecutingPath.dirname;
var check, trajectory, h=0.00001, worstNorm=0.0, worstContinuity=0.0;
var getEvents, fine, coarse, stationary, residue, maxDifference;
check = { |ok, message| if(ok.not, { ("FAIL: " ++ message).postln; 1.exit }) };
thisProcess.interpreter.executeFile(here +/+ "../supercollider/Model.scd");
4.do { |initial|
    361.do { |n|
        var t=n/10, f=~qefFrame.(t, initial), before=~qefFrame.(t-h, initial), after=~qefFrame.(t+h, initial);
        var dp=(after[\p]-before[\p])/(2*h);
        var j=f[\j], balance=[j[0].neg, j[0]-j[1], j[1]-j[2], j[2]];
        worstNorm = worstNorm.max((f[\p].sum-1).abs);
        worstContinuity = worstContinuity.max((dp-balance).abs.maxItem);
        check.((f[\incoming]-f[\outgoing]-balance).abs.maxItem < 1e-10, "current orientation");
        4.do { |i| check.((~qefDuration.(f,i) >= 0.03) and: { ~qefDuration.(f,i) <= 3 }, "decay bounds") };
    };
};
check.(worstNorm < 1e-10, "normalization"); check.(worstContinuity < 1e-7, "continuity");
getEvents = { |step|
    var events=List.new, previous=~qefFrame.(0), residual=0.0!4;
    (36/step).round.asInteger.do { |i|
        var next=~qefFrame.((i+1)*step);
        ~qefCrossings.(previous,next,residual,0.08,step).do { |e| events.add([((i+e[0])*step),e[1]]) };
        previous=next;
    }; events.asArray
};
fine=getEvents.(0.0025); coarse=getEvents.(0.005);
check.(fine.size == coarse.size, "refined event counts");
maxDifference=(fine.collect(_[0])-coarse.collect(_[0])).abs.maxItem;
check.(maxDifference < 0.003, "threshold convergence");
check.(fine.collect(_[1]) == coarse.collect(_[1]), "refined state ordering");
stationary=(incoming: 0.0!4); residue=0.0!4;
check.(~qefCrossings.(stationary, stationary, residue, 0.08, 100).isEmpty, "zero flow emits nothing");
// Constant rate and ramp integrations exercise sub-frame threshold solving.
residue=0.0!4;
trajectory=~qefCrossings.((incoming: [1,0,0,0]), (incoming: [1,0,0,0]), residue, 0.2, 1);
check.(trajectory.size == 5, "constant-flow count");
check.((trajectory.collect(_[0])-[0.2,0.4,0.6,0.8,1]).abs.maxItem < 1e-10, "constant-flow onset times");
residue=0.0!4;
trajectory=~qefCrossings.((incoming: [0,0,0,0]), (incoming: [2,0,0,0]), residue, 0.25, 1);
check.((trajectory.collect(_[0])-[0.25,0.5,0.75,1].sqrt).abs.maxItem < 1e-10, "ramp-flow onset times");
"MODEL PASS: norm %, continuity %, events %, refinement error % tau".format(
    worstNorm, worstContinuity, fine.size, maxDifference).postln;
0.exit;
)
