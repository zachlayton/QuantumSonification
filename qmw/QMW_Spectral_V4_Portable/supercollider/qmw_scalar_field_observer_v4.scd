/*
QMW Quantum Field Theory Instrument V4

This is the 16-site configuration of the shared V3/V4 instrument. The shared
implementation keeps every control, temporal adapter, renderer, recorder, and
sound mapping identical while increasing the physical lattice from 8 to 16
coupled harmonic degrees of freedom.
*/
(
~qmwQFTInstrumentVersion = 4;
~qmwQFTSiteCount = 16;
~qmwQFTDataPort = 17860;
~qmwQFTControlPort = 17861;
~qmwQFTDecayMaximum = 5.0;
thisProcess.interpreter.executeFile(
    thisProcess.nowExecutingPath.dirname
    +/+ "qmw_scalar_field_observer_v3.scd"
);
)
