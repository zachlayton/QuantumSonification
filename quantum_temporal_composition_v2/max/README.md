# QMW Correlation / Differentiation Clock v2 — Max receiver

This receiver has no time generator. There is no `metro`, phasor, `rtt.clock~`, `wrap~`, or `oscparse`. `OSC-route` receives `/qmw/temporal/v2/tick`; Max produces a trigger only when Python says accumulated relational change crossed its quantum.

The green lane displays and sounds correlation ticks. The red lane displays and sounds differentiation ticks. Each has a visible flash and counter. The global relational-time number comes from the engine, not Max.

For the live density-matrix clock, run:

```bash
python quantumsonification_conductor.py --with-correlation-clock \
  --correlation-change-quantum 0.005 --daemon
```

Open the patch and enable DSP. The two small `test tick` buttons test only the audio path; they do not advance the relational counters.

`CHANGE QUANTUM` is the live temporal-resolution control. It sends
`/qmw/temporal/v2/control/change-quantum <value>` through CNMAT
`OpenSoundControl` to UDP 7444. Lower values make smaller relational changes
count as time and therefore produce denser events; higher values require more
accumulated change. The acknowledgement displayed above the control comes back
from `/qmw/temporal/v2/config` on UDP 7442. The control has no effect until the
conductor's correlation bridge is running.

The internal oscillators take pitch directly from each OSC tick. Every tick and every `test tick` button fires a fixed one-shot `line~` envelope, connected directly to the audio output; this makes the audible diagnostic independent of RTT, MIDI parsing, and shared signal buses.

`rtt.makenote~` remains in parallel for sample-accurate MIDI. Its installed inlet contract is: 1 note, 2 velocity, 3 duration, 4 pitch bend, 5 trigger. The OSC tick already carries MIDI velocity in the `0...127` range, so Max only safety-clips it before converting it to a signal. `click~` connects only to inlet 5; it never enters the velocity inlet.
