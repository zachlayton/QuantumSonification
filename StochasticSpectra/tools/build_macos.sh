#!/bin/bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "usage: $0 /absolute/path/to/max-sdk-base" >&2
    exit 64
fi

sdk_root=$1
script_dir=$(cd "$(dirname "$0")" && pwd)
package_dir=$(cd "$script_dir/.." && pwd)
build_dir="$package_dir/build-macos"
apple_sdk=$(xcrun --show-sdk-path)
cxx=${CXX:-$(xcrun --find clang++)}
deployment_target=${MACOSX_DEPLOYMENT_TARGET:-11.0}

required=(
    "$sdk_root/script/max-linker-flags.txt"
    "$sdk_root/script/PkgInfo"
    "$sdk_root/c74support/max-includes/ext.h"
    "$sdk_root/c74support/msp-includes/z_dsp.h"
    "$sdk_root/c74support/msp-includes/MaxAudioAPI.framework"
    "$sdk_root/c74support/jit-includes/JitterAPI.framework"
)
for path in "${required[@]}"; do
    if [[ ! -e "$path" ]]; then
        echo "missing Max SDK dependency: $path" >&2
        exit 66
    fi
done

arch_flags=()
for arch in ${ARCHS:-arm64 x86_64}; do
    arch_flags+=("-arch" "$arch")
done

mkdir -p "$build_dir"

build_external() {
    local object_name=$1
    local source_folder=$2
    local source_file=$3
    local source_dir="$package_dir/source/$source_folder"
    local target_build_dir="$build_dir/$source_folder"
    local bundle="$package_dir/externals/$object_name.mxo"
    local binary="$bundle/Contents/MacOS/$object_name"
    local object_file="$target_build_dir/$source_folder.o"

    mkdir -p "$target_build_dir" "$bundle/Contents/MacOS"
    "$cxx" \
        -std=c++17 -O3 -DNDEBUG -fPIC \
        "${arch_flags[@]}" \
        -isysroot "$apple_sdk" \
        "-mmacosx-version-min=$deployment_target" \
        -isystem "$apple_sdk/usr/include/c++/v1" \
        -I "$sdk_root/c74support" \
        -I "$sdk_root/c74support/max-includes" \
        -I "$sdk_root/c74support/msp-includes" \
        -I "$sdk_root/c74support/jit-includes" \
        -c "$source_dir/$source_file" \
        -o "$object_file"

    xargs "$cxx" \
        -bundle \
        "${arch_flags[@]}" \
        -isysroot "$apple_sdk" \
        "-mmacosx-version-min=$deployment_target" \
        "$object_file" \
        -F "$sdk_root/c74support/msp-includes" -framework MaxAudioAPI \
        -F "$sdk_root/c74support/jit-includes" -framework JitterAPI \
        -o "$binary" \
        < "$sdk_root/script/max-linker-flags.txt"

    cp "$source_dir/Info.plist" "$bundle/Contents/Info.plist"
    cp "$sdk_root/script/PkgInfo" "$bundle/Contents/PkgInfo"
    codesign --force --deep --sign - "$bundle"

    echo "built $bundle"
    lipo -info "$binary"
    codesign --verify --deep --strict --verbose=2 "$bundle"
}

build_external "stochspectra~" "stochspectra_tilde" "stochspectra_tilde.cpp"
build_external "stochpacketenv~" "stochpacketenv_tilde" "stochpacketenv_tilde.cpp"
