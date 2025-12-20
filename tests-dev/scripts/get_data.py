import os
import json
from .Log import Log
from .create_images import *
from .utilities import *

"""This script contains a main() function that gets log information from GitHub using the APICall class 
and extracts data from the RegressionTest_<machine>.log files for each machine. 
"""

def main():
   """For each machine, create a log object, get current PR data, gather historical runtime/memory data, 
   and compare results to determine which test/machine combinations fall more than 2 standard deviations 
   above the historical mean for each test.""" 

   machines = os.environ.get('MACHINES').split()

   # Contains commit hashes (most recent PR hash, then most recent develop hashes from most to least recent) for each machine
   hashes = {}
   # Contains runtime/memory data by machine for the last 50 commits
   historical_runtime_memory = {}
   # Contains mean and standard deviation for each test on each machine
   stats_by_machine = {}
   # Contains information on whether test runtime was more than 2 standard deviations above the mean. 
   runtime_results_by_machine = {}
   # Contains information on whether test memory was more than 2 standard deviations above the mean. 
   mem_results_by_machine = {}
   
   hashes = get_hashes(50) # Change to 50
   
   for machine in machines:
      print(machine.upper())
      log = Log(machine)
      log.repo_commits = hashes
      current_pr_data = log.get_current_pr_data()
      # Case where test stats have been calculated and cached:
      if os.environ.get('TEST_STATS'):
         log.gather_historical_data(2) # past two commits only --> Load from cache instead and include more commits?
         log.test_stats = load_json_from_file(f"{os.environ.get('TEST_STATS')}/stats.json")[machine]
         historical_runtime_memory[machine] = load_json_from_file(f"{os.environ.get('TEST_STATS')}/historical_runtime_memory.json")[machine]
         for test in historical_runtime_memory[machine]:
            try: 
               historical_runtime_memory[machine][test]['runtime'][0] = current_pr_data[test][0]
               historical_runtime_memory[machine][test]['memory'][0] = current_pr_data[test][1]
            except KeyError:
               historical_runtime_memory[machine][test]['runtime'][0] = None
               historical_runtime_memory[machine][test]['memory'][0] = None
               logging.warning(f"Test {test} does not exist for current PR.")
         
      # Case where test stats have NOT been calculated and cached:
      else:
         log.gather_historical_data(10) # past 50 commits
         log.calculate_stats()
         stats_by_machine[machine] = log.test_stats # Add stats to save/cache later
         historical_runtime_memory[machine] = log.historical_rt_mem_data
         
         for test in historical_runtime_memory[machine]:
            try:
               historical_runtime_memory[machine][test]['runtime'].insert(0, current_pr_data[test][0])
               historical_runtime_memory[machine][test]['memory'].insert(0, current_pr_data[test][1])
            except:
               historical_runtime_memory[machine][test]['runtime'].insert(0, None)
               historical_runtime_memory[machine][test]['memory'].insert(0, None)
               logging.warning(f"Test {test} does not exist for current PR.")
      
      # Compare current results to historical values and save results (pass/warn/fail)
      log.compare_results()
      runtime_results_by_machine[machine] = log.runtime_results
      mem_results_by_machine[machine] = log.memory_results
   
   # If the statistics on mean/standard deviation have NOT already been cached, create file to cache.
   if not os.environ.get('TEST_STATS'):
      create_json(stats_by_machine, "stats")
   
   # Create a record of historical runtime & memory values w/current PR data for caching (to use in plotting job and subsequent workflow runs)
   create_json(historical_runtime_memory, "historical_runtime_memory")

   # Create resource summaries to use in write_test_summary.py 
   create_json(runtime_results_by_machine, "runtime_results")
   create_json(mem_results_by_machine, "memory_results")

   return 0

if __name__ == "__main__": # pragma: no coverage

   main()
