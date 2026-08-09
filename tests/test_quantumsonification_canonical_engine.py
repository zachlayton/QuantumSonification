"""Contract tests for the canonical engine launcher and conductor wiring."""

from __future__ import annotations

import sys
import time
import unittest

from quantumsonification_conductor import (
    CorrelationClockConfig,
    ConductorConfig,
    EulerConfig,
    GeometryConfig,
    ManagedProcess,
    QuantumSonificationConductor,
    TemporalCrystalConfig,
    TemporalMechanicsConfig,
)
from quantumsonification_engine import (
    DEFAULT_IMPLEMENTATION,
    DEFAULT_PROTOCOL,
    resolve_implementation,
)


class CanonicalEngineTests(unittest.TestCase):
    def test_default_implementation_is_registered_and_present(self) -> None:
        name, implementation = resolve_implementation(
            DEFAULT_IMPLEMENTATION
        )
        self.assertEqual(name, "resonator_v9")
        self.assertEqual(implementation.protocol, DEFAULT_PROTOCOL)
        self.assertTrue(implementation.script.is_file())

    def test_stable_alias_resolves_to_default(self) -> None:
        name, _implementation = resolve_implementation("canonical")
        self.assertEqual(name, DEFAULT_IMPLEMENTATION)

    def test_legacy_config_gets_canonical_defaults(self) -> None:
        config = ConductorConfig.from_dict({"engine": {"hz": 64.0}})
        self.assertEqual(config.engine.implementation, DEFAULT_IMPLEMENTATION)
        self.assertEqual(config.engine.protocol, DEFAULT_PROTOCOL)
        self.assertEqual(config.engine.hz, 64.0)
        self.assertTrue(config.euler.enabled)
        self.assertEqual(config.euler.basis, "ZXZ")

    def test_conductor_invokes_canonical_launcher(self) -> None:
        conductor = object.__new__(QuantumSonificationConductor)
        conductor.config = ConductorConfig()
        command = conductor._build_engine_command()

        self.assertEqual(command[0], sys.executable)
        self.assertTrue(command[1].endswith("quantumsonification_engine.py"))
        self.assertIn("--implementation=resonator_v9", command)
        self.assertIn("--protocol=qmw-osc-v1", command)
        self.assertFalse(
            any(
                argument.endswith(
                    "quantum_population_osc_v9_resonator.py"
                )
                for argument in command
            )
        )

    def test_conductor_enables_shared_euler_stream_for_qac(self) -> None:
        conductor = object.__new__(QuantumSonificationConductor)
        conductor.config = ConductorConfig(
            euler=EulerConfig(
                enabled=True,
                basis="ZXZ",
                processing_host="127.0.0.1",
                processing_port=7597,
            )
        )

        command = conductor._build_qac_bridge_command()

        self.assertEqual(
            command[:3],
            [
                sys.executable,
                "-m",
                (
                    "qac_quantumsonification_bridge_v1."
                    "qac_quantumsonification_bridge_v1"
                ),
            ],
        )
        self.assertIn("--euler-basis=ZXZ", command)
        self.assertIn("--euler-mirror-host=127.0.0.1", command)
        self.assertIn("--euler-mirror-port=7597", command)

    def test_managed_process_drains_large_child_output(self) -> None:
        process = ManagedProcess(
            "output-drain-test",
            [
                sys.executable,
                "-u",
                "-c",
                (
                    "import sys,time; "
                    "sys.stdout.write('x' * (2 * 1024 * 1024)); "
                    "sys.stdout.write('OUTPUT-DRAIN-COMPLETE'); "
                    "sys.stdout.flush(); time.sleep(0.75)"
                ),
            ],
        )
        self.assertTrue(process.start())

        deadline = time.monotonic() + 3.0
        while process.is_running() and time.monotonic() < deadline:
            time.sleep(0.02)

        self.assertFalse(process.is_running())
        process._wait_for_output_drain()
        self.assertIn("OUTPUT-DRAIN-COMPLETE", process.captured_output())

    def test_conductor_builds_lightweight_emergent_geometry_command(self) -> None:
        conductor = object.__new__(QuantumSonificationConductor)
        conductor.config = ConductorConfig(
            geometry=GeometryConfig(
                enabled=True,
                mode="emergent",
                emergent_preset="cellular",
                emergent_size=96,
                emergent_rate=10.0,
                emergent_iterations=2,
            )
        )
        command = conductor._build_geometry_command()

        self.assertEqual(command[0], sys.executable)
        self.assertTrue(command[1].endswith("emergent_geometry_osc_v1.py"))
        self.assertIn("--out-port=7431", command)
        self.assertIn("--preset=cellular", command)
        self.assertIn("--size=96", command)
        self.assertIn("--rate=10.0", command)
        self.assertIn("--iterations=2", command)

    def test_conductor_routes_temporal_mechanics_to_max_engine_port(self) -> None:
        conductor = object.__new__(QuantumSonificationConductor)
        conductor.config = ConductorConfig(
            temporal_mechanics=TemporalMechanicsConfig(
                enabled=True,
                state_port=7555,
                distance_per_pulse=0.04,
            )
        )
        command = conductor._build_temporal_mechanics_command()

        self.assertEqual(command[:3], [sys.executable, "-m", "quantum_temporal_mechanics_v1.density_clock_osc"])
        self.assertIn("--input-port=7555", command)
        self.assertIn("--output-port=7400", command)
        self.assertIn("--distance-per-pulse=0.04", command)

        engine_command = conductor._build_engine_command()
        self.assertIn("--temporal-state-port=7555", engine_command)

    def test_conductor_enables_rate_limited_temporal_crystal(self) -> None:
        conductor = object.__new__(QuantumSonificationConductor)
        conductor.config = ConductorConfig(
            temporal_crystal=TemporalCrystalConfig(
                enabled=True,
                mode="floquet",
                rate_hz=2.5,
            )
        )

        command = conductor._build_engine_command()

        self.assertIn("--temporal-crystal-mode=floquet", command)
        self.assertIn("--temporal-crystal-rate=2.5", command)

    def test_legacy_config_keeps_temporal_crystal_disabled(self) -> None:
        config = ConductorConfig.from_dict({"engine": {"hz": 64.0}})

        self.assertFalse(config.temporal_crystal.enabled)
        self.assertEqual(config.temporal_crystal.mode, "observer")
        self.assertEqual(config.temporal_crystal.rate_hz, 2.0)

    def test_conductor_routes_live_density_to_correlation_clock_v2(self) -> None:
        conductor = object.__new__(QuantumSonificationConductor)
        conductor.config = ConductorConfig(
            correlation_clock=CorrelationClockConfig(
                enabled=True,
                state_port=7666,
                output_port=7442,
                change_quantum=0.03,
            )
        )
        command = conductor._build_correlation_clock_command()
        self.assertEqual(
            command[:3],
            [
                sys.executable,
                "-m",
                "quantum_temporal_composition_v2.density_correlation_osc",
            ],
        )
        self.assertIn("--input-port=7666", command)
        self.assertIn("--output-port=7442", command)
        self.assertIn("--change-quantum=0.03", command)
        engine_command = conductor._build_engine_command()
        self.assertIn("--temporal-state-port=7666", engine_command)


if __name__ == "__main__":
    unittest.main()
