#!/usr/bin/env bash

export MACHINE_ID="${MACHINE_ID:-container}"
echo "Define env. variables to run UFS WM for MACHINE_ID=$MACHINE_ID"

export RT_COMPILER="${RT_COMPILER:-gnu}"
echo "RT_COMPILER=$RT_COMPILER " 
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export RT_COMPILER="$INPUT"
    echo "Using RT_COMPILER=$RT_COMPILER"
fi

export TPN="${TPN:-192}"
echo "TPN=$TPN"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export TPN="$INPUT"
    echo "Using TPN=$TPN"
fi

export COMPILE_ID="${COMPILE_ID:-atm}"
echo "COMPILE_ID=$COMPILE_ID " 
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export COMPILE_ID="$INPUT"
    echo "Using COMPILE_ID=$COMPILE_ID"
fi

export TEST_NAME="${TEST_NAME:-control_p8}"
echo "TEST_NAME=$TEST_NAME"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export TEST_NAME="$INPUT"
    echo "Using TEST_NAME=$TEST_NAME"
fi

export TEST_ID="${TEST_NAME}_${RT_COMPILER}"
echo "TEST_ID=$TEST_ID"

PARENT_DIR="$(cd .. && pwd)"
export PATHTR=$PARENT_DIR
echo "PATHTR=$PATHTR"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export PATHTR="$INPUT"
    echo "Using PATHTR=$PATHTR"
fi

export PATHRT="${PATHTR}/tests"
export RUNDIR_ROOT="${PATHTR}/tests/run_container"
echo "RUNDIR_ROOT=$RUNDIR_ROOT"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export RUNDIR_ROOT="$INPUT"
    echo "Using RUNDIR_ROOT=$RUNDIR_ROOT"
fi

export SCHEDULER="${SCHEDULER:-slurm}"
echo "SCHEDULER=$SCHEDULER"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export SCHEDULER="$INPUT"
    echo "Using SCHEDULER=$SCHEDULER"
fi

export DISKNM="${DISKNM:-/contrib/ufs-weather-model/RT}"
echo "DISKNM=$DISKNM"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export DISKNM="$INPUT"
    echo "Using DISKNM=$DISKNM"
fi

export INPUTDATA_ROOT="${INPUTDATA_ROOT:-${DISKNM}/NEMSfv3gfs/input-data-20251015}"
echo "INPUTDATA_ROOT=$INPUTDATA_ROOT"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export INPUTDATA_ROOT="$INPUT"
    echo "Using INPUTDATA_ROOT=$INPUTDATA_ROOT"
fi

export INPUTDATA_ROOT_WW3="${INPUTDATA_ROOT_WW3:-${INPUTDATA_ROOT}/WW3_input_data_20250807}"
echo "INPUTDATA_ROOT_WW3=$INPUTDATA_ROOT_WW3"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export INPUTDATA_ROOT_WW3="$INPUT"
    echo "Using INPUTDATA_ROOT_WW3=$INPUTDATA_ROOT_WW3"
fi

export INPUTDATA_GFSv17opn="${INPUTDATA_GFSv17opn:-${DISKNM}/NEMSfv3gfs/GFSv17opn_20251014}"
echo "INPUTDATA_GFSv17opn=$INPUTDATA_GFSv17opn"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export INPUTDATA_GFSv17opn="$INPUT"
    echo "Using INPUTDATA_GFSv17opn=$INPUTDATA_GFSv17opn"
fi

export RTVERBOSE="${RTVERBOSE:-false}"
echo "RTVERBOSE=$RTVERBOSE"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export RTVERBOSE="$INPUT"
    echo "Using RTVERBOSE=$RTVERBOSE"
fi

export ROCOTO="false"
export skip_check_results="true"

