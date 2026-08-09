# QMW Pauli State Instrument v1

**The Complete Address** is the first playable prototype of a larger Pauli
research instrument. It sits conceptually between the existing spin-measurement
engine and the Zeeman Resonator: states are given complete quantum addresses,
occupied under the exclusion rule, and mapped into a strong-field spectral
lattice.

## Open the instrument

1. Regenerate if needed:
   `python3 pauli_state_instrument_v1/build_qmw_pauli_state_instrument_v1.py`
2. Open `QMW_Pauli_State_Instrument_v1.maxpat` in Max 9.
3. Enable `ezdac~`.

The patch opens with the six states of the 2p subshell occupied.

## Three playable studies

### 1. Complete-state ledger

The six buttons represent

```text
(n, l, m_l, m_s) = (2, 1, {-1,0,1}, {-1/2,+1/2}).
```

`fill` occupies the closed subshell. `clear` releases it. After filling, click
`occupy 0`: the ledger reports exclusion and creates no seventh voice. Each
state controls a signed displacement using the perceptually magnified strong-field factor

```text
m_l + 2*m_s.
```

The voice does not place an oscillator directly at the resulting frequency.
It multiplies quadrature carrier and modulator pairs:

```text
lower = cos(fc)cos(fm) + sin(fc)sin(fm) = cos(fc-fm)
upper = cos(fc)cos(fm) - sin(fc)sin(fm) = cos(fc+fm)
```

The sign of the state displacement selects one sideband. Every occupied
address therefore contributes one resolved line while remaining genuinely
ring-modulated; the unmodulated carrier is not mixed into these six voices.

`raw RM blend` exposes the topology directly:

- `0`: quadrature single-sideband mode, preserving one spectral line per state;
- `1`: raw real multiplication `cos(fc)cos(fm)`, retaining both moving
  sidebands so the ring-modulation gesture is unmistakable;
- intermediate values: continuous comparison between analytical line
  resolution and the audible two-sideband product.

The patch now boots at `raw RM blend = 1`.

`FM index` phase-modulates each carrier quadrature with its own state modulator
before the ring product:

```text
carrier phase = 2*pi*fc*t + I*sin(2*pi*fm*t)
```

`I=0` is transparent and preserves the resolved Zeeman/Pauli line mapping.
Increasing `I` grows Bessel-distributed satellites around the ring sidebands.
This is an explicitly creative spectral-expansion parameter, not an additional
atomic quantum number. The patch boots at `FM index = 0`.

The filled shell has a zero sum of magnetic factors even while its microscopic
voices remain active.

### 2. Spinor 4pi return

Sweep rotation from 0 to 720 degrees. The 110 Hz probe is the coherent
interference intensity of the rotated spinor with an unrotated reference. It is
full at 0 degrees, silent after the 2pi sign reversal, and restored only at 4pi.

### 3. Antisymmetric two-fermion norm

Sweep one-particle state overlap from 0 to 1. The 330 Hz probe follows

```text
||a wedge b|| = sqrt(1 - |<a|b>|^2).
```

It vanishes when the normalized one-particle states coincide. This treats
exclusion as a consequence of antisymmetry rather than only as a voice limit.

## Model scope

`pauli_state_model.py` also implements:

- validated uncoupled addresses `(n,l,m_l,m_s)`;
- validated coupled addresses `(n,l,j,m_j)`;
- exact spin-1/2 Clebsch-Gordan expansion between those bases;
- arbitrary-axis spin measurement and collapse;
- the 2pi sign change and 4pi spinor return;
- a one-electron-per-address occupancy ledger;
- the normalized two-state Slater-wedge norm.

The current Max patch sonifies the uncoupled strong-field basis through a
six-voice quadrature single-sideband ring bank. A subsequent
version can use the coupled-basis coefficients to morph into the weak-field
Zeeman ring bank and can receive measurement axes from
`quantum_spin_polarization_engine_v3_measurement_basis.py`.

`pauli_state_instrument_demo.wav` is a 15-second offline audition: closed-shell
field unfolding while FM index grows from 0 to 4, then the 4pi spinor probe,
then the Slater-overlap collapse.

## Thermodynamic continuation

`quantum_statistics_instrument_v1` carries the same antisymmetry law from a
finite state ledger into the ideal-gas thermodynamic limit. Its control
`D = n*lambda_T^3` compares Fermi blocking and degeneracy pressure against Bose
bunching and condensation at the same phase-space density. The Pauli State
Instrument remains the address-level study; the Quantum Statistics Instrument
is the many-particle equation-of-state layer.
