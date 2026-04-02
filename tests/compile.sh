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

# When using a container, save build environment for the runtime in ufswm.env
env_vars () {

  local vars_file="$1"
cat >"${vars_file}" <<EOF_ENV
PATH=${UFS_BIN}:${PATH}  # Add a directory with ufs_model binary to the search path
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}
HDF5_PLUGIN_PATH=${HDF5_PLUGIN_PATH:-}
HDF5_USE_FILE_LOCKING=FALSE
ESMFMKFILE=${ESMFMKFILE:-}
CRTM_FIX=${CRTM_FIX}

EOF_ENV
}

# Singularity/apptainer containers: make a wrapper script of the UFS WM binary
ufs_binary_wrapper() {
  local bind_dir="$(echo "${PATHTR}" | cut -d'/' -f1-2)"  # local directory to bind for the container
  local wrapper="$1"
  if [[ -n "${BIND_ADD:-}" ]]; then
     local bind_add="-B ${BIND_ADD}"
  fi
  local ufs_env=${UFS_ENV:-}
  local container=${CONTAINER^^}
  local containerbin=${CONTAINER,,}

# Start EOF_WRAP
cat >"${wrapper}" <<EOF_WRAP
#!/bin/bash
set -x

export ${container}ENV_FI_PROVIDER=tcp
export ${container}_SHELL=/bin/bash

img=${SINGULARITY_CONTAINER:-/path/to/container/image.sif}
cmd=\$(basename "\$0")

EOF_WRAP

# Add compiler specific variables to EOF_WRAP
if [[ ${RT_COMPILER} == intel ]]; then
    cat >>"${wrapper}" <<EOF_WRAP
export ${container}FI_PROVIDER_PATH=${FI_PROVIDER_PATH}    
EOF_WRAP
elif [[ ${RT_COMPILER} == gnu ]]; then
    cat >>"${wrapper}" <<EOF_WRAP
export ${container}ENV_PMIX_MCA_gds=hash
export ${container}ENV_PMIX_MCA_psec=native
export ${container}ENV_OMPI_MCA_btl="^openib"

if ip link show eth0 &>/dev/null; then
    export ${container}ENV_OMPI_MCA_btl_tcp_if_include=eth0
    export ${container}ENV_OMPI_MCA_oob_tcp_if_include=eth0
fi

export ${container}ENV_OMPI_MCA_pml=ob1
export ${container}ENV_OMPI_MCA_btl_vader_single_copy_mechanism=none
export ${container}ENV_OMPI_MCA_mca_base_component_show_load_errors=0
EOF_WRAP
fi

# Complete EOF_WRAP
cat >>"${wrapper}" <<EOF_WRAP

CONTAINERBIN=\$(which ${containerbin})

"\${CONTAINERBIN}" exec --env-file ${ufs_env} \
-B ${bind_dir} ${bind_add:-} \${img} \$cmd 

EOF_WRAP

    chmod +x "${wrapper}"
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
case ${MACHINE_ID} in
  macosx|linux)
    source "${PATHTR}/modulefiles/ufs_${MACHINE_ID}.${RT_COMPILER}"
    ;;
  *)
    source "${PATHTR}/tests/module-setup.sh"
    # Load fv3 module
    module use "${PATHTR}/modulefiles"
    modulefile="ufs_${MACHINE_ID}.${RT_COMPILER}"
    module load "${modulefile}"
    module list
    ;;
esac
set -x

echo "Compiling ${MAKE_OPT} into ${BUILD_NAME}.exe on ${MACHINE_ID}"

# set CMAKE_FLAGS based on $MAKE_OPT

CMAKE_FLAGS=${MAKE_OPT}
CMAKE_FLAGS+=" -DMPI=ON"

if [[ ${MAKE_OPT} == *-DDEBUG=ON* ]]; then
  CMAKE_FLAGS+=" -DCMAKE_BUILD_TYPE=Debug"
else
  CMAKE_FLAGS+=" -DCMAKE_BUILD_TYPE=Release"
  if [[ ${MACHINE_ID} == jet ]] && [[ ${RT_COMPILER} == intel ]]; then
    CMAKE_FLAGS+=" -DSIMDMULTIARCH=ON"
  fi
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

if [[ ${MACHINE_ID} == container ]]; then
  export UFS_ENV="${PATHTR}/tests/ufswm.env"               # environment file for the runtime
  export UFS_WRAP="${PATHTR}/tests/ufs_model.sh"           # wrapper for the ufs_model executable
  export UFS_BIN="${PATHTR}/tests" # location of actual ufs_model binary
  # Address setup diffs. for SINGULARITY vs APPTAINER, depending on a ${CONTAINER} env. variable set explicitly (SINGULARITY is the default)
  export CONTAINER="${CONTAINER:-SINGULARITY}"
  env_vars ${UFS_ENV}              # create an env. file
  ufs_binary_wrapper ${UFS_WRAP}   # create a binary wrapper
  cp "${PATHTR}/modulefiles/ufs_container.runtime.lua" "${PATHTR}/tests/modules.runtime.lua"
fi

[[ ${clean_after} == YES ]] && rm -rf "${BUILD_DIR}"

elapsed=${SECONDS}
echo "Elapsed time ${elapsed} seconds. Compiling ${CMAKE_FLAGS} finished"
echo "Compile ${COMPILE_ID} elapsed time ${elapsed} seconds. ${CMAKE_FLAGS}" > "compile_${COMPILE_ID}_time.log"
