# QMW Hilbert Coherence Voice v1

This Max test patch turns a real audio signal into an analytic signal and multiplies it by a complex quantum-coherence value.

## Signal model

`hilbert~` supplies the matched quadrature pair

\[
z(t)=I(t)+iQ(t).
\]

The two smoothed coherence controls define

\[
c(t)=a(t)+ib(t).
\]

The patch calculates the complete complex product:

\[
z(t)c(t)=(Ia-Qb)+i(Ib+Qa).
\]

The first two outlets therefore carry:

1. coherence real: `I*a - Q*b`
2. coherence imaginary: `I*b + Q*a`

The third outlet carries the currently selected audition signal before the master gain and safety clipper.

## Quick start

1. Open `qmw_hilbert_coherence_voice_v1.maxpat` in Max.
2. Click `ezdac~` to enable audio.
3. Leave `source` at `1` to use the internal 110 Hz sine test signal. Set it to `2` for the harmonic-geometry source or `3` when feeding audio into the patcher's signal inlet.
4. Click the complex-number preset messages or edit coherence `a` and `b` directly.
5. Use `output` to choose:
   - `1`: coherence real
   - `2`: coherence imaginary
   - `3`: nominal positive single-sideband shift
   - `4`: nominal negative single-sideband shift
6. For modes `3` and `4`, set `shift Hz` above zero. Try `5`, `20`, `55`, or `110` Hz.

The patch initializes safely with source gain `0.5`, coherence `1 + 0i`, output mode `1`, shift `0 Hz`, and master `0.3`. The DAC remains off until clicked.

## What to listen for

A constant unit-magnitude coherence value rotates phase. With a steady sine wave, that rotation changes phase without necessarily changing the perceived pitch or timbre. The deeper musical behavior appears when `a(t)` and `b(t)` evolve, when the signal contains multiple partials, or when the complex operation is placed inside a resonant feedback path.

The SSB modes provide a more immediately audible verification of the analytic pair. They multiply `I+iQ` by a rotating complex carrier and retain one translation direction while suppressing the mirror sideband.

## Hilbert geometry

The two scopes plot the Hilbert components directly against one another:

- cyan: the original analytic trajectory `(I,Q)`
- orange: the trajectory after multiplication by quantum coherence `(Ia-Qb, Ib+Qa)`

Select source `2` to generate

\[
x(t)=\cos(\omega t)+A\cos(n\omega t).
\]

Its analytic trajectory is approximately

\[
z(t)=e^{i\omega t}+Ae^{in\omega t}.
\]

This converts harmonic number into rotational winding. At the cusp condition `A = 1/n`, the curve has `n-1` cusps: `n=4, A=0.25` produces a three-cusp, triangle-like figure; `n=6, A=0.1667` produces a five-cusp figure. Raising `A` beyond `1/n` opens loops and produces stellar rosettes. The included messages provide three-cusp, five-cusp, looped fivefold, and sevenfold starting points.

The orange scope makes the quantum action geometrically explicit. Unit-magnitude coherence rotates the complete figure; coherence magnitude contracts or expands it; time-varying coherence moves the geometry through a dynamically changing complex transformation.

## Quantum mappings

Good first mappings are:

- Bloch `x -> a` and Bloch `y -> b`
- density-matrix `Re(rho_ij) -> a` and `Im(rho_ij) -> b`
- coherence phasor `alpha*conj(beta) -> a+ib`
- coherence magnitude `|rho_ij| -> |c|`
- coherence phase `arg(rho_ij) -> arg(c)`

The patch smooths both components over 25 ms. Values with magnitude greater than one add gain, so retain the master control and safety clipper while testing live quantum streams.

## Resonator integration

For the next version, insert the analytic conversion and complex multiplication inside each resonator branch:

`excitation -> resonator mode -> hilbert~ -> complex coherence multiplication -> feedback/sum`

This placement lets imaginary coherence rotate and couple the resonant state itself, rather than modulating a parallel noise or oscillator layer.
