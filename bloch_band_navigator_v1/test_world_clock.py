import json
import unittest
from pathlib import Path
import numpy as np

from .model import BlochLattice1D
from .osc_spectral_microscope import state_packet
from .temporal_entanglement import clock_coordinates, parallel_transport
from .quench_events import (
    LatticeQuench, departure_minimum, event_packet, state_novelty, transfer_peak,
)


class WorldClockTests(unittest.TestCase):
    def test_lattice_hamiltonian_and_state(self):
        model = BlochLattice1D()
        np.testing.assert_allclose(model.hamiltonian(0.2), model.hamiltonian(0.2).T)
        state = model.state(0.25)
        self.assertAlmostEqual(float(np.vdot(state.coefficients, state.coefficients).real), 1.0)
        self.assertEqual(len(state_packet(state)), 24)

    def test_band_is_even_and_gap_opens(self):
        model = BlochLattice1D()
        self.assertAlmostEqual(model.state(-0.3).energy, model.state(0.3).energy, places=10)
        energies, _ = model.eigensystem(0.5)
        self.assertGreater(float(energies[1] - energies[0]), 1.0)

    def test_gen_has_four_complex_outputs_and_negative_time_phase(self):
        root = Path(__file__).parent / "max"
        patch = json.loads((root / "qmw_bloch_band_resonator.gendsp").read_text())
        box = next(x["box"] for x in patch["patcher"]["boxes"] if x["box"].get("id") == "code")
        self.assertEqual(box["numoutlets"], 4)
        self.assertIn("penergy-max(20", box["code"])
        for token in ("out1=tanh(u*", "out2=tanh(ui*", "out3=tanh(psi*", "out4=tanh(psii*"):
            self.assertIn(token, box["code"])

    def test_hilbert_ab_and_spat_cardinals(self):
        root = Path(__file__).parent / "max"
        main = json.loads((root / "QMW_Pauli_Bloch_World_Clock_Spat_v1.maxpat").read_text())
        text = "\n".join(x["box"].get("text", "") for x in main["patcher"]["boxes"])
        self.assertIn("hilbert~", text)
        self.assertIn("qmw_bloch_complex_spat5_hoa3~", text)
        spatial = json.loads((root / "qmw_bloch_complex_spat5_hoa3~.maxpat").read_text())
        text = "\n".join(x["box"].get("text", "") for x in spatial["patcher"]["boxes"])
        for token in ("/source/1/aed 90 0 1", "/source/2/aed -90 0 1", "/source/3/aed 0 0 1", "/source/4/aed 180 0 1", "/panning/type hoa3d, /norm SN3D"):
            self.assertIn(token, text)

    def test_temporal_entanglement_is_bounded_and_phase_continuous(self):
        samples = [clock_coordinates(t) for t in np.linspace(0.0, 100.0, 401)]
        self.assertTrue(all(-0.5 <= sample.q <= 0.5 for sample in samples))
        self.assertTrue(all(sample.depth > 0.0 for sample in samples))

        model = BlochLattice1D(samples[20].depth)
        first = model.state(samples[20].q)
        inverted = type(first)(
            first.q, first.band, first.energy, -first.coefficients
        )
        aligned = parallel_transport(inverted, first.coefficients)
        self.assertGreater(float(np.vdot(first.coefficients, aligned.coefficients).real), 0.99)

    def test_quench_is_unitary_and_events_come_from_extrema(self):
        quench = LatticeQuench(initial_width=0.0)
        frames = [quench.frame(t) for t in (0.31, 0.32, 0.33)]
        for frame in frames:
            self.assertAlmostEqual(float(np.sum(frame.populations)), 1.0, places=10)
        self.assertTrue(transfer_peak(*frames, threshold=0.1))
        self.assertEqual(len(event_packet(1, 0, frames[1])), 40)

        departure = [quench.frame(t) for t in (0.72, 0.735, 0.75)]
        self.assertTrue(departure_minimum(*departure, threshold=0.8))

        broad = LatticeQuench()
        spectral_weights = np.abs(
            broad.eigenvectors.conj().T @ broad.initial
        ) ** 2
        spectral_participation = 1.0 / np.sum(spectral_weights ** 2)
        self.assertGreater(float(spectral_participation), 4.0)
        self.assertAlmostEqual(state_novelty(broad.initial.real ** 2, None), 1.0)
        self.assertAlmostEqual(
            state_novelty(broad.initial.real ** 2, broad.initial.real ** 2), 0.0
        )

        root = Path(__file__).parent / "max"
        patch = json.loads((root / "QMW_Bloch_Emergent_Event_Clock_v1.maxpat").read_text())
        text = "\n".join(x["box"].get("text", "") for x in patch["patcher"]["boxes"])
        self.assertIn("gen~ qmw_bloch_event_resonator", text)
        dsp_objects = [
            x["box"].get("text", "").lower()
            for x in patch["patcher"]["boxes"]
            if x["box"].get("maxclass") == "newobj"
        ]
        self.assertFalse(any(value.startswith("metro") for value in dsp_objects))
        resonator = json.loads((root / "qmw_bloch_event_resonator.gendsp").read_text())
        code = next(x["box"]["code"] for x in resonator["patcher"]["boxes"] if x["box"].get("id") == "code")
        self.assertIn("trigger = eventid != previous_event", code)

    def test_elements_adaptation_has_no_artificial_lfo(self):
        root = Path(__file__).parent / "max"
        patch = json.loads((root / "QMW_Bloch_Elements_Event_Clock_v1.maxpat").read_text())
        text = "\n".join(x["box"].get("text", "") for x in patch["patcher"]["boxes"])
        self.assertIn("mc.gen~ @gen qmw_bloch_elements_mode16_mc @chans 16", text)
        resonator = json.loads((root / "qmw_bloch_elements_mode16_mc.gendsp").read_text())
        code = next(x["box"]["code"] for x in resonator["patcher"]["boxes"] if x["box"].get("id") == "code")
        for token in ("stiffness", "q_loss", "pickup_center", "FILTER"):
            if token == "FILTER":
                self.assertIn("ic1eq", code)
            else:
                self.assertIn(token, code)
        self.assertNotIn("lfo_phase", code.lower())
        notice = (root / "THIRD_PARTY_ELEMENTS_NOTICE.md").read_text()
        self.assertIn("Copyright 2014 Emilie Gillet", notice)

    def test_elements_plain_gen_repair_has_local_strike_and_private_port(self):
        root = Path(__file__).parent / "max"
        patch = json.loads((root / "QMW_Bloch_Elements_Event_Clock_v1_1.maxpat").read_text())
        text = "\n".join(x["box"].get("text", "") for x in patch["patcher"]["boxes"])
        self.assertIn("udpreceive 7491", text)
        self.assertIn("gen~ qmw_bloch_elements_resonator", text)
        self.assertIn("999 0 0.", text)
        self.assertNotIn("mc.gen~", text)
        resonator = json.loads((root / "qmw_bloch_elements_resonator.gendsp").read_text())
        code = next(x["box"]["code"] for x in resonator["patcher"]["boxes"] if x["box"].get("id") == "code")
        self.assertIn("mallet=noise()*exciter_envelope", code)
        self.assertIn("v310=mallet*w10", code)


if __name__ == "__main__":
    unittest.main()
