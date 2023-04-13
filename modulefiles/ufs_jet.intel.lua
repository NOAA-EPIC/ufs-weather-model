help([[
loads UFS Model prerequisites for Hera/Intel
]])



prepend_path("PATH", "/mnt/lfs4/HFIP/hfv3gfs/Mark.Potts/sandbox/ufs-weather-model/bin")

load("intel/2022.1.2")
load("impi/2022.1.2")
setenv("CC", "mpiicc")
setenv("CXX", "mpiicpc")
setenv("FC", "mpiifort")
setenv("CMAKE_Platform", "jet.intel")

whatis("Description: UFS build environment")
