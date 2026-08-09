/*
QMW Floquet Boundary Freeze v1

Evaluate this entire file. It boots the default server, opens a compact
control surface, and starts with the unperturbed topological reference.
*/

(
var here = thisProcess.nowExecutingPath.dirname;
var makeSlider;

(here +/+ "floquet_boundary_freeze_synthdef.scd").load;

s.options.numWireBufs = 512;

s.waitForBoot {
	var window, root, presetRow, freezeRow, status;
	var perturbationSlider, symmetrySlider, edgeRateSlider, driveRateSlider;
	var localizationSlider, ringSlider, diffusionSlider, phaseTurnsSlider;
	var fundamentalSlider, geometrySlider, pitchMotionSlider;
	var envelopeSlider, micromotionSlider;
	var piButton, freezeMenu;

	~makeFloquetBoundaryFreezeDef.value.add;
	s.sync;

	~floquetBoundaryFreeze !? { |old| old.set(\gate, 0) };
	~floquetBoundaryFreeze = Synth(\qmwFloquetBoundaryFreezeV1, [
		\topology, 1,
		\perturbation, 0,
		\symmetryBreak, 0,
		\freezeMode, 2,
		\piMode, 1
	]);

	window = Window("Floquet Boundary Freeze v1.1", Rect(110, 70, 620, 720));
	root = CompositeView(window);
	root.layout = VLayout.new;
	window.layout = VLayout(root);

	root.layout.add(
		StaticText(root)
			.string_("Hear whether a boundary-transfer pattern survives a matched perturbation")
			.align_(\center)
			.font_(Font("Helvetica", 15, true))
	);

	status = StaticText(root)
		.string_("Reference: topological / unperturbed")
		.align_(\center)
		.background_(Color.gray(0.16))
		.stringColor_(Color.white);
	root.layout.add(status);

	makeSlider = { |label, spec, value, parameter|
		var slider = EZSlider(
			root,
			600@28,
			label,
			spec,
			{ |view| ~floquetBoundaryFreeze.set(parameter, view.value) },
			value,
			unitWidth: 46,
			labelWidth: 170
		);
		root.layout.add(slider.view);
		slider;
	};

	presetRow = HLayout(
		Button(root)
			.states_([["Reference", Color.black, Color(0.72, 0.85, 1)]])
			.action_({
				~floquetBoundaryFreeze.set(\topology, 1, \perturbation, 0, \symmetryBreak, 0);
				perturbationSlider.valueAction_(0);
				symmetrySlider.valueAction_(0);
				status.string_("Reference: topological / unperturbed");
			}),
		Button(root)
			.states_([["Protected A", Color.black, Color(0.60, 0.90, 0.67)]])
			.action_({
				~floquetBoundaryFreeze.set(\topology, 1, \perturbation, 0.82, \symmetryBreak, 0);
				perturbationSlider.valueAction_(0.82);
				symmetrySlider.valueAction_(0);
				status.string_("A: strong symmetry-preserving perturbation / transfer survives");
			}),
		Button(root)
			.states_([["Broken B", Color.white, Color(0.72, 0.24, 0.23)]])
			.action_({
				~floquetBoundaryFreeze.set(\topology, 1, \perturbation, 0.82, \symmetryBreak, 1);
				perturbationSlider.valueAction_(0.82);
				symmetrySlider.valueAction_(1);
				status.string_("B: same strength, symmetry-breaking / transfer is destroyed");
			}),
		Button(root)
			.states_([["Trivial control", Color.black, Color(0.82, 0.82, 0.82)]])
			.action_({
				~floquetBoundaryFreeze.set(\topology, 0, \perturbation, 0, \symmetryBreak, 0);
				perturbationSlider.valueAction_(0);
				symmetrySlider.valueAction_(0);
				status.string_("Control: trivial chain / no coherent boundary pattern");
			})
	);
	root.layout.add(presetRow);

	perturbationSlider = makeSlider.(
		"Perturbation strength",
		ControlSpec(0, 1, \lin, 0.01),
		0,
		\perturbation
	);
	symmetrySlider = makeSlider.(
		"Symmetry breaking",
		ControlSpec(0, 1, \lin, 0.01),
		0,
		\symmetryBreak
	);
	edgeRateSlider = makeSlider.(
		"Boundary cycle (Hz)",
		ControlSpec(0.015, 0.4, \exp, 0, 0.09),
		0.16,
		\edgeRate
	);
	driveRateSlider = makeSlider.(
		"Compressed Floquet drive (Hz)",
		ControlSpec(0.08, 5, \exp, 0, 0.72),
		0.72,
		\driveRate
	);
	localizationSlider = makeSlider.(
		"Boundary decay ratio",
		ControlSpec(0.08, 0.95, \lin, 0.01),
		0.43,
		\localizationRatio
	);
	fundamentalSlider = makeSlider.(
		"Fundamental anchor (Hz)",
		ControlSpec(35, 260, \exp, 0, 105),
		105,
		\baseFundamentalHz
	);
	geometrySlider = makeSlider.(
		"Geometry exponent",
		ControlSpec(0.04, 0.35, \lin, 0.005),
		0.18,
		\geometryExponent
	);
	pitchMotionSlider = makeSlider.(
		"Data pitch motion (steps)",
		ControlSpec(0, 8, \lin, 1),
		2,
		\pitchMotionSteps
	);
	envelopeSlider = makeSlider.(
		"Boundary envelope contrast",
		ControlSpec(0.35, 2.5, \lin, 0.05),
		1.15,
		\envelopeCurve
	);
	micromotionSlider = makeSlider.(
		"Floquet amplitude motion",
		ControlSpec(0, 0.85, \lin, 0.01),
		0.28,
		\micromotionDepth
	);
	ringSlider = makeSlider.(
		"Resonator decay (s)",
		ControlSpec(0.08, 6, \exp, 0, 1.6),
		1.6,
		\ringTime
	);
	phaseTurnsSlider = makeSlider.(
		"Boundary phase winding",
		ControlSpec(-1, 1, \lin, 0.01),
		0.18,
		\phaseTurns
	);
	diffusionSlider = makeSlider.(
		"Broken-symmetry diffusion",
		ControlSpec(0, 20, \lin, 0.1),
		7,
		\diffusionRate
	);

	root.layout.add(StaticText(root).string_(
		"Freeze holds resonator magnitudes; phase continues to wind. The pi mode accumulates pi per drive period."
	).align_(\center));

	freezeRow = HLayout(
		StaticText(root).string_("Spectral state").align_(\right),
		freezeMenu = PopUpMenu(root)
			.items_(["Live magnitudes", "Hold current frame", "Stroboscopic refresh"])
			.value_(2)
			.action_({ |menu| ~floquetBoundaryFreeze.set(\freezeMode, menu.value) }),
		Button(root)
			.states_([["Capture + hold"]])
			.action_({
				~floquetBoundaryFreeze.set(\freezeMode, 0);
				AppClock.sched(0.12, {
					~floquetBoundaryFreeze.set(\freezeMode, 1);
					freezeMenu.value_(1);
					nil;
				});
			}),
		piButton = Button(root)
			.states_([
				["Zero mode", Color.black, Color(0.80, 0.84, 0.90)],
				["Pi mode", Color.white, Color(0.36, 0.28, 0.68)]
			])
			.value_(1)
			.action_({ |button| ~floquetBoundaryFreeze.set(\piMode, button.value) })
	);
	root.layout.add(freezeRow);

	root.layout.add(
		Button(root)
			.states_([["Stop", Color.white, Color(0.35, 0.12, 0.12)]])
			.action_({ window.close })
	);

	window.onClose_({
		~floquetBoundaryFreeze !? { |synth| synth.set(\gate, 0) };
		~floquetBoundaryFreeze = nil;
	});
	window.front;
	"Floquet Boundary Freeze v1 ready. Compare Protected A with Broken B.".postln;
};
)
