#!/usr/bin/env bash

export MACHINE_ID="${MACHINE_ID:-container}"
echo "Define env. variables to build the UFS WM for MACHINE_ID=$MACHINE_ID"

  if [[ -n "${APPTAINER_CONTAINER:-}" ]]; then
     export CONTAINER=APPTAINER

  elif [[ -n "${SINGULARITY_CONTAINER:-}" ]]; then
     export CONTAINER=SINGULARITY
  else
     printf "ERROR: MACHINE=container is defined\n" >&2
     printf "  but no expected container environment variables found \n" >&2
     exit 65
  fi

export RT_COMPILER="${RT_COMPILER:-gnu}"
echo "RT_COMPILER=$RT_COMPILER " 
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export RT_COMPILER="$INPUT"
    echo "Using RT_COMPILER=$RT_COMPILER"
fi

export COMPILE_ID="${COMPILE_ID:-atm}"
echo "COMPILE_ID=$COMPILE_ID" 
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export COMPILE_ID="$INPUT"
    echo "Using COMPILE_ID=$COMPILE_ID"
fi

export MAKE_OPT="${MAKE_OPT:-"-DAPP=ATM -DCCPP_SUITES=FV3_GFS_v16,FV3_GFS_v16_flake,FV3_GFS_v16_ras,FV3_GFS_v17_p8,FV3_GFS_v17_p8_ugwpv1"}"
echo "MAKE_OPT=$MAKE_OPT"
read -p "  ...press Enter to keep, or type new value (no quotes): " INPUT
if [[ -n "$INPUT" ]]; then
    export MAKE_OPT="$INPUT"
    echo "Using MAKE_OPT=$MAKE_OPT"
fi

