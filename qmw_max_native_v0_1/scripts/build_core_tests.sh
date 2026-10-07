#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
build_dir="$project_root/build/core"
mkdir -p "$build_dir"
run_dir=$(mktemp -d "$build_dir/run.XXXXXX")
object_dir="$run_dir/objects"
macos_sdk=$(xcrun --sdk macosx --show-sdk-path)
mkdir -p "$object_dir"

common_flags="-std=c++20 -O2 -Wall -Wextra -Werror -pedantic"

for core_source in "$project_root"/src/*.cpp; do
    core_name=$(basename "$core_source" .cpp)
    clang++ \
        $common_flags \
        -isystem "$macos_sdk/usr/include/c++/v1" \
        -I"$project_root/include" \
        -c "$core_source" \
        -o "$object_dir/$core_name.o"
done

libtool -static -o "$run_dir/libqmw-native.a" "$object_dir"/*.o

for test_source in "$project_root"/tests/test_*agent_core.cpp "$project_root/tests/test_state.cpp"; do
    test_name=$(basename "$test_source" .cpp)
    test_binary="$run_dir/$test_name"
    clang++ \
        $common_flags \
        -isystem "$macos_sdk/usr/include/c++/v1" \
        -I"$project_root/include" \
        "$test_source" \
        "$run_dir/libqmw-native.a" \
        -o "$test_binary"
    "$test_binary"
done

python3 -m unittest discover -s "$project_root/tests" -p 'test_*wrapper.py' -v
printf '%s\n' "QMW_ALL_CORE_AND_WRAPPER_CONTRACT_TESTS_OK $run_dir"
