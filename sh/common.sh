#!/bin/bash

function c8 {
  cut -c1-8 <<< "$1"
}

function word1 {
    cut -f1 -d' ' <<<"$1";
}

function local_py_exec {
    py="$1";
    shift;
    python3 "$(dirname "$0")/../py/$py" $@;
}

function run_with_choice {
    cmd="$1"
    shift
    choices=$(for c in "$@"; do echo "$c"; done)
    nl -w2 -s '. ' <<<"$choices"
    read -p '? ' choice
    n=$(wc -l <<<"$choices")
    if [[ -z "$choice" ]]; then
        echo Cancelled
    elif (("$choice" >= 1 && "$choice" <= $n)); then
        choice=$(sed "${choice}q;d" <<<"$choices")
        bash -c "$cmd '$choice'"
    else
        echo Invalid choice
        return 1
    fi
}
