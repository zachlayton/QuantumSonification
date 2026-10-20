#!/bin/bash
set -e
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
exec python3 python/hamiltonian_engine.py --diagnostics "$@"
