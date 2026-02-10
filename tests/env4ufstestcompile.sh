#!/usr/bin/env bash

export COMPILE_ID="${COMPILE_ID:-atm}"
echo "COMPILE_ID = $COMPILE_ID" 
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export COMPILE_ID="$INPUT"
    echo "Using COMPILE_ID=$COMPILE_ID"
fi

export MACHINE_ID="${MACHINE_ID:-container}"
echo "MACHINE_ID = $MACHINE_ID"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export MACHINE_ID="$INPUT"
    echo "Using MACHINE_ID=$MACHINE_ID"
fi

export RT_COMPILER="${RT_COMPILER:-gnu}"
echo "RT_COMPILER = $RT_COMPILER " 
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export RT_COMPILER="$INPUT"
    echo "Using RT_COMPILER=$RT_COMPILER"
fi

MAKE_OPT="  -DAPP=ATM -DCCPP_SUITES=FV3_GFS_v16,FV3_GFS_v16_flake,FV3_GFS_v16_ras,FV3_GFS_v17_p8,FV3_GFS_v17_p8_ugwpv1"
export MAKE_OPT="${MAKE_OPT:-}"
echo "MAKE_OPT = $MAKE_OPT"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export MAKE_OPT="$INPUT"
    echo "Using MAKE_OPT=$MAKE_OPT"
fi

export IMG="${IMG:-/work/noaa/epic/nperlin/scratch/orion/CONTAINERS/rocky9-gcc13-ss192.sif}"
echo "IMG = $IMG"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export IMG="$INPUT"
    echo "Using IMG=$IMG"
fi

export CONTAINER="${CONTAINER:-singularity}"
echo "CONTAINER = $CONTAINER" 
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export CONTAINER="$INPUT"
    echo "Using CONTAINER=$CONTAINER"
fi

export BIND_ADD="${BIND_ADD:-/local}"
echo "BIND_ADD = $BIND_ADD"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export BIND_ADD="$INPUT"
    echo "Using BIND_ADD=$BIND_ADD"
fi

