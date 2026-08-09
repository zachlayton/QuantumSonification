#!/bin/zsh

set -e

qmw_bloch_script_dir=${0:A:h}
qmw_bloch_project_root=${qmw_bloch_script_dir:h}

cd "$qmw_bloch_project_root"
exec python -m bloch_band_navigator_v1.quench_events "$@"
