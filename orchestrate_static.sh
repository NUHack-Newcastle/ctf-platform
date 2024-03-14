#!/usr/bin/env bash
if [ -z "${FLAG}" ]; then
    >&2 echo "Error: FLAG variable is not set or is empty."
    exit 1
fi
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SOURCE_DIR="$(realpath "$1")"
export FLAG_GEN_C_SCRIPT="$(realpath "$SCRIPT_DIR/flag_generation/generate_flag_gen_c.py")"

if [[ ! -s "$SOURCE_DIR/name" ]]; then
  >&2 echo "Could not find name for challenge in directory $SOURCE_DIR"
  exit 1
fi

NAME=$(cat "$SOURCE_DIR/name")
>&2 echo "Found challenge $NAME"

WORK_DIR=$(mktemp -d)

if [[ ! "$WORK_DIR" || ! -d "$WORK_DIR" ]]; then
  >&2 echo "Could not create temp dir"
  exit 1
fi

>&2 echo "Made working directory $WORK_DIR"
cd "$WORK_DIR" || { >&2 echo "Could not cd into temp dir" && exit 1; }

if [[ ! -s "$SOURCE_DIR/setup" ]]; then
  >&2 echo "Challenge does not have a setup script, skipping"
else
  >&2 echo "Running setup script"
  "$SOURCE_DIR/setup" || { >&2 echo "Setup script failed" && rm -rf "$WORK_DIR" && exit 1; }
fi

if [[ ! -s "$SOURCE_DIR/build" ]]; then
  >&2 echo "Challenge does not have a build script, skipping"
else
  >&2 echo "Running build script"
  "$SOURCE_DIR/build" || { >&2 echo "Build script failed" && rm -rf "$WORK_DIR" && exit 1; }
fi

cd "$SCRIPT_DIR"

# success!
>&2 echo "Build succeeded as far as we know!"
echo "$WORK_DIR"