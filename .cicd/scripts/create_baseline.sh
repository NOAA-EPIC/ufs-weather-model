#!/bin/bash -x
set -eu

echo "USER=${USER}"
echo "WORKSPACE=${WORKSPACE}"
                       export machine=${NODE_NAME}
                            export ACCNR=epic

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

function create_baseline() {
	opt="-l"
	suite="rt.conf"
	[[ -n ${WM_OPERATIONAL_TESTS}                 ]] && opt="-n" && suite="${WM_OPERATIONAL_TESTS} ${UFS_COMPILER}" || return 0
	[[    ${WM_OPERATIONAL_TESTS} = default       ]] && opt="-n" && suite="control_p8 ${UFS_COMPILER}"
	[[    ${WM_OPERATIONAL_TESTS} = comprehensive ]] && opt="-l" && suite="rt.conf"
	[[    ${WM_OPERATIONAL_TESTS} = rt.conf       ]] && opt="-l" && suite="rt.conf"
	[[ ${suite} = rt.conf ]] && opt="-l"

                       git submodule update --init --recursive
                       pwd
		       ls -al .cicd/*
                       cd tests
		       pwd
                       export machine=${NODE_NAME}
                       export PATH=$PATH:~/bin
		       export BL_DATE=$(cat bl_date.conf | cut -d '=' -f2)

                          if [[ $machine =~ "Jet" ]] 
                          then
                            echo "Creating baselines on $machine"
                            export dprefix=/lfs1/NAGAPE/$ACCNR/$USER
                            ./rt.sh -a ${ACCNR} -c -r ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
                          elif [[ $machine =~ "Hercules" ]]
                          then
                            echo "Creating baselines on $machine"
                            export dprefix=/work2/noaa/$ACCNR/$USER
                            sed "s|/noaa/stmp/|/noaa/$ACCNR/stmp/|g" -i rt.sh
                            export ACCNR=epic
                            ./rt.sh -a ${ACCNR} -c -e ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
                            export DISKNM=/work/noaa/epic/hercules/UFS-WM_RT
			    cd ${DISKNM}/NEMSfv3gfs/
			    mkdir develop-${BL_DATE}
			    cd /work2/noaa/epic/stmp/role-epic/stmp/role-epic/FV3_RT
			    rsync -a REGRESSION_TEST/ ${DISKNM}/NEMSfv3gfs/develop-${BL_DATE}
                            cd ${DISKNM}/NEMSfv3gfs/
                            ./adjust_permissions.sh hercules develop-${BL_DATE}
                            chgrp noaa-hpc develop-${BL_DATE}
		            cd $WORKSPACE/tests
                            ./rt.sh -a ${ACCNR} -e ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
			    cd logs/
                            cp RegressionTests_hercules.log /work/noaa/epic/role-epic/jenkins/workspace
                            git remote -v
                            git fetch --no-recurse-submodules origin
                            git reset FETCH_HEAD --hard
                            cd .. && cd .. && cd ..
			    cp RegressionTests_hercules.log $WORKSPACE/tests/logs/
                            cd $WORKSPACE/tests/
                          elif [[ $machine =~ "Orion" ]]
                          then
                            cd ..
                            module load git/2.28.0
                            git submodule update --init --recursive
                            cd tests
                            echo "Creating baselines on $machine"
                            export dprefix=/work2/noaa/$ACCNR/$USER
                            sed -i 's|/work/noaa/stmp/${USER}|/work/noaa/epic/stmp/role-epic/|g' rt.sh
		            export ACCNR=epic
                            ./rt.sh -a ${ACCNR} -c -e ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
                            export DISKNM=/work/noaa/epic/UFS-WM_RT
                            cd ${DISKNM}/NEMSfv3gfs/
                            mkdir develop-${BL_DATE}
                            cd  /work/noaa/epic/stmp/role-epic/stmp/role-epic/FV3_RT/
                            rsync -a REGRESSION_TEST/ ${DISKNM}/NEMSfv3gfs/develop-${BL_DATE}
                            cd ${DISKNM}/NEMSfv3gfs/
                            ./adjust_permissions.sh orion develop-${BL_DATE}
                            chgrp noaa-hpc develop-${BL_DATE}
			    cd $WORKSPACE/tests
                            ./rt.sh -a ${ACCNR} -e ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
                             cd logs/
                             cp RegressionTests_orion.log /work/noaa/epic/role-epic/jenkins/workspace
                             git remote -v
                             git fetch --no-recurse-submodules origin
                             git reset FETCH_HEAD --hard
                             cd .. && cd .. && cd ..
			     cp RegressionTests_orion.log $WORKSPACE/tests/logs/
			     cd $WORKSPACE/tests/
                          elif [[ $machine =~ "Gaea" ]]
                          then 
                            echo "Creating baselines on $machine"
                            ./rt.sh -a ${ACCNR} -c -e ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
                            unset LD_LIBRARY_PATH
                            export DISKNM=/gpfs/f5/epic/world-shared/UFS-WM_RT
                            cd ${DISKNM}/NEMSfv3gfs/
                            mkdir develop-${BL_DATE}
                            cd /gpfs/f5/epic/scratch/role.epic/FV3_RT
                            rsync -a REGRESSION_TEST/ ${DISKNM}/NEMSfv3gfs/develop-${BL_DATE}
                            cd ${DISKNM}/NEMSfv3gfs/
                            chgrp ncep develop-${BL_DATE}
		            cd $WORKSPACE/tests
                            ./rt.sh -a ${ACCNR} -e ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
			    cd logs/
			    cp RegressionTests_gaea.log /gpfs/f5/epic/scratch/role.epic/jenkins/workspace
			    git remote -v
                            git fetch --no-recurse-submodules origin
                            git reset FETCH_HEAD --hard
                            cd .. && cd .. && cd ..
			    cp RegressionTests_gaea.log $WORKSPACE/tests/logs/
			    cd $WORKSPACE/tests/
                          elif [[ $machine =~ "Hera" ]]
                          then
                            echo "Creating baselines on $machine"
                            export ACCNR=epic
                            ./rt.sh -a ${ACCNR} -c -r ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
                            export DISKNM=/scratch2/NAGAPE/epic/UFS-WM_RT
			    cd ${DISKNM}/NEMSfv3gfs/
			    mkdir develop-${BL_DATE}
			    cd  /scratch1/NCEPDEV/stmp4/role.epic/FV3_RT
			    rsync -a REGRESSION_TEST/ ${DISKNM}/NEMSfv3gfs/develop-${BL_DATE}
			    cd $WORKSPACE/tests
                            ./rt.sh -a ${ACCNR} -r ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
			     cd logs/
			     cp RegressionTests_hera.log /scratch2/NAGAPE/epic/role.epic/jenkins/workspace
			     git remote -v
                             git fetch --no-recurse-submodules origin
                             git reset FETCH_HEAD --hard
                             cd .. && cd .. && cd ..
			     cp RegressionTests_hera.log $WORKSPACE/tests/logs/
			     cd $WORKSPACE/tests/
                           elif [[ $machine =~ "Derecho" ]]
                           then
                             echo "Creating baselines on $machine"
                             export ACCNR=nral0032
                             ./rt.sh -a ${ACCNR} -c -e ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
                             export DISKNM=/glade/derecho/scratch/epicufsrt/ufs-weather-model/RT/
			     cd ${DISKNM}/NEMSfv3gfs/
			     mkdir develop-${BL_DATE}
			     cd /glade/derecho/scratch/epicufsrt/FV3_RT
			     rsync -a REGRESSION_TEST/ ${DISKNM}/NEMSfv3gfs/develop-${BL_DATE}
			     cd $WORKSPACE/tests
                             ./rt.sh -a ${ACCNR} -e ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
			     cd logs/
			     cp RegressionTests_derecho.log /glade/derecho/scratch/epicufsrt/jenkins/workspace
			     git remote -v
                             git fetch --no-recurse-submodules origin
                             git reset FETCH_HEAD --hard
                             cd .. && cd .. && cd ..
                             cp RegressionTests_derecho.log $WORKSPACE/tests/logs/
                             cd $WORKSPACE/tests/
                          else
                            echo "Creating baselines on $machine"
                            ./rt.sh -a ${ACCNR} -c -r ${opt} ${suite} | tee $WORKSPACE/tests/logs/RT-run-$machine.log
                          fi
                      echo "Testing concluded for $machine"
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

                      #curl --silent -X DELETE -H "Accept: application/vnd.github.v3+json" -H "Authorization: Bearer ${GITHUB_TOKEN}"  https://api.github.com/repos/${GIT_OWNER}/${GIT_REPO_NAME}/issues/${CHANGE_ID}/labels/$machine-BL
}

