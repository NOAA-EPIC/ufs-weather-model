#!/bin/bash -x

export PATH=$PATH:~/bin
echo "USER=${USER}"
echo "WORKSPACE=${WORKSPACE}"
export ACCNR=epic

export account="-a ${ACCNR}"
export workflow="-e"
	#[[ ${UFS_PLATFORM} =  jet         ]] && workflow="-r"
	#[[ ${UFS_PLATFORM} =  hera        ]] && workflow="-r"
	#[[ ${UFS_PLATFORM} =~ clusternoaa ]] && workflow=""

export opt="-l"
export suite="rt.conf"
	[[ -n ${WM_OPERATIONAL_TESTS}                 ]] && opt="-n" && suite="${WM_OPERATIONAL_TESTS} ${UFS_COMPILER}" || return 0
	[[    ${WM_OPERATIONAL_TESTS} = default       ]] && opt="-n" && suite="control_p8 ${UFS_COMPILER}"
	[[    ${WM_OPERATIONAL_TESTS} = comprehensive ]] && opt="-l" && suite="rt.conf"
	[[    ${WM_OPERATIONAL_TESTS} = rt.conf       ]] && opt="-l" && suite="rt.conf"
	[[   "${suite}"               = rt.conf       ]] && opt="-l"

set -eu

export machine=${NODE_NAME}

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

pwd
ls -al .cicd/*
ls -al ${TESTS_DIR}/rt.sh

function regression_test() {
	local machine=${1:-${NODE_NAME}}
	local machine_id=${machine,,} # tolower
	local WORKSPACE="$(pwd)"
	local status=0

	git submodule update --init --recursive
	pwd
	ls -al .cicd/*
	cd tests
		pwd

		[[ ${UFS_PLATFORM} =~ clusternoaa ]] && echo "export BL_DATE=20240426" > bl_date.conf || cat bl_date.conf

		mkdir -p logs/
		export BL_DATE=$(cat bl_date.conf | cut -d '=' -f2)

		if [[ $machine =~ "Jet" ]]
		then
		    echo "Running regression tests on $machine"
		    export dprefix=/lfs1/NAGAPE/$ACCNR/$USER
		    sed 's|/lfs4/HFIP/${ACCNR}/${USER}|/lfs4/HFIP/hfv3gfs/${USER}|g' -i rt.sh
		    local workflow="-r"
		    ./rt.sh -a ${ACCNR} ${workflow} ${opt} "${suite}" | tee $WORKSPACE/tests/logs/RT-run-$machine.log
		    status=${PIPESTATUS[0]}
		elif [[ $machine =~ "Hercules" ]]
		then
		    echo "Running regression tests on $machine"
		    export dprefix=/work2/noaa/$ACCNR/$USER
		    sed "s|/noaa/stmp/|/noaa/$ACCNR/stmp/|g" -i rt.sh
		    export ACCNR=epic
		    ./rt.sh -a ${ACCNR} ${workflow} ${opt} "${suite}" | tee $WORKSPACE/tests/logs/RT-run-$machine.log
		    status=${PIPESTATUS[0]}
		    cd logs/
		    cp RegressionTests_${machine_id}.log $(dirname $WORKSPACE) #/work/noaa/epic/role-epic/jenkins/workspace
		    git remote -v
		    git fetch --no-recurse-submodules origin
		    git reset FETCH_HEAD --hard
		    cd .. && cd .. && cd ..
		    pwd
		    cp $(dirname $WORKSPACE)/RegressionTests_${machine_id}.log $WORKSPACE/tests/logs/
		    cd $WORKSPACE/tests/
		elif [[ $machine =~ "Orion" ]]
		then
		    echo "Running regression tests on $machine"
		    cd ..
		    #module load git/2.28.0
			git --version
		    git submodule update --init --recursive
		    cd tests
		    export dprefix=/work2/noaa/$ACCNR/$USER
		    sed "s|/noaa/stmp/|/noaa/$ACCNR/stmp/|g" -i rt.sh
		    ./rt.sh -a ${ACCNR} ${workflow} ${opt} "${suite}" | tee $WORKSPACE/tests/logs/RT-run-$machine.log
		    status=${PIPESTATUS[0]}
		    cd logs/
		    cp RegressionTests_${machine_id}.log $(dirname $WORKSPACE) #/work/noaa/epic/role-epic/jenkins/workspace
		    git remote -v
		    git fetch --no-recurse-submodules origin
		    git reset FETCH_HEAD --hard
		    cd .. && cd .. && cd ..
		    pwd
		    cp $(dirname $WORKSPACE)/RegressionTests_${machine_id}.log $WORKSPACE/tests/logs/
		    cd $WORKSPACE/tests/
		elif [[ $machine =~ "Gaea" ]]
		then
		    echo "Running regression tests on $machine"
		    ./rt.sh -a ${ACCNR} ${workflow} ${opt} "${suite}" | tee $WORKSPACE/tests/logs/RT-run-$machine.log
		    status=${PIPESTATUS[0]}
		    unset LD_LIBRARY_PATH
		    cd logs/
		    cp RegressionTests_${machine_id}.log $(dirname $WORKSPACE) #/gpfs/f5/epic/scratch/role.epic/jenkins/workspace
		    git remote -v
		    git fetch --no-recurse-submodules origin
		    git reset FETCH_HEAD --hard
		    cd .. && cd .. && cd ..
		    pwd
		    cp $(dirname $WORKSPACE)/RegressionTests_${machine_id}.log $WORKSPACE/tests/logs/
		    cd $WORKSPACE/tests/
		elif [[ $machine =~ "Hera" ]]
		then
		    echo "Running regression tests on $machine"
		    export ACCNR=epic
		    sed "s|QUEUE=batch|QUEUE=windfall|g" -i rt.sh
		    local workflow="-r"
		    ./rt.sh -a ${ACCNR} ${workflow} ${opt} "${suite}" | tee $WORKSPACE/tests/logs/RT-run-$machine.log
		    status=${PIPESTATUS[0]}
		    cd logs/
		    cp RegressionTests_${machine_id}.log $(dirname $WORKSPACE) #/scratch2/NAGAPE/epic/role.epic/jenkins/workspace
		    git remote -v
		    git fetch --no-recurse-submodules origin
		    git reset FETCH_HEAD --hard
		    cd .. && cd .. && cd ..
		    pwd
		    cp $(dirname $WORKSPACE)/RegressionTests_${machine_id}.log $WORKSPACE/tests/logs/
		    cd $WORKSPACE/tests/
		elif [[ $machine =~ "Derecho" ]]
		then
		    echo "Running regression tests on $machine"
		    export ACCNR=nral0032
		    ./rt.sh -a ${ACCNR} ${workflow} ${opt} "${suite}" | tee $WORKSPACE/tests/logs/RT-run-$machine.log
		    status=${PIPESTATUS[0]}
		    cd logs/
		    cp RegressionTests_${machine_id}.log $(dirname $WORKSPACE) #/glade/derecho/scratch/epicufsrt/jenkins/workspace
		    git remote -v
		    git fetch --no-recurse-submodules origin
		    git reset FETCH_HEAD --hard
		    cd .. && cd .. && cd ..
		    pwd
		    cp $(dirname $WORKSPACE)/RegressionTests_${machine_id}.log $WORKSPACE/tests/logs/
		    cd $WORKSPACE/tests/
		else
		    echo "Running regression tests on $machine"
		    local workflow="-r"
		    ./rt.sh -a ${ACCNR} ${workflow} ${opt} "${suite}" | tee $WORKSPACE/tests/logs/RT-run-$machine.log
		    status=${PIPESTATUS[0]}
		fi

	cd ${WORKSPACE}

	echo "Testing concluded for $machine. status=$status"
	return $status
}

function post_test() {
	echo "Testing concluded...removing labels for $machine from $GIT_URL"
	echo $CHANGE_ID
	export SSH_ORIGIN=$(curl --silent https://api.github.com/repos/ufs-community/ufs-weather-model/pulls/$CHANGE_ID | jq -r '.head.repo.ssh_url')
	export FORK_BRANCH=$(curl --silent https://api.github.com/repos/ufs-community/ufs-weather-model/pulls/$CHANGE_ID | jq -r '.head.ref')
	echo "GIT_URL=${GIT_URL}"
	git config user.email "ecc.platform@noaa.gov"
	git config user.name "epic-cicd-jenkins"
	export machine_name_logs=$(echo $machine | awk '{ print tolower($1) }')

	#git remote -v | grep -w sshorigin > /dev/null 2>&1 && git remote remove sshorigin > /dev/null 2>&1
	#git remote add sshorigin $SSH_ORIGIN > /dev/null 2>&1
	#git add logs/RegressionTests_$machine_name_logs.log
	#git commit -m "[AutoRT] $machine Job Completed.\n\n\n on-behalf-of @ufs-community <ecc.platform@noaa.gov>"
	#git pull sshorigin $FORK_BRANCH
	#git push sshorigin HEAD:$FORK_BRANCH

	tar --create --gzip --verbose --dereference --file "${machine_name_logs}.tgz" ${WORKSPACE}/tests/logs/*.log

	GIT_OWNER=$(echo $GIT_URL | cut -d '/' -f4)
	GIT_REPO_NAME=$(echo $GIT_URL | cut -d '/' -f5 | cut -d '.' -f1)

	#curl --silent -X DELETE -H "Accept: application/vnd.github.v3+json" -H "Authorization: Bearer ${GITHUB_TOKEN}"  https://api.github.com/repos/${GIT_OWNER}/${GIT_REPO_NAME}/issues/${CHANGE_ID}/labels/$machine-RT
}

regression_test ${machine}
