/* Evaluate this whole file. Select the desired audio device BEFORE launch.
For spatial audio, set ~hybridEnableSpatial = true before evaluating; the device
must expose at least 20 outputs. Never reboot an active performance implicitly.
Base audio device UI supports <=8: after changing device there, stop server and
rerun this launcher with the selected device and spatial flag. */
(
var here = thisProcess.nowExecutingPath.dirname;
if((~hybridEnableSpatial == true) and: { s.serverRunning }, {
    "Spatial launch requires a stopped server. Stop audio first, then relaunch.".warn;
}, {
    if(~hybridEnableSpatial == true, { s.options.numOutputBusChannels = 20 });
    thisProcess.interpreter.executeFile(here +/+ "../../qmw/QMW_Spectral_V4_Portable/supercollider/qmw_scalar_field_observer_v4_2b.scd");
    // Base GUI defaults to 8 for any larger interface; retain requested count.
    // Its device-selection action still caps at 8: stop and relaunch after changing it.
    if(~hybridEnableSpatial == true, { ~qmwQFTV3OutputChannels = 20 });
    thisProcess.interpreter.executeFile(here +/+ "HybridPacketAddon.scd");
});
)
