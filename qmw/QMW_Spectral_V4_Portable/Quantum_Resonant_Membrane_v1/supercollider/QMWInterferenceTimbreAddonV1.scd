/*
QMW Interference Timbre Add-on v1

QuantumResonantMembraneV1.scd loads this file and exposes its panel from the
PHASE TIMBRE button.  The backend
owns the tested mapping

    w_j = 2 A_j^2 [1 + depth cos(phase + j spread)]

and publishes revision-matched M1-M20 gain factors.  This panel sends only
downstream mapping controls and displays committed readback.  It never edits
rho, H, geometry, modal frequencies, measurement, or event identity.
*/
(
~qrmOpenInterferenceTimbre = {
var modeCount = 20;
var root = "/qmw/qrm/v1";
var control = ~qrmControl ? NetAddr("127.0.0.1", 17921);
var window, sourceMenu, phaseSlider, spreadSlider, depthSlider, slewSlider;
var rowBox, columnBox, gainView, status, updateFunction;
var fieldColor = Color.fromHexString("080b10");
var textColor = Color.white;
var sendPair;

if(~qrmPushModeMix.isNil) {
    "QMW Interference Timbre: load QuantumResonantMembraneV1.scd first".warn;
};

~qrmInterferenceTimbreWindow !? _.close;
window = Window("QMW INTERFERENCE TIMBRE", Rect(210, 160, 720, 430)).front;
window.background = Color.fromHexString("11151c");
~qrmInterferenceTimbreWindow = window;

StaticText(window, Rect(20, 14, 680, 26))
    .string_("PHASE → INTERFERENCE WEIGHTS → M1-M20 TIMBRE")
    .font_(Font("Helvetica Neue", 17, true))
    .stringColor_(textColor);
StaticText(window, Rect(20, 42, 680, 38))
    .string_("Fixed mode frequencies; power-normalized gains except explicit complete cancellation.")
    .stringColor_(Color.fromHexString("aeb9c8"));

StaticText(window, Rect(20, 88, 100, 22)).string_("phase source").stringColor_(textColor);
sourceMenu = PopUpMenu(window, Rect(122, 86, 190, 25))
    .items_(["manual", "density coherence"])
    .background_(fieldColor).stringColor_(textColor)
    .action_({ |menu|
        control.sendMsg(
            root ++ "/control/interference_source",
            if(menu.value == 0) { "manual" } { "density_coherence" }
        );
    });

StaticText(window, Rect(332, 88, 62, 22)).string_("rho pair").stringColor_(textColor);
rowBox = NumberBox(window, Rect(395, 86, 50, 25)).value_(0).clipLo_(0).clipHi_(3)
    .background_(fieldColor).normalColor_(textColor).typingColor_(textColor);
columnBox = NumberBox(window, Rect(452, 86, 50, 25)).value_(1).clipLo_(0).clipHi_(3)
    .background_(fieldColor).normalColor_(textColor).typingColor_(textColor);
sendPair = {
    var row = rowBox.value.asInteger.clip(0, 3);
    var column = columnBox.value.asInteger.clip(0, 3);
    if(row == column) {
        column = (row + 1) % 4;
        columnBox.value_(column);
    };
    control.sendMsg(root ++ "/control/interference_pair", row, column);
};
rowBox.action_({ sendPair.value });
columnBox.action_({ sendPair.value });

phaseSlider = EZSlider(
    window, Rect(20, 126, 680, 34), "phase rad",
    ControlSpec(-pi, pi, \lin, 0, 0),
    { |view| control.sendMsg(root ++ "/control/interference_phase", view.value) },
    labelWidth: 100, numberWidth: 82, layout: \horz
);
spreadSlider = EZSlider(
    window, Rect(20, 164, 680, 34), "spread rad",
    ControlSpec(-pi, pi, \lin, 0, 0.45),
    { |view| control.sendMsg(root ++ "/control/interference_spread", view.value) },
    labelWidth: 100, numberWidth: 82, layout: \horz
);
depthSlider = EZSlider(
    window, Rect(20, 202, 680, 34), "depth",
    ControlSpec(0, 1, \lin, 0, 0),
    { |view| control.sendMsg(root ++ "/control/interference_depth", view.value) },
    labelWidth: 100, numberWidth: 82, layout: \horz
);
slewSlider = EZSlider(
    window, Rect(20, 240, 680, 34), "slew s",
    ControlSpec(0.005, 2, \exp, 0, 0.08),
    { |view| control.sendMsg(root ++ "/control/interference_slew", view.value) },
    labelWidth: 100, numberWidth: 82, layout: \horz
);
[phaseSlider, spreadSlider, depthSlider, slewSlider].do { |view|
    view.labelView.stringColor_(textColor);
    view.numberView.background_(fieldColor).normalColor_(textColor).typingColor_(textColor);
};

StaticText(window, Rect(20, 286, 680, 22))
    .string_("COMMITTED GAIN FACTORS  /  M1-M20")
    .font_(Font("Helvetica Neue", 13, true)).stringColor_(textColor);
gainView = MultiSliderView(window, Rect(20, 312, 680, 72))
    .size_(modeCount).value_(Array.fill(modeCount, 0.5))
    .elasticMode_(true).gap_(3).isFilled_(true)
    .fillColor_(Color.fromHexString("12cbd1"))
    .strokeColor_(Color.fromHexString("e5fbff"))
    .background_(fieldColor);
status = StaticText(window, Rect(20, 392, 680, 24))
    .string_("neutral / waiting for a revision-matched frame")
    .stringColor_(Color.fromHexString("aeb9c8"));

updateFunction = {
    var gains = ~qrmInterferenceTimbreGains ? Array.fill(modeCount, 1.0);
    {
        gainView.value_(gains.collect { |gain| (gain / 2).clip(0, 1) });
        status.string_("source %  phase %  spread %  depth %  slew % s  %".format(
            ~qrmInterferenceTimbreSource ? "-",
            (~qrmInterferenceTimbrePhase ? 0).round(0.001),
            (~qrmInterferenceTimbreSpread ? 0).round(0.001),
            (~qrmInterferenceTimbreDepth ? 0).round(0.001),
            (~qrmInterferenceTimbreSlew ? 0.08).round(0.001),
            if(~qrmInterferenceTimbreCancellation ? false) {
                "COMPLETE CANCELLATION"
            } {
                "power normalized"
            }
        ));
    }.defer;
};
~qrmInterferenceTimbreUpdated = updateFunction;
updateFunction.value;

window.onClose = {
    if(~qrmInterferenceTimbreUpdated === updateFunction) {
        ~qrmInterferenceTimbreUpdated = nil;
    };
    ~qrmInterferenceTimbreWindow = nil;
};
};
)
