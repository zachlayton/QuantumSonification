/*
QMW Quantum Field Theory Instrument V4.2b

Loads the complete V4.2 instrument, then adds the v3-derived post-voice audio
bus mixer. The variant is additive: V4.2 dry routing and scientific authority
remain unchanged, while seven named audio sources may be sent to parallel
MiClouds and VST returns.
*/
(
~qmwQFTDisplayVersion = "4.2b";
~qmwQFTV42BFXEnabled = true;
thisProcess.interpreter.executeFile(
    thisProcess.nowExecutingPath.dirname
    +/+ "qmw_scalar_field_observer_v4_2.scd"
);
thisProcess.interpreter.executeFile(
    thisProcess.nowExecutingPath.dirname
    +/+ "qmw_v42b_audio_bus_mixer.scd"
);
)
