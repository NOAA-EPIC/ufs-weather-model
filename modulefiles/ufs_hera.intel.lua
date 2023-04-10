help([[
loads UFS Model prerequisites for Hera/Intel
]])



prepend_path("PATH", "/scratch1/NCEPDEV/stmp2/Mark.Potts/sandbox/ufs-weather-model/bin")

load("intel/2022.1.2")
load("impi/2022.1.2")
setenv("CC", "mpiicc")
setenv("CXX", "mpiicpc")
setenv("FC", "mpiifort")
setenv("CMAKE_Platform", "hera.intel")

whatis("Description: UFS build environment")
