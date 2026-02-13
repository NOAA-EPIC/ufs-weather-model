import os
import sys
import subprocess
import yaml
from datetime import datetime
#import datetime
from ufs_test_utils import get_testcase, write_logfile, delete_files, machine_check_off, process_compile_log, process_test_log, finalize_regression_log
from runtime_env import EnvConfig

env = EnvConfig()

def finish_log():
    """Collect regression test results and generate log file.
    """
    run_logs= f"""
"""
    compile_pass= 0
    compile_nr  = 0
    job_nr = 0
    pass_nr= 0
    fail_nr= 0
    failed_list= []
    test_changes_list= env.pathrt+'/test_changes.list'
    with open(env.ufs_test_yaml, 'r') as f:
        rt_yaml = yaml.load(f, Loader=yaml.FullLoader)
        for apps, jobs in rt_yaml.items():
            for key, val in jobs.items():
                if (str(key) == 'build'):
                    rt_compiler = val['compiler']
                    Ccompile_id  = apps
                    machine_check = machine_check_off(env.machine_id, val)
                    pass_tests = False
                    if machine_check:
                        compile_nr += 1
                        rt_compiler = val['compiler']
                        compile_id = apps
                        compile_log, passed = process_compile_log(env.machine_id, compile_id, rt_compiler, env.pathrt)
                        run_logs += compile_log
                        if passed:
                            compile_pass += 1
                if (str(key) == 'tests' and env.compile_only == 'false' and not pass_tests):
                    for test in val:
                        case, config = get_testcase(test)
                        machine_check = machine_check_off(env.machine_id, config)
                        if machine_check:
                            job_nr+=1
                            test_log, passed, failed_name = process_test_log(env.machine_id, case, rt_compiler, config)
                            run_logs += test_log
                            if passed:
                                pass_nr += 1
                            else:
                                fail_nr += 1
                                failed_list.append(failed_name + " " + rt_compiler)
                    run_logs += '\n'
    
    finalize_regression_log(env, run_logs, compile_pass, compile_nr, job_nr, pass_nr, fail_nr, failed_list, test_changes_list)
   
    print("Performing Cleanup...")
    exefiles= env.pathrt+'/fv3_*.*x*'; delete_files(exefiles)
    modfiles= env.pathrt+'/modules.fv3_*'; delete_files(modfiles)
    modfiles= env.pathrt+'modulefiles/modules.fv3_*'; delete_files(modfiles)
    tmpfiles= env.pathrt+'/keep_tests.tmp'; delete_files(tmpfiles)
    if env.keep_rundir == 'false':
        rundir = env.pathrt+'/run_dir'
        os.unlink(rundir)
    if env.rocoto == 'true':
        rocotofiles=env.pathrt+'/rocoto*'
        delete_files(rocotofiles)
        lockfiles=env.pathrt+'/*_lock.db'
        delete_files(lockfiles)
    print("REGRESSION TEST RESULT: SUCCESS")    

#if __name__ == '__main__':
