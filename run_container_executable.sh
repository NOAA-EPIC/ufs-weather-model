#!/bin/bash
set -x
export img=/scratch1/NCEPDEV/nems/role.epic/containers/ubuntu20.04-intel-spack-unified.img
export SINGULARITYENV_FI_PROVIDER=tcp
export SINGULARITY_SHELL=/bin/bash
export SINGULARITYENV_CMAKE_PREFIX_PATH=/opt/spack-stack/envs/unified/install/intel/2021.8.0/mapl-2.22.0-6ukxebu:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gftl-shared-1.5.0-5ngq5ou:/opt/spack-stack/envs/unified/install/intel/2021.8.0/w3emc-2.9.2-5yhfftj:/opt/spack-stack/envs/unified/install/intel/2021.8.0/sp-2.3.3-gnke6dy:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ip-3.3.3-ickkuw4:/opt/spack-stack/envs/unified/install/intel/2021.8.0/g2tmpl-1.10.2-vucq66q:/opt/spack-stack/envs/unified/install/intel/2021.8.0/g2-3.4.5-mkzxfsr:/opt/spack-stack/envs/unified/install/intel/2021.8.0/crtm-2.4.0-4ler5pk:/opt/spack-stack/envs/unified/install/intel/2021.8.0/bacio-2.4.1-ern2m6h:/opt/spack-stack/envs/unified/install/intel/2021.8.0/fms-2022.04-waygzlh:/opt/spack-stack/envs/unified/install/intel/2021.8.0/esmf-8.3.0b09-vwu2ghr:/opt/spack-stack/envs/unified/install/intel/2021.8.0/parallelio-2.5.9-prat5qr:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-fortran-4.6.0-eqojxed:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-c-4.9.2-7at3rmt:/opt/spack-stack/envs/unified/install/intel/2021.8.0/hdf5-1.14.0-2dqk7c2:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libpng-1.6.37-nr5najk:/opt/spack-stack/envs/unified/install/intel/2021.8.0/zlib-1.2.13-pmntgh3:/opt/spack-stack/envs/unified/install/intel/2021.8.0/jasper-2.0.32-6maoneq:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-mpi-2021.8.0-mwfbgmxe2rm3wd4uxwqmahnkwxnxf3yg:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pyproj-3.1.0-x5s4p7a:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pyparsing-3.0.9-m67dc3r:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pyhdf-0.10.4-bwr5nhq:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pycparser-2.21-xt4fzaq:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pycodestyle-2.8.0-otshcg3:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pybind11-2.8.1-xrstib4:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-protobuf-3.20.1-u3oiljk:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-poetry-core-1.0.8-d7rgl45:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-ply-3.11-nkr5wic:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pkgconfig-1.5.5-zjoy7xo:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pip-22.2.2-g42mt4c:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pillow-9.2.0-bycnbwk:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pep517-0.12.0-muv2jfa:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pandas-1.4.0-wl4ln5r:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-packaging-21.3-rlxyntl:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-numpy-1.22.3-s25xslf:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-numexpr-2.8.3-wl2n2in:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-netcdf4-1.5.3-vslcg6s:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-mysql-connector-python-8.0.13-4uwsips:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-mpi4py-3.1.4-d4cnpkp:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-meson-python-0.10.0-r5htcfe:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-matplotlib-3.6.2-ulwg26e:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-markupsafe-2.1.1-pskfgmy:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-kiwisolver-1.3.2-5bo2r7j:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-jmespath-1.0.1-ans6qyp:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-jinja2-3.1.2-4g3wxdm:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-h5py-3.6.0-oggpqho:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-gitpython-3.1.27-ensr7yu:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-gitdb-4.0.9-bps5hxh:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-gast-0.5.3-rmkjt52:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-fonttools-4.37.3-r3plfmj:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-flit-core-3.7.1-dnzibd7:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-findlibs-0.0.2-kzw6fpr:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-f90nml-1.4.3-3j44n4l:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-eccodes-1.4.2-ojtpugx:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-cython-0.29.32-bb3pq3o:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-cycler-0.11.0-p3tfujt:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-cppy-1.1.0-iql4ogo:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-contourpy-1.0.5-y445kr3:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-cftime-1.0.3.4-lptfitu:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-cffi-1.15.1-grzdg7e:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-certifi-2022.9.14-j3wfl5k:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-cartopy-0.21.1-pbr4f2k:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-build-0.7.0-7z7wead:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-bottleneck-1.3.5-d4yxrkg:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-botocore-1.29.26-vheruap:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-boto3-1.26.26-d543kgh:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-beniget-0.4.1-efyp42b:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-attrs-22.1.0-vclyec7:/opt/spack-stack/envs/unified/install/intel/2021.8.0/proj-8.1.0-33367qy:/opt/spack-stack/envs/unified/install/intel/2021.8.0/prod-util-1.2.2-rzhksxt:/opt/spack-stack/envs/unified/install/intel/2021.8.0/pkg-config-0.29.2-t4mn2oy:/opt/spack-stack/envs/unified/install/intel/2021.8.0/pcre2-10.42-l5x3aub:/opt/spack-stack/envs/unified/install/intel/2021.8.0/patchelf-0.16.1-omvlpj6:/opt/spack-stack/envs/unified/install/intel/2021.8.0/parallelio-2.5.9-iiji2wa:/opt/spack-stack/envs/unified/install/intel/2021.8.0/parallel-netcdf-1.12.2-kaooril:/opt/spack-stack/envs/unified/install/intel/2021.8.0/openjpeg-2.3.1-kln3h4u:/opt/spack-stack/envs/unified/install/intel/2021.8.0/openblas-0.3.19-3ruahfe:/opt/spack-stack/envs/unified/install/intel/2021.8.0/odc-1.4.5-lkeffvi:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ninja-1.11.1-sp2azj4:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-fortran-4.6.0-5ct2no7:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-cxx4-4.3.1-mndkqbk:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-c-4.9.0-hbcrud3:/opt/spack-stack/envs/unified/install/intel/2021.8.0/nemsiogfs-2.5.3-6mnbvkg:/opt/spack-stack/envs/unified/install/intel/2021.8.0/nemsio-2.5.2-nozpyp4:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ncview-2.1.8-3trwqm3:/opt/spack-stack/envs/unified/install/intel/2021.8.0/nco-5.0.6-mqg4dig:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ncio-1.1.2-km7czzf:/opt/spack-stack/envs/unified/install/intel/2021.8.0/nccmp-1.9.0.1-jp4x7ll:/opt/spack-stack/envs/unified/install/intel/2021.8.0/metplus-4.1.1-6za3jbr:/opt/spack-stack/envs/unified/install/intel/2021.8.0/met-10.1.1-3ipxxzn:/opt/spack-stack/envs/unified/install/intel/2021.8.0/meson-0.64.0-ijcudsy:/opt/spack-stack/envs/unified/install/intel/2021.8.0/mapl-2.22.0-kztuflq:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libxt-1.1.5-utg7agb:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libxpm-3.5.12-ape4uiv:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libxmu-1.1.2-mjniw2i:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libxcrypt-4.4.33-twxqtky:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libxaw-1.0.13-5ids7fe:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libtirpc-1.2.6-om6dwsw:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libmd-1.0.4-r3ckjoe:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libjpeg-turbo-2.1.0-ibo74yj:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libbsd-0.11.5-mfztpg5:/opt/spack-stack/envs/unified/install/intel/2021.8.0/landsfcutil-2.4.1-nrh7dht:/opt/spack-stack/envs/unified/install/intel/2021.8.0/krb5-1.20.1-hjxvq7l:/opt/spack-stack/envs/unified/install/intel/2021.8.0/nlohmann-json-schema-validator-2.1.0-3sn43ro:/opt/spack-stack/envs/unified/install/intel/2021.8.0/json-c-0.16-azubnip:/opt/spack-stack/envs/unified/install/intel/2021.8.0/nlohmann-json-3.10.5-znfjyqc:/opt/spack-stack/envs/unified/install/intel/2021.8.0/jedi-um-env-unified-dev-kwvezfq:/opt/spack-stack/envs/unified/install/intel/2021.8.0/jedi-ufs-env-unified-dev-vdm6od5:/opt/spack-stack/envs/unified/install/intel/2021.8.0/jedi-fv3-env-unified-dev-2tq4bws:/opt/spack-stack/envs/unified/install/intel/2021.8.0/jedi-ewok-env-unified-dev-dm75tvg:/opt/spack-stack/envs/unified/install/intel/2021.8.0/jedi-cmake-1.4.0-6uu44m7:/opt/spack-stack/envs/unified/install/intel/2021.8.0/jedi-base-env-1.0.0-r3wargq:/opt/spack-stack/envs/unified/install/intel/2021.8.0/hdf5-1.14.0-2fwc7dv:/opt/spack-stack/envs/unified/install/intel/2021.8.0/hdf-4.2.15-szjazjp:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gsl-lite-0.37.0-xkk6duw:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gsl-2.7.1-eigzvqy:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gsibec-1.0.7-4n6znwa:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gsi-ncdiag-1.0.0-ao5xtr2:/opt/spack-stack/envs/unified/install/intel/2021.8.0/grib-util-1.2.3-fo5yjxk:/opt/spack-stack/envs/unified/install/intel/2021.8.0/global-workflow-env-unified-dev-gg3knfx:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gftl-1.8.1-asnyyq6:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gfsio-1.4.1-6mgxjme:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gettext-0.21.1-yv6tp3m:/opt/spack-stack/envs/unified/install/intel/2021.8.0/geos-3.11.1-3aolbdf:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gdal-3.6.1-zjh3dhs:/opt/spack-stack/envs/unified/install/intel/2021.8.0/g2c-1.6.4-orfpiof:/opt/spack-stack/envs/unified/install/intel/2021.8.0/fms-2022.04-fwgkgzc:/opt/spack-stack/envs/unified/install/intel/2021.8.0/fiat-1.1.0-gzqdwjj:/opt/spack-stack/envs/unified/install/intel/2021.8.0/fftw-3.3.10-wvhpgvg:/opt/spack-stack/envs/unified/install/intel/2021.8.0/fckit-0.10.0-xk5odym:/opt/spack-stack/envs/unified/install/intel/2021.8.0/esmf-8.3.0b09-cov6luj:/opt/spack-stack/envs/unified/install/intel/2021.8.0/eigen-3.4.0-fejurrg:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ectrans-1.2.0-qrpf53c:/opt/spack-stack/envs/unified/install/intel/2021.8.0/eckit-1.20.2-s227q6t:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ecflow-5.8.4-nsmzvx2:/opt/spack-stack/envs/unified/install/intel/2021.8.0/eccodes-2.27.0-xdi6pcf:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ecbuild-3.6.5-mwvtdyj:/opt/spack-stack/envs/unified/install/intel/2021.8.0/crtm-fix-2.4.0_emc-ah7qkxr:/opt/spack-stack/envs/unified/install/intel/2021.8.0/crtm-2.4.0-67t6rbn:/opt/spack-stack/envs/unified/install/intel/2021.8.0/cdo-2.0.5-yjt3wf6:/opt/spack-stack/envs/unified/install/intel/2021.8.0/bufr-11.7.1-yoze47y:/opt/spack-stack/envs/unified/install/intel/2021.8.0/boost-1.78.0-taxlfh2:/opt/spack-stack/envs/unified/install/intel/2021.8.0/base-env-1.0.0-nl5j5oo:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ecmwf-atlas-0.32.1-5yizi4j:/opt/spack-stack/envs/unified/install/intel/2021.8.0/antlr-2.7.7-dw6u5hk:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-compilers-2023.0.0-r4v4wzb2nglaet3utty5gv6l2xyw2dox/compiler/2023.0.0/linux/IntelDPCPP:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-compilers-2023.0.0-r4v4wzb2nglaet3utty5gv6l2xyw2dox
export SINGULARITYENV_PATH=/opt/spack-stack/envs/unified/install/intel/2021.8.0/mapl-2.22.0-6ukxebu/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/esmf-8.3.0b09-vwu2ghr/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-fortran-4.6.0-eqojxed/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-c-4.9.2-7at3rmt/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/hdf5-1.14.0-2dqk7c2/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libpng-1.6.37-nr5najk/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/jasper-2.0.32-6maoneq/bin:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-mpi-2021.8.0-mwfbgmxe2rm3wd4uxwqmahnkwxnxf3yg/mpi/2021.8.0/libfabric/bin:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-mpi-2021.8.0-mwfbgmxe2rm3wd4uxwqmahnkwxnxf3yg/mpi/2021.8.0/bin:PATH=/opt/spack-stack/envs/unified/install/intel/2021.8.0/antlr-2.7.7-dw6u5hk/bin:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-compilers-2023.0.0-r4v4wzb2nglaet3utty5gv6l2xyw2dox/compiler/2023.0.0/linux/lib/oclfpga/bin:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-compilers-2023.0.0-r4v4wzb2nglaet3utty5gv6l2xyw2dox/compiler/2023.0.0/linux/bin/intel64:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-compilers-2023.0.0-r4v4wzb2nglaet3utty5gv6l2xyw2dox/compiler/2023.0.0/linux/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pyproj-3.1.0-x5s4p7a/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pycodestyle-2.8.0-otshcg3/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pybind11-2.8.1-xrstib4/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-pip-22.2.2-g42mt4c/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-numpy-1.22.3-s25xslf/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-netcdf4-1.5.3-vslcg6s/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-jmespath-1.0.1-ans6qyp/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-fonttools-4.37.3-r3plfmj/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-f90nml-1.4.3-3j44n4l/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-cython-0.29.32-bb3pq3o/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-cartopy-0.21.1-pbr4f2k/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/py-build-0.7.0-7z7wead/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/proj-8.1.0-33367qy/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/prod-util-1.2.2-rzhksxt/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/pkg-config-0.29.2-t4mn2oy/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/pcre2-10.42-l5x3aub/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/patchelf-0.16.1-omvlpj6/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/parallel-netcdf-1.12.2-kaooril/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/openblas-0.3.19-3ruahfe/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/odc-1.4.5-lkeffvi/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ninja-1.11.1-sp2azj4/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-fortran-4.6.0-5ct2no7/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-cxx4-4.3.1-mndkqbk/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-c-4.9.0-hbcrud3/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/nemsio-2.5.2-nozpyp4/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ncview-2.1.8-3trwqm3/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/nco-5.0.6-mqg4dig/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/nccmp-1.9.0.1-jp4x7ll/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/metplus-4.1.1-6za3jbr/ush:/opt/spack-stack/envs/unified/install/intel/2021.8.0/met-10.1.1-3ipxxzn/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/meson-0.64.0-ijcudsy/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/mapl-2.22.0-kztuflq/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libxpm-3.5.12-ape4uiv/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libjpeg-turbo-2.1.0-ibo74yj/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/krb5-1.20.1-hjxvq7l/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/nlohmann-json-schema-validator-2.1.0-3sn43ro/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/hdf5-1.14.0-2fwc7dv/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/hdf-4.2.15-szjazjp/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gsl-2.7.1-eigzvqy/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gsibec-1.0.7-4n6znwa/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gsi-ncdiag-1.0.0-ao5xtr2/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/grib-util-1.2.3-fo5yjxk/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gettext-0.21.1-yv6tp3m/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/geos-3.11.1-3aolbdf/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/gdal-3.6.1-zjh3dhs/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/fiat-1.1.0-gzqdwjj/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/fftw-3.3.10-wvhpgvg/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/fckit-0.10.0-xk5odym/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/esmf-8.3.0b09-cov6luj/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ectrans-1.2.0-qrpf53c/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/eckit-1.20.2-s227q6t/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ecflow-5.8.4-nsmzvx2/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ecbuild-3.6.5-mwvtdyj/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/cdo-2.0.5-yjt3wf6/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/bufr-11.7.1-yoze47y/bin:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ecmwf-atlas-0.32.1-5yizi4j/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local:/scratch1/NCEPDEV/stmp2/Mark.Potts/sandbox/ufs-weather-model/tests
export SINGULARITYENV_LD_LIBRARY_PATH=/opt/spack-stack/envs/unified/install/intel/2021.8.0/mapl-2.22.0-6ukxebu/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/w3emc-2.9.2-5yhfftj/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/sp-2.3.3-gnke6dy/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/ip-3.3.3-ickkuw4/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/g2tmpl-1.10.2-vucq66q/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/g2-3.4.5-mkzxfsr/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/crtm-2.4.0-4ler5pk/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/bacio-2.4.1-ern2m6h/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/fms-2022.04-waygzlh/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/esmf-8.3.0b09-vwu2ghr/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/parallelio-2.5.9-prat5qr/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-fortran-4.6.0-eqojxed/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/netcdf-c-4.9.2-7at3rmt/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/hdf5-1.14.0-2dqk7c2/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/libpng-1.6.37-nr5najk/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/zlib-1.2.13-pmntgh3/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/jasper-2.0.32-6maoneq/lib:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-mpi-2021.8.0-mwfbgmxe2rm3wd4uxwqmahnkwxnxf3yg/mpi/2021.8.0/libfabric/lib:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-mpi-2021.8.0-mwfbgmxe2rm3wd4uxwqmahnkwxnxf3yg/mpi/2021.8.0/lib/release:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-mpi-2021.8.0-mwfbgmxe2rm3wd4uxwqmahnkwxnxf3yg/mpi/2021.8.0/lib:/opt/spack-stack/envs/unified/install/intel/2021.8.0/antlr-2.7.7-dw6u5hk/lib:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-compilers-2023.0.0-r4v4wzb2nglaet3utty5gv6l2xyw2dox/compiler/2023.0.0/linux/lib:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-compilers-2023.0.0-r4v4wzb2nglaet3utty5gv6l2xyw2dox/compiler/2023.0.0/linux/lib/x64:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-compilers-2023.0.0-r4v4wzb2nglaet3utty5gv6l2xyw2dox/compiler/2023.0.0/linux/lib/oclfpga/host/linux64/lib:/opt/spack-stack/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.4.0/intel-oneapi-compilers-2023.0.0-r4v4wzb2nglaet3utty5gv6l2xyw2dox/compiler/2023.0.0/linux/compiler/lib/intel64_lin:/.singularity.d/libs:/.singularity.d/libs
cmd=$(basename "$0")
arg="$@"
echo running: singularity exec "${img}" $cmd $arg
/usr/bin/singularity exec -B /scratch1 -B /scratch1 -B //apps "${img}" $cmd $arg

