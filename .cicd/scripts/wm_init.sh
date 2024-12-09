#!/bin/bash
set -eu
export UFS_PLATFORM=${UFS_PLATFORM:-${NODE_NAME,,}}
export UFS_COMPILER=${UFS_COMPILER:-intel}

SCRIPT_REALPATH=$(realpath "${BASH_SOURCE[0]}")
SCRIPTS_DIR=$(dirname "${SCRIPT_REALPATH}")
UFS_MODEL_DIR=$(realpath "${SCRIPTS_DIR}/../..")
readonly UFS_MODEL_DIR
echo "UFS MODEL DIR: ${UFS_MODEL_DIR}"

export CC=${CC:-mpicc}
export CXX=${CXX:-mpicxx}
export FC=${FC:-mpif90}

BUILD_DIR=${BUILD_DIR:-${UFS_MODEL_DIR}/build}
TESTS_DIR=${TESTS_DIR:-${UFS_MODEL_DIR}/tests}

cd "${UFS_MODEL_DIR}"
pwd
echo "UFS_PLATFORM=<${UFS_PLATFORM}>"
echo "UFS_COMPILER=<${UFS_COMPILER}>"
