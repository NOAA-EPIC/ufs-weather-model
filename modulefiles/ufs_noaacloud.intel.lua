help([[
loads UFS Model prerequisites for noaacloud/intel
]])


prepend_path("MODULEPATH", "/contrib/Cameron.Book/sw/spack-stack-1.2.0/envs/unified-env-2/install/modulefiles/Core")

load("stack-intel")
load("stack-intel-oneapi-mpi")
--load("stack-python")
load("cmake")

load("ufs_common_spack")

setenv("CC", "mpiicc")
setenv("CXX", "mpiicpc")
setenv("FC", "mpiifort")
setenv("CMAKE_Platform", "noaacloud.intel")

whatis("Description: UFS build environment")


