#!/bin/bash

PYTHON=python3
SCRIPT_DIR=$(cd $(dirname $BASH_SOURCE); pwd)

export PYTHONPATH=$SCRIPT_DIR/src:$SCRIPT_DIR/test

PYCRAFT="$PYTHON $SCRIPT_DIR/src/pycraft/main.py"
ANALYZER="$PYTHON $SCRIPT_DIR/src/pycraft/client/analyzer.py"
TSHARK2PYCRAFT="$PYTHON $SCRIPT_DIR/src/pycraft/client/tshark2pycraft.py"
TEST_GENERATOR="$PYTHON $SCRIPT_DIR/test/pycraft_test/util/generator.py"

alias pycraft="$PYCRAFT"
alias analyze="$ANALYZER > packet.txt"
alias tshark2pycraft="$TSHARK2PYCRAFT $1"
alias gen_test="cat packet.log | $TEST_GENERATOR $1 > test_code.txt"
