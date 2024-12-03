#!/bin/bash -x
set -eu

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

(
	cd "${TESTS_DIR}"
	pwd
	ls -al ./rt.sh
)

pwd
echo "NODE_NAME=${NODE_NAME}"
echo "USER=${USER}"
echo "UFS_PLATFORM=<${UFS_PLATFORM}>"
echo "UFS_COMPILER=<${UFS_COMPILER}>"
echo "WM_REGRESSION_TESTS=<${WM_REGRESSION_TESTS}>"
echo "WM_OPERATIONAL_TESTS=<${WM_OPERATIONAL_TESTS}>"
echo "WM_CREATE_BASELINE=<${WM_CREATE_BASELINE}>"
workspace=$(pwd)
export workflow
machine=${NODE_NAME}
echo "machine=<${machine}>"
machine_id=${UFS_PLATFORM}
if [[ ${UFS_PLATFORM} =~ clusternoaa ]] ; then
	machine_id="noaacloud"
	#sed -i -e "s|EPIC/spack-stack/spack-stack-1.5.0|spack-stack/spack-stack-1.5.1|g" modulefiles/ufs_noaacloud.intel.lua
fi
echo "machine_id=<${machine_id}>"

status=0

export LMOD_SH_DBG_ON=0
echo "LMOD_VERSION=${LMOD_VERSION}"

ls -l build/ufs_model || : # just checking
status=$?

[[ -n "${WM_REGRESSION_TESTS}"    ]] || WM_REGRESSION_TESTS=true     # default
#[[ ${UFS_PLATFORM} == jet         ]] && WM_REGRESSION_TESTS=false   # takes too long
#[[ ${UFS_PLATFORM} == derecho     ]] && WM_REGRESSION_TESTS=false
[[ ${UFS_PLATFORM} =~ clusternoaa ]] && WM_REGRESSION_TESTS=false || :
export WM_REGRESSION_TESTS

rm -f ${workspace}/wm_test_results-${UFS_PLATFORM}-${UFS_COMPILER}.txt
if [[ ${WM_REGRESSION_TESTS} = true ]] ; then
	echo "Pipeline Reqression Tests on ${UFS_PLATFORM} starting."

	set +x
	if [[ ${UFS_PLATFORM} = orion ]] ; then
		#module --ignore_cache load git/2.28.0
		git --version
		git submodule update --init --recursive
	fi

	if [[ ${UFS_PLATFORM} = gaea ]] ; then
		source /gpfs/f5/epic/scratch/role.epic/contrib/Lmod_init_C5.sh
		echo "LMOD_VERSION=${LMOD_VERSION}"
	fi

	module use ${PWD}/modulefiles >/dev/null 2>&1
	module load ufs_${machine_id}.${UFS_COMPILER} || true
	[[ ${UFS_PLATFORM} = gaea ]] && module load cmake/3.23.1
	module list
	set -x

	#export PATH=$PATH:~/bin
	echo "CHANGE_ID=${CHANGE_ID:-null}"

	#export ACCNR=epic
	echo "ACCNR=${ACCNR}"

	export FV3_RT_DIR=
	#export JENKINS_WORKSPACE=
	#workflow="-e" # -e = ecflow (default) || -r = rocoto

	opt="-l"
	suite="rt.conf"
	[[ -n ${WM_OPERATIONAL_TESTS}                 ]] && opt="-n" && suite="${WM_OPERATIONAL_TESTS} ${UFS_COMPILER}"
	[[    ${WM_OPERATIONAL_TESTS} = default       ]] && opt="-n" && suite="control_p8 ${UFS_COMPILER}"
	[[    ${WM_OPERATIONAL_TESTS} = comprehensive ]] && opt="-l" && suite="rt.conf"
	[[    ${WM_OPERATIONAL_TESTS} = rt.conf       ]] && opt="-l" && suite="rt.conf"
	[[ ${suite} = rt.conf ]] && opt="-l"

	[[ ${WM_CREATE_BASELINE} = true   ]] && BL_DATE=$(cut -d '=' -f2 tests/bl_date.conf)
        export BL_DATE
	[[ ! -f tests/logs/RegressionTests_${UFS_PLATFORM,,}.log ]] || mv tests/logs/RegressionTests_${UFS_PLATFORM,,}.log tests/logs/RegressionTests_${UFS_PLATFORM,,}.log.orig

	rm -f ${workspace}/${UFS_PLATFORM}-${UFS_COMPILER}-wm_*-log.txt
	umask 002
	if [[ ${WM_CREATE_BASELINE} = true ]] ; then
		echo "start Creating baseline on ${UFS_PLATFORM} ..."
		ls -al .cicd/*
		echo "Pipeline Creating Baseline Tests ${suite} on ${UFS_PLATFORM} ${UFS_COMPILER}: (${opt} [${suite:=rt.conf}])"
		/usr/bin/time -p \
			-o ${workspace}/${UFS_PLATFORM}-${UFS_COMPILER}-time-wm_test.json \
			-f '{\n  "cpu": "%P"\n, "memMax": "%M"\n, "mem": {"text": "%X", "data": "%D", "swaps": "%W", "context": "%c", "waits": "%w"}\n, "pagefaults": {"major": "%F", "minor": "%R"}\n, "filesystem": {"inputs": "%I", "outputs": "%O"}\n, "time": {"real": "%e", "user": "%U", "sys": "%S"}\n}' \
			./.cicd/scripts/create_baseline.sh | tee -a ${workspace}/${UFS_PLATFORM}-${UFS_COMPILER}-wm_test-log.txt
		status=${PIPESTATUS[0]}
		echo "Pipeline Completed Baseline Tests ${opt} ${suite} on ${UFS_PLATFORM} ${UFS_COMPILER}. status=${status}"
	else
		echo "skip Creating baseline on ${UFS_PLATFORM}."
		ls -al .cicd/*
		echo "Pipeline Running Regression Tests ${suite} on ${UFS_PLATFORM} ${UFS_COMPILER}: (${opt} [${suite:=rt.conf}])"
		/usr/bin/time -p \
			-o ${workspace}/${UFS_PLATFORM}-${UFS_COMPILER}-time-wm_test.json \
			-f '{\n  "cpu": "%P"\n, "memMax": "%M"\n, "mem": {"text": "%X", "data": "%D", "swaps": "%W", "context": "%c", "waits": "%w"}\n, "pagefaults": {"major": "%F", "minor": "%R"}\n, "filesystem": {"inputs": "%I", "outputs": "%O"}\n, "time": {"real": "%e", "user": "%U", "sys": "%S"}\n}' \
			./.cicd/scripts/regression_test.sh | tee -a ${workspace}/${UFS_PLATFORM}-${UFS_COMPILER}-wm_test-log.txt
		status=${PIPESTATUS[0]}
		echo "Pipeline Completed Regression Tests ${opt} ${suite} on ${UFS_PLATFORM} ${UFS_COMPILER}. status=${status}"
	fi

	cd tests/
	pwd
	ls -al .
	## Check for log files ...
	ls -al logs/.
	ls -al ${WORKSPACE:-"${workspace}/.."}/${machine_id}/tests/logs/. || :

	## Test Results ...
	echo "ExperimentName: ${suite}" | tee -a ${workspace}/${UFS_PLATFORM}-${UFS_COMPILER}-wm_test-log.txt | tee    ${workspace}/wm_test_results-${UFS_PLATFORM}-${UFS_COMPILER}.txt
	grep -E " DIRECTORY: |Time: | Completed: |Result: " logs/RegressionTests_${UFS_PLATFORM,,}.log        | tee -a ${workspace}/wm_test_results-${UFS_PLATFORM}-${UFS_COMPILER}.txt
	grep -E " -- COMPILE | -- TEST "                    logs/RegressionTests_${UFS_PLATFORM,,}.log        | tee -a ${workspace}/wm_test_results-${UFS_PLATFORM}-${UFS_COMPILER}.txt

	cd ${workspace}
	find ${workspace}/tests/logs -ls
	echo "Pipeline Reqression Tests on ${UFS_PLATFORM} complete. status=${status}"
else
	echo "Pipeline Regression Tests on ${UFS_PLATFORM} (${machine}) skipped."
	echo "ExperimentName: null" > ${workspace}/wm_test_results-${UFS_PLATFORM}-${UFS_COMPILER}.txt
fi
exit ${status}
