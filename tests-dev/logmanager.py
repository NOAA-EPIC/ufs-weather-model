import os
import yaml
from datetime import datetime
from ufs_test_utils import get_testcase, write_logfile, delete_files, machine_check_off

class RegressionLogManager:
    """
    Manages regression test logging for the UFS weather model.
    Parses compile and test logs, tracks statistics, and generates summary reports.
    """
    def __init__(self):
        self.pathrt = os.getenv("PATHRT")
        self.machine_id = os.getenv("MACHINE_ID")
        self.yaml_path = os.getenv("UFS_TEST_YAML")
        self.keep_rundir = os.getenv("KEEP_RUNDIR") == "true"
        self.rocoto = os.getenv("ROCOTO") == "true"
        self.create_baseline = os.getenv("CREATE_BASELINE") == "true"
        self.compile_only = os.getenv("COMPILE_ONLY") == "true"
        self.logfile = os.path.join(self.pathrt, f"logs/RegressionTests_{self.machine_id}.log")
        self.test_changes_list = os.path.join(self.pathrt, "test_changes.list")
        self.run_logs = ""
        self.stats = {
            "compile_pass": 0,
            "compile_total": 0,
            "job_total": 0,
            "test_pass": 0,
            "test_fail": 0,
            "failed_tests": []
        }

    def get_timestamps(self, path):
        """
        Extracts the earliest and latest modification timestamps from files in a given directory.

        Args:
            path (str): Directory path containing log files.

        Returns:
            tuple[str, str]: ISO-formatted strings for earliest and latest timestamps.
        """        
        timestamps = [datetime.fromtimestamp(os.path.getmtime(os.path.join(path, f))) for f in os.listdir(path)]
        return str(min(timestamps)), str(max(timestamps))

    def parse_compile_log(self, app, val):
        """
        Parses a compile log to determine success, extract timing and warning info,
        and update compile statistics.

        Args:
            app (str): Application name used as compile identifier.
            val (dict): Dictionary containing compiler configuration and metadata.

        Side Effects:
            Updates self.stats and appends formatted result to self.run_logs.
        """
        if not machine_check_off(self.machine_id, val):
            return
        self.stats["compile_total"] += 1
        compiler = val["compiler"]
        compile_id = app
        log_dir = os.path.join(self.pathrt, f"logs/log_{self.machine_id}")
        compile_log = f"compile_{compile_id}.log"
        timestamp_file = f"compile_{compile_id}_timestamp.txt"
        compile_path = os.path.join(log_dir, compile_log)
        timestamp_path = os.path.join(log_dir, timestamp_file)

        check1 = f"Compile {compile_id} Completed"
        check2 = "[100%] Linking Fortran executable"

        try:
            with open(compile_path) as f:
                contents = f.read()
                if check1 in contents or check2 in contents:
                    self.stats["compile_pass"] += 1
                    f.seek(0)
                    for line in f:
                        if "export RUNDIR_ROOT=" in line:
                            rundir_root = line.split("=")[1].strip()
                            break

                    err_path = os.path.join(rundir_root, f"compile_{compile_id}", "err")
                    with open(err_path) as ferr:
                        err_contents = ferr.read()
                        warnings = err_contents.count(": warning #")
                        remarks = err_contents.count(": remark #")

                    with open(timestamp_path) as flog:
                        timing_data = flog.read().split('\n', 1)[0]
                        fields = timing_data.split(",")
                        etime = int(fields[4].strip()) - int(fields[1].strip())
                        btime = int(fields[3].strip()) - int(fields[2].strip())
                        etime_min, etime_sec = divmod(etime, 60)
                        btime_min, btime_sec = divmod(btime, 60)

                    time_log = f" [{etime_min:02}:{etime_sec:02}, {btime_min:02}:{btime_sec:02}]"
                    warn_log = f"({warnings} warnings, {remarks} remarks)"
                    result = f"PASS -- COMPILE {compile_id}{time_log}{warn_log}\n"
                else:
                    result = f"FAIL -- COMPILE {compile_id}\n"
        except FileNotFoundError:
            print(f"{compile_path}: does not exist")
            result = f"FAIL -- COMPILE {compile_id}\n"

        self.run_logs += result

    def parse_test_log(self, test, config, compiler):
        """
        Parses a test log to determine pass/fail status, extract timing and memory usage,
        and update test statistics.

        Args:
            test (str): Test case name.
            config (dict): Configuration dictionary for the test.
            compiler (str): Compiler identifier used in the test.

        Side Effects:
            Updates self.stats and appends formatted result to self.run_logs.
        """        
        if not machine_check_off(self.machine_id, config):
            return
        self.stats["job_total"] += 1
        test_id = f"{test}_{compiler}"
        test_log = f"rt_{test_id}.log"
        timestamp_file = f"run_{test_id}_timestamp.txt"
        log_dir = os.path.join(self.pathrt, f"logs/log_{self.machine_id}")
        test_path = os.path.join(log_dir, test_log)
        timestamp_path = os.path.join(log_dir, timestamp_file)

        pass_check = f"Test {test_id} PASS"
        mem_check = "The maximum resident set size (KB)"
        try:
            with open(test_path) as f:
                contents = f.read()
                if pass_check in contents:
                    with open(timestamp_path) as tf:
                        timing_data = tf.read().split('\n', 1)[0]
                        fields = timing_data.split(",")
                        etime = int(fields[4].strip()) - int(fields[1].strip())
                        rtime = int(fields[3].strip()) - int(fields[2].strip())
                        etime_min, etime_sec = divmod(etime, 60)
                        rtime_min, rtime_sec = divmod(rtime, 60)
                        time_log = f" [{etime_min:02}:{etime_sec:02}, {rtime_min:02}:{rtime_sec:02}]"

                    memsize = "N/A"
                    with open(test_path) as f:
                        for line in f:
                            if mem_check in line:
                                memsize = line.split("=")[1].strip()
                                break
                    self.stats["test_pass"] += 1
                    result = f"PASS -- TEST {test_id}{time_log} ({memsize} MB)\n"
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            self.stats["test_fail"] += 1
            self.stats["failed_tests"].append(f"{test} {compiler}")
            result = f"FAIL -- TEST {test_id}\n"

        self.run_logs += result

    def summarize(self):
        """
        Generates a summary report of compile and test results, including timing and pass/fail counts.

        Returns:
            str: Multi-line formatted summary string.
        """        
        start, end = self.get_timestamps(os.path.join(self.pathrt, f"logs/log_{self.machine_id}/"))
        elapsed = datetime.strptime(end.split('.')[0], "%Y-%m-%d %H:%M:%S") - \
                  datetime.strptime(start.split('.')[0], "%Y-%m-%d %H:%M:%S")
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"""
SYNOPSIS:
Starting Date/Time: {start}
Ending Date/Time: {end}
Total Time: {int(hours):02}h:{int(minutes):02}m:{int(seconds):02}s
Compiles Completed: {self.stats['compile_pass']}/{self.stats['compile_total']}
Tests Completed: {self.stats['test_pass']}/{self.stats['job_total']}
"""

    def finalize(self):
        """
        Finalizes the regression test log by writing results and summary to disk.
        Cleans up temporary files and rundir if configured.

        Side Effects:
            Writes to self.logfile and test_changes.list.
            Deletes temporary files and directories.
            Prints final result to stdout.
        """        
        write_logfile(self.logfile, "a", output=self.run_logs)
        write_logfile(self.logfile, "a", output=self.summarize())

        if self.stats["test_fail"] == 0:
            if os.path.isfile(self.test_changes_list):
                delete_files(self.test_changes_list)
            open(self.test_changes_list, 'a').close()
            result = "SUCCESS"
        else:
            with open(self.test_changes_list, 'w') as f:
                for line in self.stats["failed_tests"]:
                    f.write(f"{line}\n")
            result = "FAILURE"

        comment_log = f"""
NOTES:
A file test_changes.list was generated {'but is empty' if result == 'SUCCESS' else 'with list of all failed tests'}.
If you are using this log as a pull request verification, please commit test_changes.list.
Result: {result}
====END OF {self.machine_id} REGRESSION TESTING LOG====
"""
        write_logfile(self.logfile, "a", output=comment_log)

        print("Performing Cleanup...")
        delete_files(os.path.join(self.pathrt, "fv3_*.*x*"))
        delete_files(os.path.join(self.pathrt, "modules.fv3_*"))
        delete_files(os.path.join(self.pathrt, "modulefiles/modules.fv3_*"))
        delete_files(os.path.join(self.pathrt, "keep_tests.tmp"))
        if not self.keep_rundir:
            os.unlink(os.path.join(self.pathrt, "run_dir"))
        if self.rocoto:
            delete_files(os.path.join(self.pathrt, "rocoto*"))
        delete_files(os.path.join(self.pathrt, "*_lock.db"))

        print(f"REGRESSION TEST RESULT: {result}")

    def run(self):
        """
        Executes the full regression logging workflow:
        parses YAML test configuration, processes compile and test logs,
        and finalizes the output.

        Side Effects:
            Populates self.stats and writes logs to disk.
        """        
        with open(self.yaml_path, "r") as f:
            rt_yaml = yaml.load(f, Loader=yaml.FullLoader)

        for app, jobs in rt_yaml.items():
            for key, val in jobs.items():
                if key == "build":
                     rt_compiler = val['compiler']
                     self.parse_compile_log(app, val)
                elif key == "tests" and not self.compile_only:
                    for test in val:
                        case, config = get_testcase(test)
                        self.parse_test_log(case, config, rt_compiler)

        self.finalize()
      
def run_regression_logging():
    """
    Entry point for executing regression logging via the RegressionLogManager class.
    """    
    from logmanager import RegressionLogManager  # adjust import if needed
    logger = RegressionLogManager()
    logger.run()
