/*
QMW Quantum Field Theory Instrument V5

V5 is the fixed-length continuum-resolution configuration of the shared
Gaussian scalar-field instrument. QMW_QFT_V5_SITES selects 8, 16, or 32 sites;
the launcher and Python backend use the same environment value.
*/
(
var selectedSites = ("QMW_QFT_V5_SITES".getenv ? "32").asInteger;
if([8, 16, 32].includes(selectedSites).not) { selectedSites = 32 };
~qmwQFTInstrumentVersion = 5;
~qmwQFTSiteCount = selectedSites;
~qmwQFTDataPort = 17870;
~qmwQFTControlPort = 17871;
~qmwQFTDecayMaximum = 5.0;
thisProcess.interpreter.executeFile(
    thisProcess.nowExecutingPath.dirname
    +/+ "qmw_scalar_field_observer_v3.scd"
);
)
