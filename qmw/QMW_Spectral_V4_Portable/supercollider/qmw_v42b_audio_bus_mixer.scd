/*
QMW V4.2b post-voice audio-bus mixer
====================================

This is an additive port of the shared stereo FX-send/return architecture in
Quantum_Resonant_Membrane_v1/supercollider/QMWResonantInteractionAddonV1.scd.
It adapts that routing contract to seven real V4.2 sources:

  Simple, Gaussian, Layered, QHO FM, Bloch, Field, Parseval.

Every send and both returns start at exact zero. The existing V4.2 dry buses,
four-output split, event admission, rho, H, and field evolution are unchanged.
MiClouds and VSTPlugin are optional runtime extensions; no third-party source is
copied into QMW and the instrument remains usable when either class is absent.
*/

(
var defineFXSynths, ensureFXGroup, ensureCloudsReturn, ensureVSTReturn;
var scanVSTPlugins, openVSTChooser, openVST, refreshVSTStatus;
var openControls, cleanup, stopReturns, installMainButton, priorStop;
var styleMenu, styleSlider, styleTextField;
var textColor = Color.fromHexString("dcecff");
var mutedTextColor = Color.fromHexString("a9c5dd");
var panelColor = Color.fromHexString("101722");
var fieldColor = Color.fromHexString("18212b");
var mainButton;

// Qt's inherited widget palette can produce dark text on the mixer's dark
// panels (or white-on-white editable number fields) under either macOS
// appearance. Style every editable surface, including both QNumberBox states.
styleMenu = { |menu|
    menu.background_(fieldColor).stringColor_(textColor);
    menu
};
styleSlider = { |slider|
    slider.labelView.stringColor_(textColor);
    slider.numberView
        .normalColor_(textColor)
        .typingColor_(textColor)
        .stringColor_(textColor)
        .background_(fieldColor);
    slider.sliderView.background_(fieldColor);
    slider
};
styleTextField = { |field|
    field.stringColor_(textColor).background_(fieldColor);
    field
};

~qmwQFTV42BFXCleanup !? { |function| function.value };

~qmwQFTV42BFXEnabled = true;
~qmwQFTV42BFXSends = Array.fill(7, { |index|
    ((~qmwQFTV42BFXSends ? [])[index] ? 0.0).asFloat.clip(0, 1)
});
~qmwQFTV42BCloudsReturn = (~qmwQFTV42BCloudsReturn ? 0.0).asFloat.clip(0, 1);
~qmwQFTV42BVSTReturn = (~qmwQFTV42BVSTReturn ? 0.0).asFloat.clip(0, 1);
~qmwQFTV42BVSTBypass = (~qmwQFTV42BVSTBypass ? 0).asInteger.clip(0, 1);
~qmwQFTV42BCloudsPitch = (~qmwQFTV42BCloudsPitch ? 0.0).asFloat.clip(-48, 48);
~qmwQFTV42BCloudsPosition = (~qmwQFTV42BCloudsPosition ? 0.5).asFloat.clip(0, 1);
~qmwQFTV42BCloudsSize = (~qmwQFTV42BCloudsSize ? 0.45).asFloat.clip(0, 1);
~qmwQFTV42BCloudsDensity = (~qmwQFTV42BCloudsDensity ? 0.65).asFloat.clip(0, 1);
~qmwQFTV42BCloudsTexture = (~qmwQFTV42BCloudsTexture ? 0.5).asFloat.clip(0, 1);
~qmwQFTV42BCloudsDryWet = (~qmwQFTV42BCloudsDryWet ? 1.0).asFloat.clip(0, 1);
~qmwQFTV42BCloudsInputGain = (~qmwQFTV42BCloudsInputGain ? 1.0).asFloat.clip(0.125, 8);
~qmwQFTV42BCloudsSpread = (~qmwQFTV42BCloudsSpread ? 0.5).asFloat.clip(0, 1);
~qmwQFTV42BCloudsReverb = (~qmwQFTV42BCloudsReverb ? 0.2).asFloat.clip(0, 1);
~qmwQFTV42BCloudsFeedback = (~qmwQFTV42BCloudsFeedback ? 0.2).asFloat.clip(0, 1);
~qmwQFTV42BCloudsFreeze = (~qmwQFTV42BCloudsFreeze ? 0).asInteger.clip(0, 1);
~qmwQFTV42BCloudsMode = (~qmwQFTV42BCloudsMode ? 0).asInteger.clip(0, 3);
~qmwQFTV42BCloudsLofi = (~qmwQFTV42BCloudsLofi ? 0).asInteger.clip(0, 1);
~qmwQFTV42BMiCloudsAvailable = \MiClouds.asClass.notNil;
~qmwQFTV42BVSTAvailable = \VSTPlugin.asClass.notNil
    and: { \VSTPluginController.asClass.notNil };
~qmwQFTV42BFXGroup = nil;
~qmwQFTV42BFXBaseGroupID = nil;
~qmwQFTV42BCloudsNode = nil;
~qmwQFTV42BVSTNode = nil;
~qmwQFTV42BVSTController = nil;
~qmwQFTV42BVSTControllerDependant = nil;
~qmwQFTV42BVSTLoaded = false;
~qmwQFTV42BVSTPluginKey = ~qmwQFTV42BVSTPluginKey ? nil;
~qmwQFTV42BVSTPresetName = ~qmwQFTV42BVSTPresetName ? "QMW V4.2b";
~qmwQFTV42BVSTLatencySamples = 0;
~qmwQFTV42BVSTPendingOpen = nil;
~qmwQFTV42BVSTAutoScanEnabled = true;
~qmwQFTV42BFXWindow = nil;
~qmwQFTV42BVSTChooserWindow = nil;
~qmwQFTV42BVSTStatus = nil;
~qmwQFTV42BFXCleaning = false;

~qmwQFTV42BUpdateFXSends = {
    ~qmwQFTV42BFXSends = Array.fill(7, { |index|
        (~qmwQFTV42BFXSends[index] ? 0.0).asFloat.clip(0, 1)
    });
    ~qmwQFTV42BFXSendControlBus !? { |bus| bus.setn(~qmwQFTV42BFXSends) };
};

defineFXSynths = {
    var cloudsClass = \MiClouds.asClass;
    var vstClass = \VSTPlugin.asClass;
    ~qmwQFTV42BMiCloudsAvailable = cloudsClass.notNil;
    ~qmwQFTV42BVSTAvailable = vstClass.notNil
        and: { \VSTPluginController.asClass.notNil };

    if(cloudsClass.notNil, {
        SynthDef(\qmwQFTV42BCloudsReturn, {
            |inBus=0, out=0, returnGain=0, pit=0, pos=0.5, size=0.45,
            dens=0.65, tex=0.5, drywet=1, inGain=1, spread=0.5,
            rvb=0.2, fb=0.2, freeze=0, mode=0, lofi=0, trig=0|
            var source = In.ar(inBus, 2);
            var wet = cloudsClass.perform(
                \ar, source, pit.clip(-48, 48), pos.clip(0, 1),
                size.clip(0, 1), dens.clip(0, 1), tex.clip(0, 1),
                drywet.clip(0, 1), inGain.clip(0.125, 8), spread.clip(0, 1),
                rvb.clip(0, 1), fb.clip(0, 1), freeze.clip(0, 1),
                mode.round.clip(0, 3), lofi.clip(0, 1), Trig1.kr(trig, 0.001)
            );
            Out.ar(out, Limiter.ar(
                wet * Lag.kr(returnGain.clip(0, 1), 0.04), 0.78
            ));
        }).add;
    });

    if(vstClass.notNil, {
        SynthDef(\qmwQFTV42BVSTReturn, {
            |inBus=0, out=0, returnGain=0, bypass=0, active=0|
            var source = In.ar(inBus, 2);
            var processed = vstClass.perform(\ar, source, 2, bypass.clip(0, 1));
            var signal = processed * Lag.kr(returnGain.clip(0, 1), 0.04)
                * Lag.kr(active.clip(0, 1), 0.04);
            Out.ar(out, Limiter.ar(signal, 0.78));
        }).add;
    });
};
~qmwQFTV42BDefineFXSynths = defineFXSynths;

refreshVSTStatus = {
    var pluginName = "EMPTY";
    ~qmwQFTV42BVSTController !? { |controller|
        controller.info !? { |info| pluginName = info.name.asString }
    };
    {
        ~qmwQFTV42BVSTStatus !? { |view|
            view.string_("%  /  % samples (% ms)".format(
                pluginName,
                ~qmwQFTV42BVSTLatencySamples,
                ((~qmwQFTV42BVSTLatencySamples
                    / (s.sampleRate ? 48000).max(1)) * 1000).round(0.01)
            ))
        }
    }.defer;
};

ensureCloudsReturn = {
    if(~qmwQFTV42BMiCloudsAvailable
        and: { ~qmwQFTV42BFXGroup.notNil }
        and: { ~qmwQFTV42BFXSendBus.notNil }, {
        if(~qmwQFTV42BCloudsReturn > 0.0001, {
            if(~qmwQFTV42BCloudsNode.isNil
                or: { ~qmwQFTV42BCloudsNode.isPlaying.not }, {
                ~qmwQFTV42BCloudsNode = Synth.tail(
                    ~qmwQFTV42BFXGroup,
                    \qmwQFTV42BCloudsReturn,
                    [\inBus, ~qmwQFTV42BFXSendBus.index, \out, 0]
                ).register;
            });
            ~qmwQFTV42BCloudsNode.set(
                \returnGain, ~qmwQFTV42BCloudsReturn,
                \pit, ~qmwQFTV42BCloudsPitch,
                \pos, ~qmwQFTV42BCloudsPosition,
                \size, ~qmwQFTV42BCloudsSize,
                \dens, ~qmwQFTV42BCloudsDensity,
                \tex, ~qmwQFTV42BCloudsTexture,
                \drywet, ~qmwQFTV42BCloudsDryWet,
                \inGain, ~qmwQFTV42BCloudsInputGain,
                \spread, ~qmwQFTV42BCloudsSpread,
                \rvb, ~qmwQFTV42BCloudsReverb,
                \fb, ~qmwQFTV42BCloudsFeedback,
                \freeze, ~qmwQFTV42BCloudsFreeze,
                \mode, ~qmwQFTV42BCloudsMode,
                \lofi, ~qmwQFTV42BCloudsLofi
            );
        }, {
            ~qmwQFTV42BCloudsNode !? { |node| node.free };
            ~qmwQFTV42BCloudsNode = nil;
        });
    });
};
~qmwQFTV42BUpdateCloudsReturn = ensureCloudsReturn;
~qmwQFTV42BTriggerClouds = {
    ensureCloudsReturn.value;
    ~qmwQFTV42BCloudsNode !? { |node|
        node.set(\trig, 1);
        AppClock.sched(0.02, { node.set(\trig, 0); nil });
    };
};

ensureVSTReturn = {
    var controllerClass = \VSTPluginController.asClass;
    if(~qmwQFTV42BVSTAvailable
        and: { ~qmwQFTV42BFXGroup.notNil }
        and: { ~qmwQFTV42BFXSendBus.notNil }, {
        if(~qmwQFTV42BVSTNode.isNil
            or: { ~qmwQFTV42BVSTNode.isPlaying.not }, {
            var dependant;
            ~qmwQFTV42BVSTNode = Synth.tail(
                ~qmwQFTV42BFXGroup,
                \qmwQFTV42BVSTReturn,
                [
                    \inBus, ~qmwQFTV42BFXSendBus.index, \out, 0,
                    \returnGain, ~qmwQFTV42BVSTReturn,
                    \bypass, ~qmwQFTV42BVSTBypass, \active, 0
                ]
            ).register;
            ~qmwQFTV42BVSTController = controllerClass.perform(
                \new, ~qmwQFTV42BVSTNode
            );
            dependant = { |object, what ...args|
                if(what == \open, {
                    ~qmwQFTV42BVSTLoaded = args[1] ? false;
                    if(~qmwQFTV42BVSTLoaded, {
                        ~qmwQFTV42BVSTPluginKey = object.info.key;
                        ~qmwQFTV42BVSTLatencySamples = object.latency ? 0;
                    });
                    ~qmwQFTV42BVSTNode !? { |node|
                        node.set(\active, ~qmwQFTV42BVSTLoaded.asInteger)
                    };
                    refreshVSTStatus.value;
                });
                if(what == \close or: { what == \crashed } or: { what == \free }, {
                    ~qmwQFTV42BVSTLoaded = false;
                    ~qmwQFTV42BVSTLatencySamples = 0;
                    ~qmwQFTV42BVSTNode !? { |node| node.set(\active, 0) };
                    refreshVSTStatus.value;
                });
                if(what == \close, {
                    ~qmwQFTV42BVSTPendingOpen !? { |pending|
                        ~qmwQFTV42BVSTPendingOpen = nil;
                        AppClock.sched(0.02, { pending.value; nil });
                    };
                });
                if(what == \latency, {
                    ~qmwQFTV42BVSTLatencySamples = (args[0] ? 0).asInteger.max(0);
                    refreshVSTStatus.value;
                });
                if(what == \preset_save or: { what == \preset_load }, {
                    object.preset !? { |preset|
                        ~qmwQFTV42BVSTPresetName = preset.name.asString
                    };
                });
            };
            ~qmwQFTV42BVSTController.latencyChanged = { |samples|
                ~qmwQFTV42BVSTLatencySamples = (samples ? 0).asInteger.max(0);
                refreshVSTStatus.value;
            };
            ~qmwQFTV42BVSTController.addDependant(dependant);
            ~qmwQFTV42BVSTControllerDependant = dependant;
        });
        ~qmwQFTV42BVSTNode.set(
            \returnGain, ~qmwQFTV42BVSTReturn,
            \bypass, ~qmwQFTV42BVSTBypass,
            \active, ~qmwQFTV42BVSTLoaded.asInteger
        );
    });
};
~qmwQFTV42BEnsureVSTReturn = ensureVSTReturn;

scanVSTPlugins = { |statusView, completion|
    var pluginClass = \VSTPlugin.asClass;
    if(pluginClass.isNil, {
        statusView !? { |view| view.string_("VSTPlugin extension unavailable.") };
        completion.value;
    }, {
        if(s.serverRunning.not, {
            statusView !? { |view| view.string_("Start the audio server before scanning VSTs.") };
            completion.value;
        }, {
            statusView !? { |view| view.string_("Scanning default VST paths...") };
            pluginClass.perform(\search, s, nil, nil, true, -1, {
                {
                    var count = pluginClass.perform(\pluginList, s, true).size;
                    statusView !? { |view|
                        view.string_("VST scan complete: % plugins found.".format(count))
                    };
                    completion.value;
                }.defer;
            });
        });
    });
};
~qmwQFTV42BScanVSTPlugins = scanVSTPlugins;

openVST = { |pluginKey|
    var controller, loadPlugin;
    ensureVSTReturn.value;
    controller = ~qmwQFTV42BVSTController;
    if(controller.isNil, {
        "QMW V4.2b VST return is not ready; rebuild or restart audio.".warn;
    }, {
        loadPlugin = {
            {
                ~qmwQFTV42BVSTStatus !? { |view|
                    view.string_("Loading %...".format(pluginKey))
                }
            }.defer;
            controller.perform(\open, pluginKey.asString, true, true,
                { |self, success|
                    {
                        if(success, {
                            ~qmwQFTV42BVSTPluginKey = self.info.key;
                            ~qmwQFTV42BVSTLoaded = true;
                            ~qmwQFTV42BVSTNode.set(\active, 1);
                            refreshVSTStatus.value;
                        }, {
                            ~qmwQFTV42BVSTStatus !? { |view|
                                view.string_("Could not load %. See the post window."
                                    .format(pluginKey))
                            };
                        });
                    }.defer;
                });
        };
        if(controller.info.notNil, {
            ~qmwQFTV42BVSTPendingOpen = loadPlugin;
            controller.perform(\close);
        }, {
            loadPlugin.value;
        });
    });
};
~qmwQFTV42BOpenVST = openVST;

openVSTChooser = {
    var window, listView, filterField, statusView;
    var plugins = [], visiblePlugins = [];
    var refreshList, chooseSelection, pluginClass = \VSTPlugin.asClass;
    if(pluginClass.isNil, {
        "VSTPlugin extension is unavailable in this sclang session.".warn;
    }, {
        ensureVSTReturn.value;
        ~qmwQFTV42BVSTChooserWindow !? { |view| view.close };
        window = Window("QMW V4.2b VST selector", Rect(190, 80, 700, 570))
            .front.alwaysOnTop_(true).background_(panelColor);
        ~qmwQFTV42BVSTChooserWindow = window;
        StaticText(window, Rect(16, 12, 668, 26))
            .string_("SELECT A VST EFFECT FOR THE SHARED 4.2b SEND")
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(textColor);
        StaticText(window, Rect(16, 42, 78, 26)).string_("Filter")
            .stringColor_(mutedTextColor);
        filterField = styleTextField.(
            TextField(window, Rect(94, 42, 410, 28)).string_("")
        );
        Button(window, Rect(514, 42, 80, 28))
            .states_([["FILTER", textColor, Color.fromHexString("263241")]])
            .action_({ refreshList.value });
        Button(window, Rect(604, 42, 80, 28))
            .states_([["CLEAR", textColor, Color.fromHexString("263241")]])
            .action_({ filterField.string_(""); refreshList.value });
        listView = ListView(window, Rect(16, 82, 668, 388))
            .background_(fieldColor).stringColor_(textColor);
        statusView = StaticText(window, Rect(16, 480, 668, 26))
            .stringColor_(mutedTextColor);
        refreshList = {
            var needle = filterField.string.asString.toLower;
            plugins = pluginClass.perform(\pluginList, s, true)
                .select { |info| info.synth.not };
            visiblePlugins = plugins.select { |info|
                var searchable = "% % %".format(
                    info.name ? "Unnamed", info.vendor ? "Unknown", info.key
                ).toLower;
                needle.isEmpty or: { searchable.find(needle).notNil }
            };
            listView.items_(visiblePlugins.collect { |info|
                "%  —  %".format(
                    info.name ? info.key, info.vendor ? "Unknown vendor"
                )
            });
            listView.value_(0);
            statusView.string_(if(visiblePlugins.isEmpty, {
                "No scanned VST effects match. Press RESCAN DEFAULT PATHS."
            }, {
                "% effects available.".format(visiblePlugins.size)
            }));
        };
        chooseSelection = {
            if(visiblePlugins.isEmpty, {
                statusView.string_("No effect is selected.")
            }, {
                openVST.(visiblePlugins[
                    listView.value.clip(0, visiblePlugins.size - 1)
                ].key);
                window.close;
            });
        };
        filterField.action_({ refreshList.value });
        listView.enterKeyAction_({ chooseSelection.value });
        Button(window, Rect(16, 518, 216, 34))
            .states_([["RESCAN DEFAULT PATHS", textColor, Color.fromHexString("263241")]])
            .action_({ scanVSTPlugins.(statusView, refreshList) });
        Button(window, Rect(444, 518, 154, 34))
            .states_([["LOAD SELECTED", Color.black, Color.fromHexString("80ed99")]])
            .action_({ chooseSelection.value });
        Button(window, Rect(608, 518, 76, 34))
            .states_([["CANCEL", textColor, Color.fromHexString("532b35")]])
            .action_({ window.close });
        window.onClose = {
            if(~qmwQFTV42BVSTChooserWindow === window) {
                ~qmwQFTV42BVSTChooserWindow = nil
            }
        };
        refreshList.value;
        if((~qmwQFTV42BVSTAutoScanEnabled ? true)
            and: { plugins.isEmpty } and: { s.serverRunning }, {
            scanVSTPlugins.(statusView, refreshList)
        });
    });
};
~qmwQFTV42BOpenVSTChooser = openVSTChooser;

stopReturns = {
    ~qmwQFTV42BVSTChooserWindow !? { |window| window.close };
    ~qmwQFTV42BVSTChooserWindow = nil;
    ~qmwQFTV42BCloudsNode !? { |node| node.free };
    ~qmwQFTV42BCloudsNode = nil;
    ~qmwQFTV42BVSTController !? { |controller|
        ~qmwQFTV42BVSTControllerDependant !? { |dependant|
            controller.removeDependant(dependant)
        };
        controller.perform(\close);
    };
    ~qmwQFTV42BVSTNode !? { |node| node.free };
    ~qmwQFTV42BVSTNode = nil;
    ~qmwQFTV42BVSTController = nil;
    ~qmwQFTV42BVSTControllerDependant = nil;
    ~qmwQFTV42BVSTPendingOpen = nil;
    ~qmwQFTV42BVSTLoaded = false;
    ~qmwQFTV42BVSTLatencySamples = 0;
};

ensureFXGroup = {
    var baseGroupID;
    if(s.serverRunning and: { ~qmwQFTV3AudioReady ? false }
        and: { ~qmwQFTV3FXGroup.notNil }
        and: { ~qmwQFTV42BFXSendBus.notNil }
        and: { ~qmwQFTV42BFXSendControlBus.notNil }, {
        baseGroupID = ~qmwQFTV3FXGroup.nodeID;
        if(~qmwQFTV42BFXGroup.isNil
            or: { ~qmwQFTV42BFXBaseGroupID != baseGroupID }, {
            stopReturns.value;
            ~qmwQFTV42BFXGroup !? { |group| group.freeAll; group.free };
            defineFXSynths.value;
            s.sync;
            ~qmwQFTV42BFXGroup = Group.after(~qmwQFTV3FXGroup).register;
            ~qmwQFTV42BFXBaseGroupID = baseGroupID;
            s.sync;
        });
        ~qmwQFTV42BUpdateFXSends.();
        ensureCloudsReturn.value;
        if(~qmwQFTV42BVSTController.notNil, { ensureVSTReturn.value });
    }, {
        ~qmwQFTV42BFXGroup = nil;
        ~qmwQFTV42BFXBaseGroupID = nil;
        ~qmwQFTV42BCloudsNode = nil;
        ~qmwQFTV42BVSTNode = nil;
        ~qmwQFTV42BVSTController = nil;
        ~qmwQFTV42BVSTLoaded = false;
    });
};

openControls = {
    var sendSliders, cloudsSetter, presetField;
    if(~qmwQFTV42BFXWindow.notNil, {
        ~qmwQFTV42BFXWindow.front
    }, {
        ensureFXGroup.value;
        ~qmwQFTV42BFXWindow = Window(
            "QMW V4.2b Audio Bus Mixer", Rect(90, 24, 1060, 790)
        ).front.background_(panelColor);
        StaticText(~qmwQFTV42BFXWindow, Rect(16, 12, 1028, 26))
            .string_("V4.2b POST-VOICE SEND MIXER  /  PARALLEL MICLOUDS + VST RETURNS")
            .font_(Font("Helvetica Neue", 14, true)).stringColor_(textColor);
        StaticText(~qmwQFTV42BFXWindow, Rect(16, 42, 1028, 38))
            .string_("Seven audible 4.2 sources feed one shared stereo send bus. Dry routing stays intact; every send and both returns begin at zero.")
            .stringColor_(mutedTextColor);

        StaticText(~qmwQFTV42BFXWindow, Rect(16, 88, 474, 22))
            .string_("SOURCE -> SHARED FX BUS  /  POST-FADER SENDS")
            .stringColor_(Color.fromHexString("8ecae6"));
        sendSliders = Array.fill(7, { |index|
            styleSlider.(EZSlider(
                ~qmwQFTV42BFXWindow,
                Rect(16, 116 + (index * 38), 474, 30),
                ~qmwQFTV42BFXSourceNames[index],
                ControlSpec(0, 1, \lin, 0.001),
                { |view|
                    ~qmwQFTV42BFXSends[index] = view.value;
                    ~qmwQFTV42BUpdateFXSends.();
                },
                ~qmwQFTV42BFXSends[index],
                labelWidth: 86, numberWidth: 56
            ))
        });
        Button(~qmwQFTV42BFXWindow, Rect(16, 390, 474, 30))
            .states_([["ZERO ALL SENDS", textColor, Color.fromHexString("532b35")]])
            .action_({
                ~qmwQFTV42BFXSends = Array.fill(7, 0.0);
                ~qmwQFTV42BUpdateFXSends.();
                sendSliders.do { |slider| slider.value_(0) };
            });
        StaticText(~qmwQFTV42BFXWindow, Rect(16, 430, 474, 92))
            .string_("These are audio-routing controls only. Pluck sends follow their voice faders; Bloch follows its fifth-channel fader; Field and Parseval follow their own audible gains.")
            .stringColor_(Color.fromHexString("ffcf70"));

        cloudsSetter = { ensureCloudsReturn.value };
        StaticText(~qmwQFTV42BFXWindow, Rect(516, 88, 528, 22))
            .string_(if(~qmwQFTV42BMiCloudsAvailable, {
                "MICLOUDS RETURN  /  INSTALLED"
            }, { "MICLOUDS RETURN  /  UNAVAILABLE" }))
            .stringColor_(if(~qmwQFTV42BMiCloudsAvailable, {
                Color.fromHexString("80ed99")
            }, { Color.fromHexString("ffd166") }));
        styleSlider.(EZSlider(~qmwQFTV42BFXWindow, Rect(516, 116, 252, 28), "return",
            ControlSpec(0, 1, \lin, 0.001), { |view|
                ~qmwQFTV42BCloudsReturn = view.value; cloudsSetter.value
            }, ~qmwQFTV42BCloudsReturn, labelWidth: 72, numberWidth: 48));
        styleSlider.(EZSlider(~qmwQFTV42BFXWindow, Rect(780, 116, 264, 28), "pitch",
            ControlSpec(-48, 48, \lin, 0.01), { |view|
                ~qmwQFTV42BCloudsPitch = view.value; cloudsSetter.value
            }, ~qmwQFTV42BCloudsPitch, labelWidth: 72, numberWidth: 48));
        [
            ["position", \qmwQFTV42BCloudsPosition, 150, 516],
            ["size", \qmwQFTV42BCloudsSize, 150, 780],
            ["density", \qmwQFTV42BCloudsDensity, 184, 516],
            ["texture", \qmwQFTV42BCloudsTexture, 184, 780],
            ["dry / wet", \qmwQFTV42BCloudsDryWet, 218, 516],
            ["spread", \qmwQFTV42BCloudsSpread, 218, 780],
            ["reverb", \qmwQFTV42BCloudsReverb, 252, 516],
            ["feedback", \qmwQFTV42BCloudsFeedback, 252, 780]
        ].do { |spec|
            styleSlider.(EZSlider(
                ~qmwQFTV42BFXWindow, Rect(spec[3], spec[2], 264, 28), spec[0],
                ControlSpec(0, 1, \lin, 0.001), { |view|
                    currentEnvironment.put(spec[1], view.value);
                    cloudsSetter.value;
                }, currentEnvironment.at(spec[1]), labelWidth: 72, numberWidth: 48
            ));
        };
        styleSlider.(EZSlider(~qmwQFTV42BFXWindow, Rect(516, 286, 264, 28), "input gain",
            ControlSpec(0.125, 8, \exp, 0.001), { |view|
                ~qmwQFTV42BCloudsInputGain = view.value; cloudsSetter.value
            }, ~qmwQFTV42BCloudsInputGain, labelWidth: 72, numberWidth: 48));
        Button(~qmwQFTV42BFXWindow, Rect(792, 286, 120, 28)).states_([
            ["LIVE", textColor, Color.fromHexString("263241")],
            ["FREEZE", Color.fromHexString("ffd166"), Color.fromHexString("532b35")]
        ]).value_(~qmwQFTV42BCloudsFreeze).action_({ |button|
            ~qmwQFTV42BCloudsFreeze = button.value; cloudsSetter.value
        });
        Button(~qmwQFTV42BFXWindow, Rect(924, 286, 120, 28)).states_([
            ["HI-FI", textColor, Color.fromHexString("263241")],
            ["LO-FI", Color.fromHexString("ffd166"), Color.fromHexString("532b35")]
        ]).value_(~qmwQFTV42BCloudsLofi).action_({ |button|
            ~qmwQFTV42BCloudsLofi = button.value; cloudsSetter.value
        });
        styleMenu.(PopUpMenu(~qmwQFTV42BFXWindow, Rect(516, 324, 252, 28)))
            .items_(["Granular", "Stretch", "Loop delay", "Spectral"])
            .value_(~qmwQFTV42BCloudsMode).action_({ |menu|
                ~qmwQFTV42BCloudsMode = menu.value; cloudsSetter.value
            });
        Button(~qmwQFTV42BFXWindow, Rect(780, 324, 264, 28))
            .states_([["TRIGGER CLOUDS BUFFER", Color.black, Color.fromHexString("80ed99")]])
            .enabled_(~qmwQFTV42BMiCloudsAvailable)
            .action_({ ~qmwQFTV42BTriggerClouds.() });
        StaticText(~qmwQFTV42BFXWindow, Rect(516, 362, 528, 62))
            .string_("Complete MiClouds surface: pit, pos, size, dens, tex, drywet, input gain, spread, reverb, feedback, freeze, mode, lofi, and trigger.")
            .stringColor_(mutedTextColor);

        StaticText(~qmwQFTV42BFXWindow, Rect(16, 548, 1028, 22))
            .string_(if(~qmwQFTV42BVSTAvailable, {
                "VST EFFECT RETURN  /  HOST READY"
            }, { "VST EFFECT RETURN  /  VSTPLUGIN UNAVAILABLE" }))
            .stringColor_(if(~qmwQFTV42BVSTAvailable, {
                Color.fromHexString("80ed99")
            }, { Color.fromHexString("ffd166") }));
        styleSlider.(EZSlider(~qmwQFTV42BFXWindow, Rect(16, 578, 300, 30), "VST return",
            ControlSpec(0, 1, \lin, 0.001), { |view|
                ~qmwQFTV42BVSTReturn = view.value;
                ensureVSTReturn.value;
            }, ~qmwQFTV42BVSTReturn, labelWidth: 90, numberWidth: 52));
        Button(~qmwQFTV42BFXWindow, Rect(328, 578, 110, 30)).states_([
            ["LIVE", textColor, Color.fromHexString("263241")],
            ["BYPASS", Color.fromHexString("ffd166"), Color.fromHexString("532b35")]
        ]).value_(~qmwQFTV42BVSTBypass).enabled_(~qmwQFTV42BVSTAvailable)
            .action_({ |button|
                ~qmwQFTV42BVSTBypass = button.value; ensureVSTReturn.value
            });
        Button(~qmwQFTV42BFXWindow, Rect(450, 578, 122, 30))
            .states_([["SELECT VST", Color.black, Color.fromHexString("80ed99")]])
            .enabled_(~qmwQFTV42BVSTAvailable).action_({ openVSTChooser.value });
        Button(~qmwQFTV42BFXWindow, Rect(584, 578, 92, 30))
            .states_([["EDITOR", textColor, Color.fromHexString("263241")]])
            .enabled_(~qmwQFTV42BVSTAvailable).action_({
                ~qmwQFTV42BVSTController !? { |controller| controller.perform(\editor) }
            });
        Button(~qmwQFTV42BFXWindow, Rect(688, 578, 92, 30))
            .states_([["GUI", textColor, Color.fromHexString("263241")]])
            .enabled_(~qmwQFTV42BVSTAvailable).action_({
                ~qmwQFTV42BVSTController !? { |controller| controller.perform(\gui) }
            });
        Button(~qmwQFTV42BFXWindow, Rect(792, 578, 92, 30))
            .states_([["CLOSE", textColor, Color.fromHexString("532b35")]])
            .enabled_(~qmwQFTV42BVSTAvailable).action_({
                ~qmwQFTV42BVSTController !? { |controller| controller.perform(\close) }
            });
        Button(~qmwQFTV42BFXWindow, Rect(896, 578, 148, 30))
            .states_([["SCAN VST PATHS", textColor, Color.fromHexString("263241")]])
            .enabled_(~qmwQFTV42BVSTAvailable).action_({
                scanVSTPlugins.(~qmwQFTV42BVSTStatus, { refreshVSTStatus.value })
            });
        ~qmwQFTV42BVSTStatus = StaticText(
            ~qmwQFTV42BFXWindow, Rect(16, 616, 500, 30)
        ).stringColor_(mutedTextColor);
        presetField = styleTextField.(
            TextField(~qmwQFTV42BFXWindow, Rect(528, 616, 250, 30))
                .string_(~qmwQFTV42BVSTPresetName.asString)
        );
        Button(~qmwQFTV42BFXWindow, Rect(790, 616, 120, 30))
            .states_([["STORE PRESET", textColor, Color.fromHexString("263241")]])
            .enabled_(~qmwQFTV42BVSTAvailable).action_({
                var name = presetField.string.stripWhiteSpace;
                ~qmwQFTV42BVSTController !? { |controller|
                    if(controller.info.notNil and: { name.notEmpty }, {
                        ~qmwQFTV42BVSTPresetName = name;
                        controller.perform(\savePreset, name)
                    });
                };
            });
        Button(~qmwQFTV42BFXWindow, Rect(922, 616, 122, 30))
            .states_([["RECALL", textColor, Color.fromHexString("263241")]])
            .enabled_(~qmwQFTV42BVSTAvailable).action_({
                var name = presetField.string.stripWhiteSpace;
                ~qmwQFTV42BVSTController !? { |controller|
                    if(controller.info.notNil and: { name.notEmpty }, {
                        ~qmwQFTV42BVSTPresetName = name;
                        controller.perform(\loadPreset, name)
                    });
                };
            });
        refreshVSTStatus.value;

        StaticText(~qmwQFTV42BFXWindow, Rect(16, 676, 1028, 42))
            .string_("Returns are parallel and land on hardware outputs 1–2. The established dry stems remain plucks/Bloch on 1–2 and field/Parseval on 3–4.")
            .stringColor_(Color.fromHexString("8ecae6"));
        StaticText(~qmwQFTV42BFXWindow, Rect(16, 724, 1028, 48))
            .string_("This mixer is downstream sound design. It cannot change rho, H, the Python clock, field evolution, event admission, or the Sophie Germain visualization contract.")
            .stringColor_(Color.fromHexString("ffcf70"));
        ~qmwQFTV42BFXWindow.onClose = {
            ~qmwQFTV42BFXWindow = nil;
            ~qmwQFTV42BVSTStatus = nil;
        };
    });
};
~qmwQFTV42BOpenFXMixer = openControls;

installMainButton = Routine({
    while({ ~qmwQFTV3Window.isNil }, { 0.1.wait });
    {
        mainButton = Button(~qmwQFTV3Window, Rect(730, 2770, 360, 30))
            .states_([[
                "4.2b AUDIO BUS MIXER  /  Clouds + VST",
                Color.black, Color.fromHexString("80ed99")
            ]])
            .action_({ openControls.value });
    }.defer;
}).play(AppClock);

~qmwQFTV42BFXRoutine = Routine({
    inf.do {
        ensureFXGroup.value;
        0.25.wait;
    }
}).play(AppClock);

cleanup = {
    if(~qmwQFTV42BFXCleaning.not, {
        ~qmwQFTV42BFXCleaning = true;
        ~qmwQFTV42BFXRoutine !? { |routine| routine.stop };
        installMainButton !? { |routine| routine.stop };
        ~qmwQFTV42BFXWindow !? { |window| window.close };
        ~qmwQFTV42BFXWindow = nil;
        stopReturns.value;
        ~qmwQFTV42BFXGroup !? { |group| group.freeAll; group.free };
        ~qmwQFTV42BFXGroup = nil;
        ~qmwQFTV42BFXBaseGroupID = nil;
    });
};
~qmwQFTV42BFXCleanup = cleanup;

priorStop = ~qmwQFTV3Stop;
~qmwQFTV3Stop = {
    cleanup.value;
    priorStop.value;
};

"QMW V4.2b audio-bus mixer ready: seven sends + optional Clouds/VST; all zero by default."
    .postln;
)
