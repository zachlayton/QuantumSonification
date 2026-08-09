#!/bin/zsh

QMW_FBF_DIRECTORY=${0:A:h}

exec "/Applications/SuperCollider.app/Contents/MacOS/sclang" \
	-D "$QMW_FBF_DIRECTORY/FloquetBoundaryFreezeV1.scd"
