help([[
loads UFS Model prerequisites for noaacloud/intel
]])


prepend_path("MODULEPATH", "/contrib/EPIC/spack-stack/spack-stack-1.3.0/envs/unified-dev/install/modulefiles/Core")

load("stack-intel")
load("stack-intel-oneapi-mpi")
load("ufs-weather-model-env/unified-dev")
load("w3emc")

--load("ufs_common_spack")

setenv("CC", "mpiicc")
setenv("CXX", "mpiicpc")
setenv("FC", "mpiifort")
setenv("CMAKE_Platform", "noaacloud.intel")

whatis("Description: UFS build environment")


