import os
import json
from .Log import Log
from .create_images import *

"""This script contains a main() function that gets log information from GitHub using the APICall class 
and extracts data from the RegressionTest_<machine>.log files for each machine. 
It also contains two utility functions to (1) create a JSON file from log data and (2) load data from a 
JSON file into a python dictionary. 
"""

# Utilities for file I/O & plotting
def create_json(dictionary, file_name):
   """Create a json file with statistics for each test on each machine"""

   with open(f"data/{file_name}.json", 'w') as fh:
      json.dump(dictionary, fh, indent=4)

def load_json(file_path):
   """Convert JSON file to python dictionary."""
   with open(file_path, 'r', encoding='utf-8') as file:
      data = json.load(file)

   return data

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
   
   for machine in machines[3:7]:
      print(machine.upper())
      log = Log(machine)
      current_pr_data = log.get_current_pr_data()
      # Case where test stats have been calculated and cached:
      if os.environ.get('TEST_STATS'):
         log.gather_historical_data(2) # past two commits only
         log.test_stats = load_json(os.environ.get('TEST_STATS'))[machine]

      # Case where test stats have NOT been calculated and cached:
      else:
         log.gather_historical_data(10) # past 50 commits
         log.calculate_stats()
         stats_by_machine[machine] = log.test_stats # Add stats to save/cache later

      # Save historial runtime/memory data to plot
      historical_runtime_memory[machine] = log.historical_rt_mem_data
      for test in historical_runtime_memory[machine]:
         historical_runtime_memory[machine][test]['runtime'].insert(0, current_pr_data[test][0])
         #historical_runtime_memory[machine][test]['memory'].insert(0, current_pr_data[test][1])
      
      # Compare current results to historical values and save results (pass/warn/fail)
      log.compare_results()
      runtime_results_by_machine[machine] = log.runtime_results
      mem_results_by_machine[machine] = log.memory_results
   
   # If the statistics on mean/standard deviation have NOT already been cached, create file to cache.
   if not os.environ.get('TEST_STATS'):
      create_json(stats_by_machine, "stats")

   # Create resource summaries to use in write_test_summary.py 
   create_json(runtime_results_by_machine, "runtime_results")
   create_json(mem_results_by_machine, "memory_results")

   # Plot results
   #categories = ["runtime", "memory"]
   categories = ["runtime"]
   for category in categories:
      plot_results(historical_runtime_memory, category)

   return 0

if __name__ == "__main__": # pragma: no coverage

   main()
