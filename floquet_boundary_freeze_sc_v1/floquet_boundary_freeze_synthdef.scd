/*
QMW Floquet Boundary Freeze v1 - synthesis definition

The sound follows an effective two-edge Hamiltonian. A symmetry-preserving
perturbation changes common spectral phase without suppressing population
transfer. A symmetry-breaking perturbation detunes the two boundary states,
reduces transfer depth, and progressively diffuses FFT-bin phases.
*/

~makeFloquetBoundaryFreezeDef = {
	var fftSize = 2048;
	var fftHop = 0.5;
	var resonatorDegrees = [0, 1, 2, 3, 5, 7, 9, 12, 15, 18];
	var resonatorCount = resonatorDegrees.size;
	var depths = Array.series(resonatorCount, 0, 1);

	SynthDef(\qmwFloquetBoundaryFreezeV1, {
		|out = 0, amp = 0.24, gate = 1,
		topology = 1, perturbation = 0, symmetryBreak = 0,
		edgeRate = 0.16, driveRate = 0.72, piMode = 1,
		localizationRatio = 0.43, shapeCompression = 0.62,
		baseFundamentalHz = 105, geometryExponent = 0.18, pitchMotionSteps = 2,
		envelopeCurve = 1.15, arrivalAccent = 0.42, micromotionDepth = 0.28,
		ringTime = 1.6, excitationRate = 7.2, excitationDecay = 0.11,
		freezeMode = 2, phaseTurns = 0.18, diffusionRate = 7,
		referenceMix = 0.18, crossfeed = 0.06, bulkLeak = 0.025|

		var topo, breakAmount, perturb, detuneRatio, effectiveRate;
		var transferDepth, rightProbability, leftProbability;
		var shape, shapeEnergy, ratio, excitationEnvelope;
		var geometricRatio, gapScaleIndex, motionScaleIndex, scaleIndex;
		var fundamentalHz, resonatorFrequencies, driveMotion;
		var exciterLeft, exciterRight, bankLeft, bankRight;
		var leftArrivalGate, rightArrivalGate, leftArrival, rightArrival;
		var leftGain, rightGain, leftMicromotion, rightMicromotion;
		var captureWindow, autoFreeze, freezeState;
		var frameRate, stepScale, basePhaseStep, windingStep;
		var phaseStepLeft, phaseStepRight, diffuserFrequency;
		var diffuseTriggerLeft, diffuseTriggerRight;
		var magnitudeChainLeft, magnitudeChainRight;
		var carrierChainLeft, carrierChainRight;
		var phaseChainLeft, phaseChainRight;
		var referenceChainLeft, referenceChainRight;
		var shiftedChainLeft, shiftedChainRight;
		var frozenLeft, frozenRight, referenceLeft, referenceRight;
		var voiceLeft, voiceRight, bulkAmount, bulkSignal, stereo, envelope;
		var phaseCarrierLeft, phaseCarrierRight;

		topo = topology.clip(0, 1);
		perturb = perturbation.clip(0, 1);
		breakAmount = symmetryBreak.clip(0, 1);

		// Effective two-boundary-state dynamics:
		// P_R = [1 / (1 + delta^2)] sin^2(Omega_eff t).
		// The perturbation affects transfer only through its symmetry-breaking part.
		detuneRatio = perturb * breakAmount * 8;
		effectiveRate = edgeRate.max(0.005) * (1 + detuneRatio.squared).sqrt;
		transferDepth = topo / (1 + detuneRatio.squared);
		rightProbability = SinOsc.kr(effectiveRate * 0.5, 0).squared * transferDepth;
		leftProbability = (topo - rightProbability).max(0);
		driveMotion = SinOsc.kr(driveRate.clip(0.01, 20), 0);

		// The resonator index denotes distance from a boundary. This is the
		// compressed amplitude form of an exponentially localized SSH edge state.
		ratio = localizationRatio.clip(0.06, 0.96);

		// The boundary decay ratio generates a geometric pitch scale q = r^-k.
		// Quasienergy splitting chooses its stable scale degree; compressed
		// Floquet micromotion moves locally around that degree.
		geometricRatio = ratio.pow(geometryExponent.clip(0.04, 0.35).neg).clip(1.035, 1.19);
		gapScaleIndex = (
			((effectiveRate / edgeRate.max(0.005)).log / geometricRatio.log)
		).round;
		motionScaleIndex = (driveMotion * pitchMotionSteps.clip(0, 8)).round;
		scaleIndex = gapScaleIndex + motionScaleIndex;
		fundamentalHz = (
			baseFundamentalHz.clip(35, 320) * geometricRatio.pow(scaleIndex)
		).clip(35, 1200).lag(0.065);
		resonatorFrequencies = resonatorDegrees.collect { |degree|
			(fundamentalHz * geometricRatio.pow(degree)).clip(38, 10500);
		};

		shape = depths.collect { |depth|
			ratio.pow(depth * shapeCompression.clip(0.2, 1));
		};
		shapeEnergy = shape.collect { |item| item.squared }.sum.sqrt.max(0.0001);
		shape = shape / shapeEnergy;

		excitationEnvelope = 0.11 + Decay2.kr(
			Impulse.kr(excitationRate.clip(0.1, 40)),
			0.004,
			excitationDecay.clip(0.015, 1.5)
		);
		exciterLeft = HPF.ar(LPF.ar(PinkNoise.ar(0.32), 9000), 55) * excitationEnvelope;
		exciterRight = HPF.ar(LPF.ar(PinkNoise.ar(0.32), 9000), 55) * excitationEnvelope;

		bankLeft = Mix.fill(resonatorCount, { |index|
			Ringz.ar(
				exciterLeft,
				resonatorFrequencies[index],
				ringTime.clip(0.08, 8)
			) * shape[index];
		}) / resonatorCount.sqrt;

		bankRight = Mix.fill(resonatorCount, { |index|
			Ringz.ar(
				exciterRight,
				resonatorFrequencies[index],
				ringTime.clip(0.08, 8)
			) * shape[index];
		}) / resonatorCount.sqrt;

		// Probability remains the source of amplitude motion, but the perceptual
		// display uses a steeper curve than the former square-root law. Edge
		// arrivals receive a short accent, while drive-phase micromotion breathes
		// the two boundary envelopes in opposition.
		leftArrivalGate = leftProbability > (topo * 0.93);
		rightArrivalGate = rightProbability > (transferDepth * 0.93);
		leftArrival = Decay2.kr(HPZ1.kr(leftArrivalGate).max(0), 0.01, 0.42);
		rightArrival = Decay2.kr(HPZ1.kr(rightArrivalGate).max(0), 0.01, 0.42);
		leftMicromotion = (1 + (driveMotion * micromotionDepth.clip(0, 0.85))).max(0);
		rightMicromotion = (1 - (driveMotion * micromotionDepth.clip(0, 0.85))).max(0);
		leftGain = leftProbability.pow(envelopeCurve.clip(0.35, 2.5))
			* leftMicromotion
			* (1 + (leftArrival * arrivalAccent.clip(0, 2)));
		rightGain = rightProbability.pow(envelopeCurve.clip(0.35, 2.5))
			* rightMicromotion
			* (1 + (rightArrival * arrivalAccent.clip(0, 2)));

		// Mode 0: live magnitudes. Mode 1: hold. Mode 2: briefly open once
		// per edge cycle, then capture a new stroboscopic spectral frame.
		captureWindow = Trig1.kr(Impulse.kr(edgeRate.max(0.03)), 0.075);
		autoFreeze = 1 - captureWindow;
		freezeState = Select.kr(freezeMode.clip(0, 2), [0, 1, autoFreeze]);

		// Deterministic broadband carriers replace the stochastic source phase.
		// Frozen resonator magnitudes therefore retain a controllable phase life.
		phaseCarrierLeft = (Saw.ar(37, 0.06) + Pulse.ar(53, 0.37, 0.04));
		phaseCarrierRight = (Saw.ar(41, 0.06) + Pulse.ar(59, 0.43, 0.04));

		magnitudeChainLeft = FFT(LocalBuf(fftSize), bankLeft, hop: fftHop);
		magnitudeChainLeft = PV_MagFreeze(magnitudeChainLeft, freezeState);
		carrierChainLeft = FFT(LocalBuf(fftSize), phaseCarrierLeft, hop: fftHop);
		phaseChainLeft = PV_CopyPhase(magnitudeChainLeft, carrierChainLeft);
		referenceChainLeft = PV_Copy(phaseChainLeft, LocalBuf(fftSize));

		magnitudeChainRight = FFT(LocalBuf(fftSize), bankRight, hop: fftHop);
		magnitudeChainRight = PV_MagFreeze(magnitudeChainRight, freezeState);
		carrierChainRight = FFT(LocalBuf(fftSize), phaseCarrierRight, hop: fftHop);
		phaseChainRight = PV_CopyPhase(magnitudeChainRight, carrierChainRight);
		referenceChainRight = PV_Copy(phaseChainRight, LocalBuf(fftSize));

		// Accumulate exactly pi of additional phase per drive period in pi mode.
		// A quiet unshifted reference makes this otherwise polarity-like motion
		// audible through controlled interference.
		frameRate = SampleRate.ir / (fftSize * fftHop);
		stepScale = driveRate.clip(0.01, 20) / frameRate;
		basePhaseStep = (
			(piMode.clip(0, 1) * pi)
			+ (perturb * (1 - breakAmount) * 0.5pi)
		) * stepScale;
		windingStep = phaseTurns.clip(-2, 2) * 2pi * stepScale;
		phaseStepLeft = basePhaseStep + windingStep;
		phaseStepRight = basePhaseStep - windingStep;

		shiftedChainLeft = PV_PhaseShift(phaseChainLeft, phaseStepLeft, 1);
		shiftedChainRight = PV_PhaseShift(phaseChainRight, phaseStepRight, 1);

		// Symmetry loss is heard as relative-bin phase diffusion rather than as
		// an arbitrary change in loudness or pitch.
		diffuserFrequency = (diffusionRate.clip(0, 30) * perturb * breakAmount);
		diffuseTriggerLeft = Impulse.kr(diffuserFrequency) * (diffuserFrequency > 0.001);
		diffuseTriggerRight = Impulse.kr(diffuserFrequency, 0.5) * (diffuserFrequency > 0.001);
		shiftedChainLeft = PV_Diffuser(shiftedChainLeft, diffuseTriggerLeft);
		shiftedChainRight = PV_Diffuser(shiftedChainRight, diffuseTriggerRight);

		referenceLeft = IFFT(referenceChainLeft);
		referenceRight = IFFT(referenceChainRight);
		frozenLeft = IFFT(shiftedChainLeft);
		frozenRight = IFFT(shiftedChainRight);

		voiceLeft = XFade2.ar(
			frozenLeft,
			referenceLeft,
			(referenceMix.clip(0, 1) * 2) - 1
		) * leftGain;
		voiceRight = XFade2.ar(
			frozenRight,
			referenceRight,
			(referenceMix.clip(0, 1) * 2) - 1
		) * rightGain;

		bulkAmount = (bulkLeak.clip(0, 1) + ((1 - topo) * 0.72)).clip(0, 1);
		bulkSignal = BPF.ar(
			PinkNoise.ar(0.22),
			LFNoise1.kr(0.19).exprange(380, 6200),
			0.42
		) * bulkAmount;

		stereo = [
			voiceLeft + (voiceRight * crossfeed.clip(0, 0.5)) + bulkSignal,
			voiceRight + (voiceLeft * crossfeed.clip(0, 0.5)) + bulkSignal
		];
		envelope = EnvGen.kr(Env.asr(0.08, 1, 1.2), gate, doneAction: 2);
		stereo = Limiter.ar(LeakDC.ar(stereo), 0.88, 0.02) * amp.clip(0, 0.8) * envelope;
		Out.ar(out, stereo);
	});
};
