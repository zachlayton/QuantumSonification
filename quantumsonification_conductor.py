#!/usr/bin/env python3
"""
QuantumSonification Conductor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Master orchestrator for the entire QuantumSonification system.

Manages:
  - Canonical quantum simulation engine
  - Operator geometry/spectral systems
  - Circuit builder interactive UI
  - Max/MSP patch coordination
  - Audio input/output and recording
  - Parameter morphing and preset management
  - OSC routing and signal distribution

Usage:
    python quantumsonification_conductor.py --help
    python quantumsonification_conductor.py --profile resonator
    python quantumsonification_conductor.py --with-geometry --with-circuit-ui

"""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from pythonosc.udp_client import SimpleUDPClient
except ImportError:
    SimpleUDPClient = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Configuration & Logging
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT_ROOT = Path(__file__).resolve().parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("QSConductor")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Classes for Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@dataclass
class OSCConfig:
    """OSC network configuration."""
    host: str = "127.0.0.1"
    control_host: str = "127.0.0.1"
    engine_port: int = 7400
    supercollider_port: Optional[int] = None
    visual_port: int = 7401
    control_port: int = 7402
    geometry_port: int = 7405
    status_port: int = 7410


@dataclass
class EngineConfig:
    """Quantum simulation engine configuration."""
    enabled: bool = True
    implementation: str = "resonator_v9"
    protocol: str = "qmw-osc-v1"
    hz: float = 100.0
    density_field_hz: float = 30.0
    # Full visual diagnostics include several 256-value wavepacket arrays.
    # 8 Hz keeps those monitors fluid while leaving the 100 Hz quantum/grain
    # stream enough CPU headroom to maintain its clock.
    diagnostics_hz: float = 8.0
    status_hz: float = 0.5
    profile: str = "full"
    clock_source: str = "internal"
    excitation_source: str = "schrodinger_interference"
    excitation_drive: Optional[float] = None
    audio_path: Optional[str] = None


@dataclass
class GeometryConfig:
    """Operator geometry/spectral pipeline configuration."""
    enabled: bool = False
    mode: str = "noncommutative"  # or "algebraic", "emergent"
    auto_update_interval: Optional[float] = None
    output_format: str = "wav"
    emergent_preset: str = "labyrinth"
    emergent_size: int = 96
    emergent_rate: float = 10.0
    emergent_iterations: int = 2
    emergent_control_port: int = 7430
    emergent_out_port: int = 7431


@dataclass
class CircuitUIConfig:
    """Interactive circuit builder configuration."""
    enabled: bool = False
    n_qubits: int = 4
    n_steps: int = 16
    osc_enabled: bool = True


@dataclass
class QACBridgeConfig:
    """QAC/OpenQASM circuit-score bridge and density injection."""
    enabled: bool = False
    input_port: int = 7401
    output_port: int = 7400
    engine_control_port: int = 7402
    shots: int = 1024
    inject_density: bool = True


@dataclass
class EulerConfig:
    """Shared one-qubit Euler analysis for every accepted circuit."""

    enabled: bool = True
    basis: str = "ZXZ"
    mirror_processing: bool = True
    processing_host: str = "127.0.0.1"
    processing_port: int = 7497


@dataclass
class TemporalMechanicsConfig:
    """Relational quantum temporal-mechanics OSC stream."""
    enabled: bool = False
    state_port: int = 7444
    distance_per_pulse: float = 0.025
    mode: str = "poisson"
    coherence_depth: float = 0.35


@dataclass
class TemporalCrystalConfig:
    """In-process four-qubit logical-time and recurrence layer."""

    enabled: bool = False
    mode: str = "observer"
    rate_hz: float = 2.0


@dataclass
class CorrelationClockConfig:
    """Pairwise mutual-information correlation/differentiation clock."""
    enabled: bool = False
    state_port: int = 7444
    output_port: int = 7442
    change_quantum: float = 0.025


@dataclass
class RecorderConfig:
    """Audio/session recording configuration."""
    enabled: bool = False
    record_path: Optional[str] = None
    record_audio: bool = False
    record_osc: bool = False
    record_parameters: bool = False


@dataclass
class ConductorConfig:
    """Master conductor configuration."""
    osc: OSCConfig = field(default_factory=OSCConfig)
    engine: EngineConfig = field(default_factory=EngineConfig)
    geometry: GeometryConfig = field(default_factory=GeometryConfig)
    circuit_ui: CircuitUIConfig = field(default_factory=CircuitUIConfig)
    qac_bridge: QACBridgeConfig = field(default_factory=QACBridgeConfig)
    euler: EulerConfig = field(default_factory=EulerConfig)
    temporal_mechanics: TemporalMechanicsConfig = field(
        default_factory=TemporalMechanicsConfig
    )
    temporal_crystal: TemporalCrystalConfig = field(
        default_factory=TemporalCrystalConfig
    )
    correlation_clock: CorrelationClockConfig = field(
        default_factory=CorrelationClockConfig
    )
    recorder: RecorderConfig = field(default_factory=RecorderConfig)
    verbose: bool = False
    quiet: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConductorConfig:
        return cls(
            osc=OSCConfig(**data.get("osc", {})),
            engine=EngineConfig(**data.get("engine", {})),
            geometry=GeometryConfig(**data.get("geometry", {})),
            circuit_ui=CircuitUIConfig(**data.get("circuit_ui", {})),
            qac_bridge=QACBridgeConfig(**data.get("qac_bridge", {})),
            euler=EulerConfig(**data.get("euler", {})),
            temporal_mechanics=TemporalMechanicsConfig(
                **data.get("temporal_mechanics", {})
            ),
            temporal_crystal=TemporalCrystalConfig(
                **data.get("temporal_crystal", {})
            ),
            correlation_clock=CorrelationClockConfig(
                **data.get("correlation_clock", {})
            ),
            recorder=RecorderConfig(**data.get("recorder", {})),
            verbose=bool(data.get("verbose", False)),
            quiet=bool(data.get("quiet", False)),
        )

    def save(self, path: Path) -> None:
        """Save configuration to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Configuration saved to {path}")

    @classmethod
    def load(cls, path: Path) -> ConductorConfig:
        """Load configuration from JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        logger.info(f"Configuration loaded from {path}")
        return cls.from_dict(data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Process Management
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ManagedProcess:
    """Wraps a subprocess with lifecycle management."""

    OUTPUT_TAIL_LIMIT = 32 * 1024

    def __init__(self, name: str, cmd: List[str], env: Optional[Dict[str, str]] = None):
        self.name = name
        self.cmd = cmd
        self.env = env or os.environ.copy()
        self.process: Optional[subprocess.Popen] = None
        self.start_time: Optional[float] = None
        self.exit_reported = False
        self._output_thread: Optional[threading.Thread] = None
        self._output_tail = ""
        self._output_lock = threading.Lock()

    def _drain_output(self, stream) -> None:
        """Continuously drain child output while retaining a bounded tail.

        The resonator prints carriage-return status updates from the same
        thread that advances the simulation. If its captured pipe is not
        drained, the 64 KiB OS buffer eventually fills and blocks both the
        status print and subsequent OSC frames.
        """
        try:
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    break
                with self._output_lock:
                    self._output_tail = (
                        self._output_tail + chunk
                    )[-self.OUTPUT_TAIL_LIMIT :]
        except (OSError, ValueError):
            # The stream can be closed as part of process teardown.
            pass
        finally:
            try:
                stream.close()
            except (OSError, ValueError):
                pass

    def _start_output_drain(self) -> None:
        if self.process is None or self.process.stdout is None:
            return
        with self._output_lock:
            self._output_tail = ""
        self._output_thread = threading.Thread(
            target=self._drain_output,
            args=(self.process.stdout,),
            name=f"{self.name}-output-drain",
            daemon=True,
        )
        self._output_thread.start()

    def _wait_for_output_drain(self, timeout: float = 1.0) -> None:
        if self._output_thread is not None:
            self._output_thread.join(timeout=timeout)

    def captured_output(self) -> str:
        """Return the bounded tail of the child process's combined output."""
        with self._output_lock:
            return self._output_tail

    def start(self) -> bool:
        """Start the subprocess."""
        if self.process is not None:
            logger.warning(f"{self.name} is already running (PID: {self.process.pid})")
            return False

        try:
            logger.info(f"Starting {self.name}: {' '.join(self.cmd)}")
            self.process = subprocess.Popen(
                self.cmd,
                env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                bufsize=1,
            )
            self._start_output_drain()
            self.start_time = time.time()
            self.exit_reported = False
            logger.info(f"{self.name} started (PID: {self.process.pid})")
            
            # Give it a moment to start, then check if it crashed
            time.sleep(0.5)
            if not self.is_running():
                # Process died immediately; capture error
                self._wait_for_output_drain()
                output = self.captured_output()
                logger.error(
                    f"{self.name} exited during startup with code "
                    f"{self.process.returncode}. Output:\n{output}"
                )
                self.exit_reported = True
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to start {self.name}: {e}")
            return False

    def stop(self, timeout: float = 5.0) -> bool:
        """Stop the subprocess gracefully."""
        if self.process is None:
            logger.warning(f"{self.name} is not running")
            return True

        try:
            logger.info(f"Stopping {self.name} (PID: {self.process.pid})...")
            self.process.terminate()
            try:
                self.process.wait(timeout=timeout)
                self._wait_for_output_drain()
                logger.info(f"{self.name} stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning(f"{self.name} did not stop; killing...")
                self.process.kill()
                self.process.wait()
                self._wait_for_output_drain()
                logger.info(f"{self.name} killed")
            return True
        except Exception as e:
            logger.error(f"Error stopping {self.name}: {e}")
            return False
        finally:
            self.process = None
            self.start_time = None

    def is_running(self) -> bool:
        """Check if subprocess is still running."""
        if self.process is None:
            return False
        return self.process.poll() is None

    def uptime(self) -> Optional[float]:
        """Return uptime in seconds, or None if not running."""
        if not self.is_running() or self.start_time is None:
            return None
        return time.time() - self.start_time

    def report_unexpected_exit(self) -> None:
        """Log a child process's captured output once after a delayed exit."""
        if self.process is None or self.is_running() or self.exit_reported:
            return

        self._wait_for_output_drain()
        output = self.captured_output()

        message = (
            f"Process {self.name} exited with code {self.process.returncode}."
        )
        if output:
            message += f" Output:\n{output}"
        logger.error(message)
        self.exit_reported = True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# The Conductor
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class QuantumSonificationConductor:
    """
    Master orchestrator for all QuantumSonification subsystems.
    
    Responsibilities:
      - Launch and monitor the engine, circuit UI, and geometry pipelines
      - Coordinate OSC communication between components
      - Manage configuration and presets
      - Record sessions and parameter changes
      - Provide unified control interface
    """

    def __init__(self, config: ConductorConfig):
        self.config = config
        self.processes: Dict[str, ManagedProcess] = {}
        self.is_running = False
        self.osc_client: Optional[SimpleUDPClient] = None
        self._setup_logging()
        self._setup_signal_handlers()

    def _setup_logging(self) -> None:
        """Configure logging verbosity."""
        if self.config.quiet:
            logging.getLogger().setLevel(logging.WARNING)
        elif self.config.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    def _setup_signal_handlers(self) -> None:
        """Handle graceful shutdown on SIGINT/SIGTERM."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}; shutting down...")
        self.shutdown()
        sys.exit(0)

    def _build_engine_command(self) -> List[str]:
        """Build the command for the stable, canonical engine launcher."""
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "quantumsonification_engine.py"),
            f"--implementation={self.config.engine.implementation}",
            f"--protocol={self.config.engine.protocol}",
            f"--osc-host={self.config.osc.host}",
            f"--osc-port={self.config.osc.engine_port}",
            f"--visual-osc-port={self.config.osc.visual_port}",
            f"--control-port={self.config.osc.control_port}",
            f"--control-host={self.config.osc.control_host}",
            f"--status-osc-port={self.config.osc.status_port}",
            f"--engine-hz={self.config.engine.hz}",
            f"--density-field-hz={self.config.engine.density_field_hz}",
            f"--diagnostics-hz={self.config.engine.diagnostics_hz}",
            f"--status-hz={self.config.engine.status_hz}",
            f"--osc-profile={self.config.engine.profile}",
            f"--clock-source={self.config.engine.clock_source}",
            f"--excitation-source={self.config.engine.excitation_source}",
        ]

        if self.config.engine.excitation_drive is not None:
            cmd.append(
                f"--excitation-drive={self.config.engine.excitation_drive}"
            )

        if self.config.engine.audio_path:
            cmd.append(f"--audio-path={self.config.engine.audio_path}")

        if self.config.osc.supercollider_port is not None:
            cmd.append(
                f"--sc-osc-port={self.config.osc.supercollider_port}"
            )

        if self.config.temporal_crystal.enabled:
            cmd.extend(
                [
                    (
                        "--temporal-crystal-mode="
                        f"{self.config.temporal_crystal.mode}"
                    ),
                    (
                        "--temporal-crystal-rate="
                        f"{self.config.temporal_crystal.rate_hz}"
                    ),
                ]
            )

        if self.config.temporal_mechanics.enabled:
            cmd.append(
                f"--temporal-state-port={self.config.temporal_mechanics.state_port}"
            )
        elif self.config.correlation_clock.enabled:
            cmd.append(
                f"--temporal-state-port={self.config.correlation_clock.state_port}"
            )

        if self.config.quiet:
            cmd.append("--quiet")
        if self.config.verbose:
            cmd.append("--verbose")

        return cmd

    def _build_circuit_ui_command(self) -> List[str]:
        """Build command line for interactive circuit builder."""
        return [
            sys.executable,
            str(PROJECT_ROOT / "qmw_circuit_builder_controller.py"),
        ]

    def _build_qac_bridge_command(self) -> List[str]:
        cmd = [
            sys.executable,
            "-m",
            "qac_quantumsonification_bridge_v1.qac_quantumsonification_bridge_v1",
            f"--in-host={self.config.osc.host}",
            f"--in-port={self.config.qac_bridge.input_port}",
            f"--out-host={self.config.osc.host}",
            f"--out-port={self.config.qac_bridge.output_port}",
            f"--shots={self.config.qac_bridge.shots}",
            f"--euler-basis={self.config.euler.basis}",
        ]
        if not self.config.euler.enabled:
            cmd.append("--no-euler")
        elif self.config.euler.mirror_processing:
            cmd.extend(
                [
                    (
                        "--euler-mirror-host="
                        f"{self.config.euler.processing_host}"
                    ),
                    (
                        "--euler-mirror-port="
                        f"{self.config.euler.processing_port}"
                    ),
                ]
            )
        if self.config.qac_bridge.inject_density:
            cmd.extend(
                [
                    f"--engine-control-host={self.config.osc.host}",
                    f"--engine-control-port={self.config.qac_bridge.engine_control_port}",
                ]
            )
        return cmd

    def _build_temporal_mechanics_command(self) -> List[str]:
        """Turn live engine density displacement into Max clock pulses."""
        return [
            sys.executable,
            "-m",
            "quantum_temporal_mechanics_v1.density_clock_osc",
            f"--input-host={self.config.osc.host}",
            f"--input-port={self.config.temporal_mechanics.state_port}",
            f"--output-host={self.config.osc.host}",
            f"--output-port={self.config.osc.engine_port}",
            f"--distance-per-pulse={self.config.temporal_mechanics.distance_per_pulse}",
            f"--mode={self.config.temporal_mechanics.mode}",
            f"--coherence-depth={self.config.temporal_mechanics.coherence_depth}",
        ]

    def _build_correlation_clock_command(self) -> List[str]:
        """Turn live engine qubit mutual-information change into v2 ticks."""
        return [
            sys.executable,
            "-m",
            "quantum_temporal_composition_v2.density_correlation_osc",
            f"--input-host={self.config.osc.host}",
            f"--input-port={self.config.correlation_clock.state_port}",
            f"--output-host={self.config.osc.host}",
            f"--output-port={self.config.correlation_clock.output_port}",
            f"--change-quantum={self.config.correlation_clock.change_quantum}",
        ]

    def _build_geometry_command(self) -> List[str]:
        """Build command line for geometry/spectral pipeline."""
        if self.config.geometry.mode == "emergent":
            return [
                sys.executable,
                str(
                    PROJECT_ROOT
                    / "emergent_geometry_v1_osc"
                    / "emergent_geometry_osc_v1.py"
                ),
                f"--host={self.config.osc.host}",
                f"--control-port={self.config.geometry.emergent_control_port}",
                f"--out-host={self.config.osc.host}",
                f"--out-port={self.config.geometry.emergent_out_port}",
                f"--preset={self.config.geometry.emergent_preset}",
                f"--size={self.config.geometry.emergent_size}",
                f"--rate={self.config.geometry.emergent_rate}",
                f"--iterations={self.config.geometry.emergent_iterations}",
            ]
        return [
            sys.executable,
            str(PROJECT_ROOT / "operators" / "operator_ecology_controller_v1.py"),
        ]

    def startup(self) -> bool:
        """Start all enabled subsystems."""
        logger.info("=" * 70)

        if (
            self.config.temporal_mechanics.enabled
            and self.config.correlation_clock.enabled
        ):
            logger.error(
                "Choose either temporal mechanics v1 or correlation clock v2; "
                "both require the private density-state port."
            )
            return False
        logger.info("QUANTUMSONIFICATION CONDUCTOR STARTUP")
        logger.info("=" * 70)

        if self.config.engine.enabled:
            cmd = self._build_engine_command()
            proc = ManagedProcess("Quantum-Engine", cmd)
            if proc.start():
                self.processes["quantum_engine"] = proc
                time.sleep(1)  # Let engine initialize
            else:
                logger.error(
                    "Failed to start quantum engine; continuing anyway"
                )

        if self.config.geometry.enabled:
            cmd = self._build_geometry_command()
            proc = ManagedProcess("Geometry-Pipeline", cmd)
            if proc.start():
                self.processes["geometry"] = proc
                time.sleep(1)

        if self.config.circuit_ui.enabled:
            cmd = self._build_circuit_ui_command()
            proc = ManagedProcess("Circuit-UI", cmd)
            if proc.start():
                self.processes["circuit_ui"] = proc
                time.sleep(1)

        if self.config.qac_bridge.enabled:
            cmd = self._build_qac_bridge_command()
            proc = ManagedProcess("QAC-Bridge", cmd)
            if proc.start():
                self.processes["qac_bridge"] = proc
                time.sleep(0.5)

        if self.config.temporal_mechanics.enabled:
            cmd = self._build_temporal_mechanics_command()
            proc = ManagedProcess("Temporal-Mechanics", cmd)
            if proc.start():
                self.processes["temporal_mechanics"] = proc
                time.sleep(0.5)

        if self.config.correlation_clock.enabled:
            cmd = self._build_correlation_clock_command()
            proc = ManagedProcess("Correlation-Clock-v2", cmd)
            if proc.start():
                self.processes["correlation_clock"] = proc
                time.sleep(0.5)

        # Initialize OSC client for sending control messages
        if SimpleUDPClient:
            self.osc_client = SimpleUDPClient(
                self.config.osc.host,
                self.config.osc.engine_port,
            )
            logger.info(f"OSC client ready: {self.config.osc.host}:{self.config.osc.engine_port}")

        self.is_running = True
        logger.info(f"Conductor started with {len(self.processes)} subprocess(es)")
        return True

    def shutdown(self) -> None:
        """Stop all running subsystems gracefully."""
        logger.info("=" * 70)
        logger.info("QUANTUMSONIFICATION CONDUCTOR SHUTDOWN")
        logger.info("=" * 70)

        self.is_running = False

        for name, proc in self.processes.items():
            proc.stop(timeout=5.0)

        logger.info("Conductor shutdown complete")

    def status(self) -> Dict[str, Any]:
        """Get status of all subsystems."""
        status = {
            "conductor_running": self.is_running,
            "timestamp": time.time(),
            "processes": {},
        }

        for name, proc in self.processes.items():
            status["processes"][name] = {
                "running": proc.is_running(),
                "pid": proc.process.pid if proc.process else None,
                "uptime_seconds": proc.uptime(),
            }

        return status

    def print_status(self) -> None:
        """Pretty-print conductor status."""
        status = self.status()
        print("\n" + "=" * 70)
        print("CONDUCTOR STATUS")
        print("=" * 70)
        print(f"Conductor running: {status['conductor_running']}")
        print(f"Time: {status['timestamp']}")
        print()

        for name, proc_status in status["processes"].items():
            running_str = "✓ RUNNING" if proc_status["running"] else "✗ STOPPED"
            pid_str = f" (PID: {proc_status['pid']})" if proc_status["pid"] else ""
            uptime_str = (
                f" | Uptime: {proc_status['uptime_seconds']:.1f}s"
                if proc_status["uptime_seconds"] is not None
                else ""
            )
            print(f"  {name:20s} {running_str}{pid_str}{uptime_str}")

        print("=" * 70 + "\n")

    def interactive_loop(self) -> None:
        """Run interactive shell for conductor control."""
        print(
            "\nQuantumSonification Conductor Interactive Mode\n"
            "Commands: status, shutdown, restart, help\n"
        )

        while self.is_running:
            try:
                cmd = input("conductor> ").strip().lower()

                if cmd == "status":
                    self.print_status()
                elif cmd == "shutdown":
                    self.shutdown()
                elif cmd == "restart":
                    logger.info("Restarting all processes...")
                    for proc in self.processes.values():
                        proc.stop()
                    time.sleep(2)
                    self.startup()
                elif cmd == "help":
                    print("Commands: status, shutdown, restart, help, quit")
                elif cmd in {"quit", "exit"}:
                    self.shutdown()
                elif cmd:
                    print(f"Unknown command: {cmd}")

            except KeyboardInterrupt:
                self.shutdown()
                break
            except Exception as e:
                logger.error(f"Error in interactive loop: {e}")

    def monitor_loop(self, update_interval: float = 5.0) -> None:
        """Monitor subprocess health in background."""
        logger.info(f"Starting health monitor (interval: {update_interval}s)")

        while self.is_running:
            time.sleep(update_interval)

            status = self.status()
            for name, proc_status in status["processes"].items():
                if not proc_status["running"]:
                    self.processes[name].report_unexpected_exit()

            if not self.config.quiet and self.config.verbose:
                uptime_strs = []
                for name, proc_status in status["processes"].items():
                    if proc_status["uptime_seconds"] is not None:
                        uptime_strs.append(f"{name}:{proc_status['uptime_seconds']:.0f}s")
                if uptime_strs:
                    logger.debug(f"Uptimes: {', '.join(uptime_strs)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="QuantumSonification Conductor - Master orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with the canonical engine only
  python quantumsonification_conductor.py
  
  # Start all subsystems
  python quantumsonification_conductor.py --with-geometry --with-circuit-ui
  
  # Load a saved configuration
  python quantumsonification_conductor.py --config my_config.json
  
  # Start in non-interactive mode (for automated workflows)
  python quantumsonification_conductor.py --daemon
        """,
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Load configuration from JSON file",
    )

    parser.add_argument(
        "--osc-host",
        default="127.0.0.1",
        help="OSC host address (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--osc-engine-port",
        type=int,
        default=7400,
        help="OSC port for engine (default: 7400)",
    )

    parser.add_argument(
        "--control-host",
        default="127.0.0.1",
        help="Local control-server bind address (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--supercollider-port",
        type=int,
        default=None,
        help="Mirror the engine OSC stream to SuperCollider (usually 57120)",
    )

    parser.add_argument(
        "--engine-implementation",
        default="resonator_v9",
        help="Canonical engine backend (default: resonator_v9)",
    )

    parser.add_argument(
        "--engine-protocol",
        default="qmw-osc-v1",
        help="Required engine OSC protocol (default: qmw-osc-v1)",
    )

    parser.add_argument(
        "--engine-hz",
        type=float,
        default=100.0,
        help="Engine update frequency (default: 100 Hz)",
    )

    parser.add_argument(
        "--density-field-hz",
        type=float,
        default=30.0,
        help="Density-field OSC frequency (default: 30 Hz)",
    )

    parser.add_argument(
        "--excitation-source",
        choices=[
            "internal",
            "born_transition",
            "hydrogen_spectrum",
            "hydrogen_orbital",
            "schrodinger_packet",
            "schrodinger_interference",
        ],
        default="schrodinger_interference",
        help=(
            "Density-engine excitation source "
            "(default: schrodinger_interference)"
        ),
    )

    parser.add_argument(
        "--excitation-drive",
        type=float,
        default=None,
        help=(
            "Override the selected excitation mode's drive strength "
            "(non-negative; default: use the mode profile)"
        ),
    )

    parser.add_argument(
        "--diagnostics-hz",
        type=float,
        default=8.0,
        help="Dashboard and mutual-information OSC frequency (default: 8 Hz)",
    )

    parser.add_argument(
        "--profile",
        choices=["resonator", "full"],
        default="full",
        help="OSC profile for Max integration (default: full)",
    )

    parser.add_argument(
        "--audio-path",
        type=Path,
        help="Path to audio file for feedback",
    )

    parser.add_argument(
        "--with-geometry",
        action="store_true",
        help="Enable geometry/spectral pipeline",
    )

    parser.add_argument(
        "--with-emergent-geometry",
        action="store_true",
        help="Enable the lightweight MLX emergent descriptor stream on UDP 7431",
    )

    parser.add_argument(
        "--emergent-preset",
        choices=["labyrinth", "cellular", "coral_growth"],
        default="labyrinth",
        help="Emergent geometry preset (default: labyrinth)",
    )

    parser.add_argument(
        "--emergent-size",
        type=int,
        default=96,
        help="Emergent MLX field width/height (default: 96)",
    )

    parser.add_argument(
        "--emergent-rate",
        type=float,
        default=10.0,
        help="Emergent descriptor update rate (default: 10 Hz)",
    )

    parser.add_argument(
        "--emergent-iterations",
        type=int,
        default=2,
        help="Reaction-diffusion iterations per update (default: 2)",
    )

    parser.add_argument(
        "--with-circuit-ui",
        action="store_true",
        help="Enable interactive circuit builder UI",
    )

    parser.add_argument(
        "--with-qac-bridge",
        action="store_true",
        help="Enable the QAC/OpenQASM circuit and density bridge",
    )

    parser.add_argument(
        "--no-euler",
        action="store_true",
        help="Disable shared one-qubit Euler analysis for circuit workflows",
    )

    parser.add_argument(
        "--euler-basis",
        choices=["ZXZ", "ZYZ", "XYX", "XZX"],
        default="ZXZ",
        help="One-qubit Euler basis (default: ZXZ for direct ZX spiders)",
    )

    parser.add_argument(
        "--euler-processing-port",
        type=int,
        default=7497,
        help="Mirror circuit Euler data to Processing (default: 7497)",
    )

    parser.add_argument(
        "--with-temporal-mechanics",
        action="store_true",
        help="Stream relational temporal mechanics to Max on the engine port",
    )

    parser.add_argument(
        "--with-temporal-crystal",
        action="store_true",
        help="Enable the in-process QMW temporal-crystal/logical-time layer",
    )

    parser.add_argument(
        "--temporal-crystal-mode",
        choices=["observer", "floquet", "lfsr", "pythagorean"],
        default="observer",
        help="Temporal-crystal protocol (default: observer)",
    )

    parser.add_argument(
        "--temporal-crystal-rate",
        type=float,
        default=2.0,
        help="Logical temporal steps per second (default: 2 Hz)",
    )

    parser.add_argument(
        "--with-correlation-clock",
        action="store_true",
        help="Drive correlation/differentiation ticks from live qubit mutual information",
    )

    parser.add_argument(
        "--correlation-state-port",
        type=int,
        default=7444,
        help="Private engine density port for correlation clock v2 (default: 7444)",
    )

    parser.add_argument(
        "--correlation-clock-port",
        type=int,
        default=7442,
        help="OSC output port for correlation/differentiation v2 (default: 7442)",
    )

    parser.add_argument(
        "--correlation-change-quantum",
        type=float,
        default=0.025,
        help="Mutual-information change accumulated per v2 tick (default: 0.025)",
    )

    parser.add_argument(
        "--temporal-distance",
        type=float,
        default=0.025,
        help="Bures-angle distance required per temporal pulse (default: 0.025)",
    )

    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon (no interactive shell)",
    )

    parser.add_argument(
        "--save-config",
        type=Path,
        help="Save current configuration to JSON file and exit",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-essential output",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Load or build configuration
    if args.config:
        config = ConductorConfig.load(args.config)
    else:
        config = ConductorConfig(
            osc=OSCConfig(
                host=args.osc_host,
                control_host=args.control_host,
                engine_port=args.osc_engine_port,
                supercollider_port=args.supercollider_port,
            ),
            engine=EngineConfig(
                implementation=args.engine_implementation,
                protocol=args.engine_protocol,
                hz=args.engine_hz,
                density_field_hz=args.density_field_hz,
                diagnostics_hz=args.diagnostics_hz,
                profile=args.profile,
                excitation_source=args.excitation_source,
                excitation_drive=args.excitation_drive,
                audio_path=str(args.audio_path) if args.audio_path else None,
            ),
            geometry=GeometryConfig(
                enabled=args.with_geometry or args.with_emergent_geometry,
                mode=(
                    "emergent"
                    if args.with_emergent_geometry
                    else "noncommutative"
                ),
                emergent_preset=args.emergent_preset,
                emergent_size=max(32, args.emergent_size),
                emergent_rate=max(0.1, args.emergent_rate),
                emergent_iterations=max(1, args.emergent_iterations),
            ),
            circuit_ui=CircuitUIConfig(enabled=args.with_circuit_ui),
            qac_bridge=QACBridgeConfig(enabled=args.with_qac_bridge),
            euler=EulerConfig(
                enabled=not args.no_euler,
                basis=args.euler_basis,
                processing_host=args.osc_host,
                processing_port=args.euler_processing_port,
            ),
            temporal_mechanics=TemporalMechanicsConfig(
                enabled=args.with_temporal_mechanics,
                distance_per_pulse=max(1e-6, args.temporal_distance),
            ),
            temporal_crystal=TemporalCrystalConfig(
                enabled=args.with_temporal_crystal,
                mode=args.temporal_crystal_mode,
                rate_hz=max(1e-6, args.temporal_crystal_rate),
            ),
            correlation_clock=CorrelationClockConfig(
                enabled=args.with_correlation_clock,
                state_port=args.correlation_state_port,
                output_port=args.correlation_clock_port,
                change_quantum=max(1e-6, args.correlation_change_quantum),
            ),
            verbose=args.verbose,
            quiet=args.quiet,
        )

    # Save and exit if requested
    if args.save_config:
        config.save(args.save_config)
        return 0

    # Start conductor
    conductor = QuantumSonificationConductor(config)

    if not conductor.startup():
        logger.error("Failed to start conductor")
        return 1

    # Print initial status
    conductor.print_status()

    # Run monitoring in background
    monitor_thread = threading.Thread(
        target=conductor.monitor_loop,
        kwargs={"update_interval": 5.0},
        daemon=True,
    )
    monitor_thread.start()

    # Interactive or daemon mode
    if args.daemon:
        logger.info("Running in daemon mode; press Ctrl+C to shutdown")
        try:
            while conductor.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            conductor.shutdown()
    else:
        conductor.interactive_loop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
