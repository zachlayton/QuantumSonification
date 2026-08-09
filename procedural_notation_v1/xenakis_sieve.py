"""Small modular pitch sieves in the spirit of Xenakis's sieve theory."""

from __future__ import annotations


# Messiaen's decatonic Mode 7 preserves the previous eight pitch classes while
# adding C-sharp and G-sharp.  Its ordered positions provide stable digit
# identities 0--9 without opening the field to all twelve pitch classes.
DEFAULT_PARENT_PITCH_CLASSES = (0, 1, 2, 3, 4, 6, 7, 8, 9, 10)


def pitch_digit(
    midi_pitch: int,
    parent_pitch_classes: tuple[int, ...] = DEFAULT_PARENT_PITCH_CLASSES,
) -> int:
    """Return the parent-lattice digit (0--9) represented by a MIDI pitch."""
    if len(parent_pitch_classes) != 10:
        raise ValueError("digit mapping requires exactly ten parent pitch classes")
    try:
        return parent_pitch_classes.index(midi_pitch % 12)
    except ValueError as exc:
        raise ValueError("MIDI pitch is outside the ten-class parent lattice") from exc


def modular_pitch_sieve(
    lower_midi: int = 36,
    upper_midi: int = 96,
    residue_shift_7: int = 0,
    residue_shift_9: int = 0,
    parent_pitch_classes: tuple[int, ...] = DEFAULT_PARENT_PITCH_CLASSES,
) -> tuple[int, ...]:
    """Filter a decatonic, digit-addressable pitch lattice with a 7/9 sieve."""
    if (
        isinstance(lower_midi, bool)
        or isinstance(upper_midi, bool)
        or not isinstance(lower_midi, int)
        or not isinstance(upper_midi, int)
        or not 0 <= lower_midi <= upper_midi <= 127
    ):
        raise ValueError("MIDI bounds must be integers satisfying 0 <= lower <= upper <= 127")
    if (
        not parent_pitch_classes
        or len(set(parent_pitch_classes)) != len(parent_pitch_classes)
        or any(
            isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < 12
            for value in parent_pitch_classes
        )
    ):
        raise ValueError("parent_pitch_classes must contain distinct integers from 0 to 11")
    parent_lattice = tuple(
        midi_pitch
        for midi_pitch in range(lower_midi, upper_midi + 1)
        if midi_pitch % 12 in parent_pitch_classes
    )
    pitches = tuple(
        midi_pitch
        for lattice_index, midi_pitch in enumerate(parent_lattice)
        if (
            (lattice_index - residue_shift_7) % 7 in (0, 2)
            or (lattice_index - residue_shift_9) % 9 == 1
        )
    )
    if not pitches:
        raise ValueError("sieve produced no pitches in the requested range")
    return pitches
