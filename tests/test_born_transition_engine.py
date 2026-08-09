from __future__ import annotations

import math
from types import SimpleNamespace
import unittest

from excitation.born_transition import (
    BornTransitionEngine,
    HYDROGENIC_SPECIES,
    HYDROGEN_IONIZATION_FREQUENCY_HZ,
    PLANCK_EV_SECONDS,
    QuantumLevel,
    electric_dipole_allowed,
    global_ratio_scale_frequency,
    hydrogen_energy_ev,
    hydrogenic_demo_levels,
    hydrogen_radial_dipole_au,
    octave_fold_frequency,
)


class BornTransitionEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = BornTransitionEngine()

    def test_default_engine_builds_only_allowed_emissions(self) -> None:
        self.assertGreater(len(self.engine.transitions), 0)
        for transition in self.engine.transitions:
            self.assertTrue(
                electric_dipole_allowed(transition.initial, transition.final)
            )
            self.assertGreater(transition.delta_energy_ev, 0.0)
            self.assertEqual(abs(transition.delta_l), 1)
            self.assertLessEqual(abs(transition.delta_m), 1)

    def test_photon_frequency_comes_from_energy_difference(self) -> None:
        for transition in self.engine.transitions:
            expected = transition.delta_energy_ev / PLANCK_EV_SECONDS
            self.assertTrue(
                math.isclose(
                    transition.photon_frequency_hz,
                    expected,
                    rel_tol=1.0e-12,
                )
            )

    def test_event_probabilities_are_normalized(self) -> None:
        total = sum(
            transition.event_probability
            for transition in self.engine.transitions
        )
        self.assertTrue(math.isclose(total, 1.0, abs_tol=1.0e-12))

    def test_branch_probabilities_sum_to_one_per_initial_state(self) -> None:
        initial_labels = {
            transition.initial.label for transition in self.engine.transitions
        }
        for label in initial_labels:
            total = sum(
                transition.branching_probability
                for transition in self.engine.transitions
                if transition.initial.label == label
            )
            self.assertTrue(math.isclose(total, 1.0, abs_tol=1.0e-12))

    def test_spontaneous_rate_includes_frequency_cubed(self) -> None:
        for transition in self.engine.transitions:
            expected = (
                transition.line_strength
                * transition.photon_frequency_hz**3
            )
            self.assertTrue(
                math.isclose(
                    transition.spontaneous_rate_weight,
                    expected,
                    rel_tol=1.0e-12,
                )
            )

    def test_metastable_2s_to_1s_is_forbidden(self) -> None:
        level_2s = QuantumLevel(
            "2s", 2, 0, 0, hydrogen_energy_ev(2), 1.0
        )
        level_1s = QuantumLevel(
            "1s", 1, 0, 0, hydrogen_energy_ev(1), 0.0
        )
        self.assertFalse(electric_dipole_allowed(level_2s, level_1s))

    def test_known_1s_2p_radial_integral_is_reasonable(self) -> None:
        # Analytic magnitude is approximately 1.2903 Bohr radii.
        radial = abs(hydrogen_radial_dipole_au(2, 1, 1, 0))
        self.assertTrue(math.isclose(radial, 1.2903, rel_tol=5.0e-4))

    def test_octave_fold_stays_in_requested_register(self) -> None:
        folded, shift = octave_fold_frequency(2.466e15, 55.0, 1_760.0)
        self.assertGreaterEqual(folded, 55.0)
        self.assertLessEqual(folded, 1_760.0)
        self.assertLess(shift, 0)
        self.assertTrue(
            math.isclose(folded, 2.466e15 * (2.0**shift), rel_tol=1.0e-12)
        )

    def test_global_ratio_mapping_uses_one_fixed_scale(self) -> None:
        expected_scale = 1_760.0 / HYDROGEN_IONIZATION_FREQUENCY_HZ
        for transition in self.engine.transitions:
            self.assertEqual(transition.frequency_mapping, "global_ratio")
            self.assertIsNone(transition.octave_shift)
            self.assertTrue(
                math.isclose(
                    transition.audio_scale_factor,
                    expected_scale,
                    rel_tol=1.0e-12,
                )
            )
            self.assertTrue(
                math.isclose(
                    transition.audio_frequency_hz,
                    transition.photon_frequency_hz * expected_scale,
                    rel_tol=1.0e-12,
                )
            )

    def test_global_ratio_mapping_preserves_harmonic_relationships(self) -> None:
        transition_by_labels = {
            (transition.initial.label, transition.final.label): transition
            for transition in self.engine.transitions
        }
        high = transition_by_labels[("2p0", "1s")]
        low = transition_by_labels[("4s", "2p0")]
        self.assertTrue(
            math.isclose(
                high.photon_frequency_hz / low.photon_frequency_hz,
                4.0,
                rel_tol=1.0e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                high.audio_frequency_hz / low.audio_frequency_hz,
                4.0,
                rel_tol=1.0e-12,
            )
        )

    def test_legacy_octave_fold_remains_available(self) -> None:
        engine = BornTransitionEngine(frequency_mapping="octave_fold")
        self.assertTrue(
            all(
                transition.frequency_mapping == "octave_fold"
                and transition.octave_shift is not None
                for transition in engine.transitions
            )
        )

    def test_isotope_reduced_mass_shift_approaches_infinite_mass_limit(self) -> None:
        frequencies = []
        for species in ("H-1", "H-2", "H-3"):
            engine = BornTransitionEngine(species=species)
            frequencies.append(engine.transitions[0].photon_frequency_hz)
        self.assertLess(frequencies[0], frequencies[1])
        self.assertLess(frequencies[1], frequencies[2])
        self.assertTrue(
            all(key in HYDROGENIC_SPECIES for key in ("H-1", "H-2", "H-3"))
        )

    def test_higher_charge_changes_frequency_and_lifetime_scaling(self) -> None:
        hydrogen = BornTransitionEngine(species="H-1")
        helium = BornTransitionEngine(species="He-4+")
        h_line = hydrogen.transitions[0]
        he_line = helium.transitions[0]
        self.assertTrue(
            math.isclose(
                he_line.photon_frequency_hz / h_line.photon_frequency_hz,
                4.0,
                rel_tol=5.0e-4,
            )
        )
        h_levels = {level.label: level for level in hydrogenic_demo_levels("H-1")}
        he_levels = {level.label: level for level in hydrogenic_demo_levels("He-4+")}
        self.assertTrue(
            math.isclose(
                h_levels["3s"].lifetime_seconds
                / he_levels["3s"].lifetime_seconds,
                16.0,
                rel_tol=1.0e-12,
            )
        )

    def test_radioactivity_is_metadata_not_electronic_decay(self) -> None:
        tritium = BornTransitionEngine(species="H-3")
        self.assertTrue(tritium.state.radioactive)
        self.assertEqual(tritium.state.species, "H-3")
        self.assertEqual(tritium.state.nuclear_charge, 1)

    def test_global_ratio_helper_is_anchored_to_reference(self) -> None:
        audio, scale = global_ratio_scale_frequency(
            HYDROGEN_IONIZATION_FREQUENCY_HZ
        )
        self.assertTrue(math.isclose(audio, 1_760.0, abs_tol=1.0e-12))
        self.assertTrue(
            math.isclose(
                scale,
                1_760.0 / HYDROGEN_IONIZATION_FREQUENCY_HZ,
                rel_tol=1.0e-12,
            )
        )

    def test_step_holds_then_advances_after_sonic_duration(self) -> None:
        engine = BornTransitionEngine()
        initial_index = engine.state.index
        initial_event = engine.state.event_id
        engine.step(engine.state.sonic_duration_seconds * 0.5)
        self.assertEqual(engine.state.index, initial_index)
        self.assertEqual(engine.state.event_id, initial_event)
        engine.step(engine.state.sonic_duration_seconds * 0.5)
        self.assertNotEqual(engine.state.index, initial_index)
        self.assertEqual(engine.state.event_id, initial_event + 1)

    def test_negative_time_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.step(-0.01)

    def test_density_engine_accepts_born_transition_alias(self) -> None:
        from density.density_matrix_engine_4q import DensityMatrixEngine

        engine = object.__new__(DensityMatrixEngine)
        engine.excitation_source_kind = "internal"
        engine.excitation_source = None
        engine.source_descriptor = None
        DensityMatrixEngine.set_excitation_source(engine, "born_transition")
        self.assertIsInstance(engine.excitation_source, BornTransitionEngine)
        self.assertEqual(engine.excitation_source_kind, "born_transition")

    def test_density_engine_can_switch_born_species_live(self) -> None:
        from density.density_matrix_engine_4q import DensityMatrixEngine

        engine = object.__new__(DensityMatrixEngine)
        engine.born_config = {"species": "H-1"}
        DensityMatrixEngine.set_born_species(engine, "He-3+")
        self.assertEqual(engine.excitation_source.species, "He-3+")
        self.assertEqual(engine.born_config["species"], "He-3+")
        self.assertEqual(engine.excitation_source_kind, "born_transition")

    def test_canonical_engine_publishes_one_packet_per_event(self) -> None:
        from quantum_population_osc_v9_resonator import (
            MLXQuantumResonatorEngine,
        )

        class OSCRecorder:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, value) -> None:
                self.messages.append((address, value))

        source = BornTransitionEngine()
        engine = object.__new__(MLXQuantumResonatorEngine)
        engine.density_engine = SimpleNamespace(excitation_source=source)
        engine.osc = OSCRecorder()
        engine.last_born_transition_event_id = None

        self.assertTrue(engine.send_born_transition_frame())
        self.assertFalse(engine.send_born_transition_frame())
        transition_packets = [
            value
            for address, value in engine.osc.messages
            if address == "/qmw/excitation/born/transition"
        ]
        self.assertEqual(len(transition_packets), 1)
        self.assertEqual(transition_packets[0][2], source.state.initial_label)
        self.assertEqual(transition_packets[0][3], source.state.final_label)
        self.assertEqual(
            transition_packets[0][4], source.state.audio_frequency_hz
        )

        source.step(source.state.sonic_duration_seconds)
        self.assertTrue(engine.send_born_transition_frame())
        transition_packets = [
            value
            for address, value in engine.osc.messages
            if address == "/qmw/excitation/born/transition"
        ]
        self.assertEqual(len(transition_packets), 2)

    def test_canonical_engine_publishes_persistent_catalog(self) -> None:
        from quantum_population_osc_v9_resonator import (
            MLXQuantumResonatorEngine,
        )

        class OSCRecorder:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, address, value) -> None:
                self.messages.append((address, value))

        source = BornTransitionEngine(species="H-2")
        engine = object.__new__(MLXQuantumResonatorEngine)
        engine.density_engine = SimpleNamespace(excitation_source=source)
        engine.osc = OSCRecorder()
        engine.last_born_catalog_time = None
        engine.born_catalog_interval = 5.0
        engine.born_catalog_revision = 3

        self.assertTrue(engine.send_born_transition_catalog())
        self.assertFalse(engine.send_born_transition_catalog())
        begin = [v for a, v in engine.osc.messages if a.endswith("/begin")]
        rows = [v for a, v in engine.osc.messages if a.endswith("/row")]
        end = [v for a, v in engine.osc.messages if a.endswith("/end")]
        self.assertEqual(begin[0][:3], [3, len(source.transitions), "H-2"])
        self.assertEqual(len(rows), len(source.transitions))
        self.assertEqual(rows[0][1], "H-2")
        self.assertEqual(end[0], [3, len(source.transitions)])


if __name__ == "__main__":
    unittest.main()
