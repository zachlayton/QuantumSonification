#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
sdk_root=${QMW_MAX_SDK_BASE:-/private/tmp/qmw-max-sdk-base}
include_root="$sdk_root/c74support/max-includes"
msp_include_root="$sdk_root/c74support/msp-includes"
macos_sdk=$(xcrun --sdk macosx --show-sdk-path)
build_root=$(mktemp -d /private/tmp/qmw-native-build.XXXXXX)
if [ ! -f "$include_root/ext.h" ]; then
    printf '%s\n' "Max SDK header not found: $include_root/ext.h" >&2
    printf '%s\n' "Set QMW_MAX_SDK_BASE to a pinned Cycling74/max-sdk-base checkout." >&2
    exit 2
fi
if [ ! -f "$msp_include_root/z_dsp.h" ]; then
    printf '%s\n' "Max MSP SDK header not found: $msp_include_root/z_dsp.h" >&2
    exit 2
fi

common_flags="-std=c++20 -O2 -Wall -Wextra -Werror -Wno-cast-function-type-mismatch -pedantic -fvisibility=hidden"

build_core_archive()
{
    architecture=$1
    architecture_root="$build_root/$architecture"
    mkdir -p "$architecture_root"
    for core_source in "$project_root"/src/*.cpp; do
        core_name=$(basename "$core_source" .cpp)
        clang++ \
            $common_flags \
            -isystem "$macos_sdk/usr/include/c++/v1" \
            -arch "$architecture" \
            -I"$project_root/include" \
            -c "$core_source" \
            -o "$architecture_root/$core_name.o"
    done
    libtool -static -o "$build_root/libqmw-$architecture.a" "$architecture_root"/*.o
}

build_core_archive arm64
build_core_archive x86_64
lipo -create \
    "$build_root/libqmw-arm64.a" \
    "$build_root/libqmw-x86_64.a" \
    -output "$build_root/libqmw-native.a"

build_external()
{
    external_name=$1
    wrapper_source=$2
    bundle="$project_root/package/QMW-Native/externals/$external_name.mxo"
    binary="$bundle/Contents/MacOS/$external_name"
    bundle_slug=$(printf '%s' "$external_name" | sed -e 's/\./-/g' -e 's/~/tilde/g')
    bundle_id="org.quantummusicworkstation.$bundle_slug"

    mkdir -p "$bundle/Contents/MacOS"
    sed \
        -e "s|@EXECUTABLE@|$external_name|g" \
        -e "s|@BUNDLE_ID@|$bundle_id|g" \
        "$project_root/resources/Info.plist.in" \
        > "$bundle/Contents/Info.plist"
    cp "$project_root/resources/PkgInfo" "$bundle/Contents/PkgInfo"
    clang++ \
        $common_flags \
        -isystem "$macos_sdk/usr/include/c++/v1" \
        -arch arm64 \
        -arch x86_64 \
        -bundle \
        -undefined dynamic_lookup \
        -I"$project_root/include" \
        -I"$include_root" \
        -I"$msp_include_root" \
        "$wrapper_source" \
        "$build_root/libqmw-native.a" \
        -o "$binary"

    codesign --sign - --force --deep "$bundle"
    file "$binary"
    nm -gU "$binary" | grep '_ext_main$'
    printf '%s\n' "QMW_MAX_EXTERNAL_BUILD_OK $binary"
}

build_external qmw.state "$project_root/source/qmw.state/qmw.state.cpp"
build_external qmw.hamiltonian "$project_root/source/qmw.hamiltonian/qmw.hamiltonian.cpp"
build_external qmw.pauli "$project_root/source/qmw.pauli/qmw.pauli.cpp"
build_external qmw.evolve "$project_root/source/qmw.evolve/qmw.evolve.cpp"
build_external qmw.observe "$project_root/source/qmw.observe/qmw.observe.cpp"
build_external qmw.uncertainty "$project_root/source/qmw.uncertainty/qmw.uncertainty.cpp"
build_external qmw.transition "$project_root/source/qmw.transition/qmw.transition.cpp"
build_external qmw.measure "$project_root/source/qmw.measure/qmw.measure.cpp"
build_external qmw.spectrum "$project_root/source/qmw.spectrum/qmw.spectrum.cpp"
build_external qmw.qmm "$project_root/source/qmw.qmm/qmw.qmm.cpp"
build_external qmw.flow "$project_root/source/qmw.flow/qmw.flow.cpp"
build_external 'qmw.resonator~' "$project_root/source/qmw.resonator~/qmw.resonator_tilde.cpp"
build_external 'qmw.interference~' "$project_root/source/qmw.interference~/qmw.interference_tilde.cpp"
build_external 'qmw.excite~' "$project_root/source/qmw.excite~/qmw.excite_tilde.cpp"
build_external 'qmw.lorentz~' "$project_root/source/qmw.lorentz~/qmw.lorentz_tilde.cpp"
build_external 'qmw.memory~' "$project_root/source/qmw.memory~/qmw.memory_tilde.cpp"
build_external 'qmw.modalbank~' "$project_root/source/qmw.modalbank~/qmw.modalbank_tilde.cpp"
