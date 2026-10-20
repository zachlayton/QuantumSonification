/* Run AFTER StartHybrid and base audio ready. Starts at low gain.
Expected: brief Gaussian-driven resonance, then no H excitation without backend,
then synthesis resumes; base nodes and all seven FX sends remain allocated.
Listen through headphones at low output gain. Test actual audio separately. */
(
Routine({
    ~hybridStart.(); 2.wait;
    if(~hybridNode.isNil, { Error("Hybrid failed to start").throw });
    ~hybridSet.(\gain, 0.005);
    ~hybridSet.(\densityDepth, 1); ~hybridSet.(\envelopeDepth, 1);
    ~hybridNode.set(\t_burst, 1); 2.wait;
    ~hybridSet.(\blend, 1); ~hybridNode.set(\t_burst, 1); 2.wait;
    ~hybridSet.(\blend, 0); ~hybridNode.set(\t_burst, 1); 2.wait;
    ~hybridStop.();
    "Hybrid smoke sequence finished. Inspect server errors and verify audio by listening.".postln;
}).play(AppClock);
)
