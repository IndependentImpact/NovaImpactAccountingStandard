#!/usr/bin/env bash

load_nias_env() {
  local root_dir="$1"
  local env_path="$root_dir/.env"

  if [ -f "$env_path" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$env_path"
    set +a
  fi

  if [ -n "${NIAS_TMP_DIR:-}" ]; then
    case "$NIAS_TMP_DIR" in
      "~") NIAS_TMP_DIR="$HOME" ;;
      "~/"*) NIAS_TMP_DIR="$HOME/${NIAS_TMP_DIR#~/}" ;;
    esac
    mkdir -p "$NIAS_TMP_DIR"
    export NIAS_TMP_DIR
    export TMPDIR="$NIAS_TMP_DIR"
    export TEMP="$NIAS_TMP_DIR"
    export TMP="$NIAS_TMP_DIR"
  fi
}
