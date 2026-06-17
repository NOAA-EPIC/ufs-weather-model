#!/bin/bash
set -eux

function trim {
    local var="$1"
    # remove leading whitespace characters
    var="${var#"${var%%[![:space:]]*}"}"
    # remove trailing whitespace characters
    var="${var%"${var##*[![:space:]]}"}"
    echo -n "${var}"
}


SECONDS=0

SCRIPT_REALPATH=$(realpath "${BASH_SOURCE[0]}")
MYDIR=$(dirname "${SCRIPT_REALPATH}")
readonly MYDIR

# ----------------------------------------------------------------------
# Parse arguments.

readonly ARGC=$#

if [[ ${ARGC} -lt 2 ]]; then
  echo "Usage: $0 MACHINE_ID [ MAKE_OPT ] [ COMPILE_ID ] [ RT_COMPILER ] [ clean_before ] [ clean_after ]"
  echo Valid MACHINE_IDs:
  echostuff=$( ls -1 ../cmake/configure_* )
  echostuff=${echostuff/:.*configure_::g}
  echostuff=${echostuff/:\.cmake::}
  echostuff=$( fold -sw72 <<< "${echostuff}" )
  exit 1
else
  MACHINE_ID=$1
  MAKE_OPT=${2:-}
  COMPILE_ID=${3:+$3}
  RT_COMPILER=${4:-intel}
  clean_before=${5:-YES}
  clean_after=${6:-YES}
fi

BUILD_NAME=fv3_${COMPILE_ID}

PATHTR=${PATHTR:-$( cd "${MYDIR}/.." && pwd )}
BUILD_DIR=${BUILD_DIR:-$(pwd)/build_${BUILD_NAME}}

# ----------------------------------------------------------------------
# Make sure we have reasonable number of threads.

if [[ ${MACHINE_ID} == derecho ]]; then
    BUILD_JOBS=${BUILD_JOBS:-3}
fi

BUILD_JOBS=${BUILD_JOBS:-8}

#hostname

set +x
if [[ ${USE_CONTAINER:-false} == true ]]; then
  source "${PATHTR}/tests/module-setup.sh"
  module use "${PATHTR}/modulefiles"
  module load "ufs_container.${RT_COMPILER}"
  module list
else
  case ${MACHINE_ID} in
    macosx|linux)
      # shellcheck source=/github/workspace/modulefiles/ufs_ursa.intelllvm.lua
      source "${PATHTR}/modulefiles/ufs_${MACHINE_ID}.${RT_COMPILER}"
      ;;
    *)
      source "${PATHTR}/tests/module-setup.sh"
      module use "${PATHTR}/modulefiles"
      module load "ufs_${MACHINE_ID}.${RT_COMPILER}"
      module list
      ;;
  esac
fi
set -x

echo "Compiling ${MAKE_OPT} into ${BUILD_NAME}.exe on ${MACHINE_ID}"

# set CMAKE_FLAGS based on $MAKE_OPT

CMAKE_FLAGS=${MAKE_OPT}
CMAKE_FLAGS+=" -DMPI=ON"

if [[ ${MAKE_OPT} == *-DDEBUG=ON* ]]; then
  CMAKE_FLAGS+=" -DCMAKE_BUILD_TYPE=Debug"
else
  CMAKE_FLAGS+=" -DCMAKE_BUILD_TYPE=Release"
fi

if [[ ${MACHINE_ID} == wcoss2 ]] || [[ ${MACHINE_ID} == acorn ]]; then
    CMAKE_FLAGS+=" -DENABLE_PARALLELRESTART=ON"
fi

# Check if suites argument is provided or not
set +ex
SUITES=$(grep -Po "\-DCCPP_SUITES=\K[^ ]*" <<< "${MAKE_OPT}")
export SUITES
set -ex

CMAKE_FLAGS=$(set -e; trim "${CMAKE_FLAGS}")
echo "CMAKE_FLAGS = ${CMAKE_FLAGS}"

[[ ${clean_before} = YES ]] && rm -rf "${BUILD_DIR}"

export BUILD_VERBOSE=1
export BUILD_DIR
export BUILD_JOBS
export CMAKE_FLAGS

bash -x "${PATHTR}/build.sh"

rsync --remove-source-files "${BUILD_DIR}/ufs_model" "${PATHTR}/tests/${BUILD_NAME}.exe"

if [[ ${MACHINE_ID} == linux ]]; then
  cp "${PATHTR}/modulefiles/ufs_${MACHINE_ID}.${RT_COMPILER}" "${PATHTR}/tests/modules.${BUILD_NAME}"
else
  cp "${PATHTR}/modulefiles/ufs_${MACHINE_ID}.${RT_COMPILER}.lua" "${PATHTR}/tests/modules.${BUILD_NAME}.lua"
fi

if [[ ${USE_CONTAINER:-false} == true ]]; then
  cp "${PATHTR}/modulefiles/ufs_container.runtime.lua" "${PATHTR}/tests/modules.runtime.lua"
fi

[[ ${clean_after} == YES ]] && rm -rf "${BUILD_DIR}"

elapsed=${SECONDS}
echo "Elapsed time ${elapsed} seconds. Compiling ${CMAKE_FLAGS} finished"
echo "Compile ${COMPILE_ID} elapsed time ${elapsed} seconds. ${CMAKE_FLAGS}" > "compile_${COMPILE_ID}_time.log"
