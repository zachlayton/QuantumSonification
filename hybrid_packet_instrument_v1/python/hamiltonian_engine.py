#!/usr/bin/env python3
"""Pure-state Schrödinger packet projection backend (NumPy + Python stdlib).

Dimensionless hbar=m=1, hard walls at x=-1,+1. Exact-in-time unitary
propagation of the finite-difference Hamiltonian. Outputs 16 complex sine
mode overlaps at control rate, NOT acoustic samples or a thermal phonon bath.
SC deliberately sonifies these coefficients through its packet/modal engine.
"""
from __future__ import annotations

import argparse
import json
import math
import socket
import struct
import time
from dataclasses import dataclass

import numpy as np


def _osc_string(value: str) -> bytes:
    raw = value.encode('utf-8') + b'\0'
    return raw + b'\0' * (-len(raw) % 4)


def encode_osc(address: str, values) -> bytes:
    if not address.startswith('/'):
        raise ValueError('OSC address must start with /')
    tags, data = ',', bytearray()
    for value in values:
        if isinstance(value, (int, np.integer)):
            tags += 'i'
            data.extend(struct.pack('>i', int(value)))
        else:
            value = float(value)
            if not math.isfinite(value):
                raise ValueError('Nonfinite OSC value')
            tags += 'f'
            data.extend(struct.pack('>f', value))
    return _osc_string(address) + _osc_string(tags) + data


def decode_osc(packet: bytes):
    """Strict scalar OSC messages only; reject bundles and unsupported types."""
    def string_at(offset):
        end = packet.find(b'\0', offset)
        if end < 0:
            raise ValueError('Unterminated OSC string')
        value = packet[offset:end].decode('utf-8')
        nxt = (end + 4) & ~3
        if nxt > len(packet) or any(packet[end:nxt]):
            raise ValueError('Invalid OSC padding')
        return value, nxt
    address, offset = string_at(0)
    tags, offset = string_at(offset)
    if not address.startswith('/') or not tags.startswith(','):
        raise ValueError('Invalid OSC header')
    values = []
    for tag in tags[1:]:
        if tag not in ('i', 'f') or offset + 4 > len(packet):
            raise ValueError('Unsupported or truncated OSC argument')
        value = struct.unpack_from('>' + tag, packet, offset)[0]
        if not math.isfinite(value):
            raise ValueError('Nonfinite OSC argument')
        values.append(value)
        offset += 4
    if offset != len(packet):
        raise ValueError('Trailing OSC data')
    return address, values


@dataclass
class Parameters:
    potential: int = 1
    center: float = -0.35
    width: float = 0.12
    momentum: float = 2.0
    phase: float = 0.0
    omega: float = 8.0
    rate: float = 0.1


class HamiltonianEngine:
    def __init__(self, points=128, params=None):
        if not 32 <= points <= 1024:
            raise ValueError('points must be between 32 and 1024')
        self.params = params or Parameters()
        self.dx = 2.0 / (points + 1)
        self.x = -1 + self.dx * np.arange(1, points + 1)
        self.kinetic = (np.diag(np.ones(points)) -
                        0.5 * np.diag(np.ones(points - 1), 1) -
                        0.5 * np.diag(np.ones(points - 1), -1)) / self.dx**2
        # Integral of sin^2(j*pi*(x+1)/2) on [-1,1] is one.
        self.modal_basis = np.sin(np.outer(self.x + 1, np.arange(1, 17) * np.pi / 2))
        self.rebuild()

    def rebuild(self):
        p = self.params
        self.potential = 0.5 * p.omega**2 * self.x**2 if p.potential else np.zeros_like(self.x)
        self.H = self.kinetic + np.diag(self.potential)
        self.energies, self.eigenvectors = np.linalg.eigh(self.H)
        self.reset()

    def reset(self):
        p = self.params
        psi = np.exp(-(self.x-p.center)**2 / (4*p.width**2)).astype(complex)
        psi *= np.exp(1j * (p.momentum*(self.x-p.center) + p.phase))
        psi /= np.sqrt(np.vdot(psi, psi).real * self.dx)
        self.coefficients = self.eigenvectors.T @ psi
        self.model_time = 0.0

    @property
    def psi(self):
        return self.eigenvectors @ self.coefficients

    def advance(self, dt):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError('dt must be finite and nonnegative')
        self.coefficients *= np.exp(-1j * self.energies * dt)
        self.model_time += dt

    def diagnostics(self):
        psi = self.psi
        norm = float(np.vdot(psi, psi).real * self.dx)
        k = float(np.vdot(psi, self.kinetic @ psi).real * self.dx)
        v = float(np.sum(np.abs(psi)**2 * self.potential) * self.dx)
        return dict(time=self.model_time, norm=norm, energy=k+v, kinetic=k, potential=v,
                    mean_x=float(np.sum(self.x * np.abs(psi)**2) * self.dx))

    def overlaps(self):
        return self.modal_basis.T @ self.psi * self.dx

    def frame(self, sequence):
        d, c = self.diagnostics(), self.overlaps()
        return [sequence, d['time'], d['norm'], d['energy'], d['kinetic'], d['potential'],
                *c.real.tolist(), *c.imag.tolist()]

    def control(self, address, values):
        if address in ('/qmw/hybrid/physics/reset', '/qmw/hybrid/reset'):
            if len(values) > 1:
                raise ValueError('Reset accepts zero or one trigger argument')
            self.reset()
            return
        prefix = '/qmw/hybrid/physics/'
        limits = {'potential': (0, 1), 'center': (-.8, .8), 'width': (.02, .8),
                  'momentum': (-80, 80), 'phase': (-1e6, 1e6), 'omega': (0, 30), 'rate': (0, 10)}
        key = address[len(prefix):] if address.startswith(prefix) else ''
        if key not in limits or len(values) != 1:
            raise ValueError('Unknown control or incorrect argument count')
        value = float(values[0])
        lo, hi = limits[key]
        if not math.isfinite(value) or not lo <= value <= hi:
            raise ValueError(f'{key} must be in [{lo}, {hi}]')
        if key == 'potential':
            if value not in (0, 1):
                raise ValueError('potential must be 0 (box) or 1 (harmonic)')
            value = int(value)
        setattr(self.params, key, value)
        if key in ('potential', 'omega'):
            self.rebuild()
        elif key != 'rate':
            self.reset()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--listen-port', type=int, default=17921)
    parser.add_argument('--sc-port', type=int, default=17920)
    parser.add_argument('--points', type=int, default=128)
    parser.add_argument('--hz', type=float, default=30)
    parser.add_argument('--duration', type=float, default=0, help='seconds, 0 runs until Ctrl-C')
    parser.add_argument('--diagnostics', action='store_true', help='print JSON diagnostics once a second')
    parser.add_argument('--self-check', action='store_true', help='check isolated unitary evolution and exit')
    args = parser.parse_args()
    if not 1 <= args.hz <= 120 or args.duration < 0:
        parser.error('hz must be 1..120 and duration nonnegative')
    engine = HamiltonianEngine(args.points)
    if args.self_check:
        before = engine.diagnostics()
        for _ in range(100):
            engine.advance(.003)
        after = engine.diagnostics()
        assert abs(after['norm'] - 1) < 1e-10
        assert abs(after['energy'] - before['energy']) < 1e-8
        print(json.dumps({'self_check': 'passed', **after}))
        return
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('127.0.0.1', args.listen_port))
        sock.setblocking(False)
        start = last = deadline = time.monotonic()
        next_report, sequence = start, 0
        print(f'Pure-state backend listening 127.0.0.1:{args.listen_port}; projections -> {args.sc_port}', flush=True)
        try:
            while not args.duration or time.monotonic() - start < args.duration:
                # Bounded batch prevents a flooded control socket starving output.
                for _ in range(64):
                    try:
                        packet, _ = sock.recvfrom(4096)
                    except BlockingIOError:
                        break
                    try:
                        engine.control(*decode_osc(packet))
                    except (ValueError, UnicodeError, struct.error) as exc:
                        print(f'Ignored OSC control: {exc}', flush=True)
                now = time.monotonic()
                engine.advance((now-last) * engine.params.rate)
                last = now
                sock.sendto(encode_osc('/qmw/hybrid/projection', engine.frame(sequence)), ('127.0.0.1', args.sc_port))
                sequence = (sequence + 1) % 2147483647
                if args.diagnostics and now >= next_report:
                    print(json.dumps(engine.diagnostics()), flush=True)
                    next_report = now + 1
                deadline += 1/args.hz
                time.sleep(max(0, deadline-time.monotonic()))
                if deadline < time.monotonic()-1/args.hz:
                    deadline = time.monotonic()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
