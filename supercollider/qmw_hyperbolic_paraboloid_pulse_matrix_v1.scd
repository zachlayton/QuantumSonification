// QMW -- hyperbolic paraboloid pulse matrix
//
// Sonifies the same saddle surface added to the offline pipeline
// (operators/algebraic_surface_pipeline_v1.py, surface="hyperbolic_paraboloid"):
//
//     z = a * (x^2 - y^2)
//
// as a literal time x pitch matrix instead of an eigenmode spectrum: the
// surface's own x/y grid becomes the piece's grid. Column (x) -> time,
// scanning the saddle left to right over the piece. Row (y) -> pitch, one
// audio partial per row. Height (z) -> per-pulse amplitude, decay, and pan,
// so the saddle's positive lobe (x^2 > y^2) and negative lobe (y^2 > x^2)
// read as distinct loud/short vs. quiet/long, right- vs. left-panned
// pulses, and the near-diagonal ridge where z ~ 0 reads as an audible
// silent "X" carved through the piece -- the saddle's shape made audible.
//
// Interactive use (boot a server first):
//   ~qmwHPPlay.();       // play once, live
//   ~qmwHPStop.();       // stop early
//
// Offline bounce to a 30-second WAV, no live server needed:
//   ~qmwHPRenderNRT.("/absolute/path/out.wav");

(
~qmwHPPrivateBus = 20; // internal stereo mix bus for the NRT bounce path

~qmwHPPulseDef = SynthDef(\qmwHPPulse, { |out=0, freq=220, amp=0.2, decay=0.5, pan=0|
	// Three inharmonic partials, echoing the plate/membrane material models
	// used elsewhere in this project (surface_material_models_v1) rather
	// than a pure sine click.
	var ratios = #[1.0, 2.756, 5.404];
	var gains = #[1.0, 0.55, 0.30];
	var sig = Mix.fill(3, { |i|
		var pFreq = freq * ratios[i];
		var pDecay = (decay * gains[i]).max(0.03);
		var env = EnvGen.kr(
			Env.perc(0.001, pDecay, curve: -4),
			doneAction: if (i == 0) { 2 } { 0 }
		);
		SinOsc.ar(pFreq) * env * gains[i];
	});
	Out.ar(out, Pan2.ar(sig * amp, pan));
});

~qmwHPMasterDef = SynthDef(\qmwHPMaster, { |in=0, out=0|
	Out.ar(out, Limiter.ar(In.ar(in, 2), 0.9));
});

// Builds the (time, freq, amp, decay, pan) pulse list directly from the
// saddle equation -- the single source of geometry both the live and NRT
// paths below play back.
~qmwHPPulses = { |a = 1.0, bound = 3.0, cols = 46, rows = 28, tStart = 0.0,
	tEnd = 26.0, baseFreq = 220.0, freqOctaveRange = 1.5, gateThreshold = 0.10,
	rowStaggerSec = 0.006, ampFloor = 0.05, ampScale = 0.35, decayFloor = 0.25,
	decayScale = 1.8|
	var zMax = a * bound.squared;
	var pulses = List.new;
	cols.do { |c|
		var x = c.linlin(0, cols - 1, bound.neg, bound);
		var time = c.linlin(0, cols - 1, tStart, tEnd);
		rows.do { |r|
			var y = r.linlin(0, rows - 1, bound.neg, bound);
			var z = a * (x.squared - y.squared);
			var ampNorm = (z.abs / zMax).clip(0, 1);
			if (ampNorm > gateThreshold) {
				var freq = baseFreq * (2 ** (z / zMax * freqOctaveRange));
				var amp = ampFloor + (ampScale * ampNorm);
				var decay = decayFloor + (decayScale * ampNorm);
				var pan = (z.sign * ampNorm).clip(-1, 1);
				pulses.add((
					time: time + (r * rowStaggerSec),
					freq: freq, amp: amp, decay: decay, pan: pan
				));
			};
		};
	};
	pulses.asArray.sort({ |aa, bb| aa[\time] < bb[\time] });
};

~qmwHPPlay = { |...args|
	var server = Server.default;
	var pulses = ~qmwHPPulses.valueArray(args);
	var bus = Bus.audio(server, 2);
	var master;
	server.bind {
		~qmwHPPulseDef.add;
		~qmwHPMasterDef.add;
	};
	server.sync;
	master = Synth(\qmwHPMaster, [\in, bus.index, \out, 0]);
	~qmwHPRoutine = Routine {
		var last = 0.0;
		pulses.do { |p|
			(p[\time] - last).max(0).wait;
			last = p[\time];
			Synth.before(master, \qmwHPPulse, [
				\freq, p[\freq], \amp, p[\amp], \decay, p[\decay],
				\pan, p[\pan], \out, bus.index
			]);
		};
		3.0.wait; // let the final decay tails ring before tearing down
		master.free;
		bus.free;
	}.play;
};

~qmwHPStop = {
	~qmwHPRoutine.stop;
	~qmwHPRoutine = nil;
};

~qmwHPRenderNRT = { |path, duration = 30.0, sampleRate = 48000, pulseArgs|
	var pulses = ~qmwHPPulses.valueArray(pulseArgs ? []);
	var bus = ~qmwHPPrivateBus;
	var msgs = [
		[0.0, ['/d_recv', ~qmwHPPulseDef.asBytes]],
		[0.0, ['/d_recv', ~qmwHPMasterDef.asBytes]],
		// A fixed, far-out-of-range node ID: scsynth auto-assigns pulse IDs
		// (from the -1 below) starting at 1000 and counting up, so this stays
		// well clear of collisions with however many pulses get scheduled.
		[0.0, ['/s_new', \qmwHPMaster, 999999, 0, 1, \in, bus, \out, 0]]
	] ++ pulses.collect { |p|
		[p[\time], ['/s_new', \qmwHPPulse, -1, 0, 1,
			\freq, p[\freq], \amp, p[\amp], \decay, p[\decay],
			\pan, p[\pan], \out, bus
		]]
	};
	Score(msgs).recordNRT(
		outputFilePath: path,
		sampleRate: sampleRate,
		headerFormat: "WAV",
		sampleFormat: "int16",
		options: ServerOptions.new,
		duration: duration,
		action: { "qmwHPRenderNRT: wrote %\n".postf(path); }
	);
};
)
