import os
import requests
import json
from datetime import datetime
import re

def get_file_info(machine, headers): 
   """Extract the file text."""

   file_contents = []
   url=f"{os.environ.get('BASE_URL')}/contents/tests/logs/RegressionTests_{machine}.log"
   
   r = requests.get(url, headers=headers)
   file_contents.append(r.text)

   return file_contents

def parse_file(file_contents): #Refactor to remove date parsing
   """Parse file to determine the memory usage and runtime for each test."""
   
   test_data = {}
   test_pattern = r"TEST \'(.*)\' \[\d+:\d+, (\d+):(\d+)\]\((\d+) MB\)"
   
   for item in file_contents: # Refactor into get_date() and get_test_data()
      item = item.splitlines()
      for line in item:
         test_match = re.search(test_pattern, line)
         if test_match:
            test_name, hh, mm, mem = test_match.groups()
            try:
               total_minutes = int(hh) * 60 + int(mm)
               test_data[test_name]["runtime"].append(total_minutes)
               test_data[test_name]["memory"].append(int(mem))
            except(KeyError): 
               total_minutes = int(hh) * 60 + int(mm)
               test_data[test_name] = {"runtime": [total_minutes], "memory": [int(mem)]}

   return test_data

def compare_runtime(log, hist_stats, machine):
   results = {}

   for test in log:
      hi_rt = hist_stats[machine][test][0] + hist_stats[machine][test][1]
      if log[test]["runtime"][0] > hi_rt:
         results[test] = f"❌ FAIL"
      else:
         results[test] = '✅ PASS'

   return results

def compare_memory(log, hist_stats, machine):

   for test in log:
      hi_mem = hist_stats[machine][test][2] + hist_stats[machine][test][3]
      if log[test]["memory"][0] > hi_mem:
         results[test] = f"❌ FAIL" 
      else:
         results[test] = '✅ PASS'

   return results

def compare_results(log, hist_stats, machine): 
   
   runtime_results = compare_runtime(log, hist_stats, machine)
   memory_results = compare_memory(log, hist_stats, machine)

   for test in runtime_results:
      results[test] = [runtime_results[test],memory_results[test]]

   return results

def load_json(json_file):
   """Convert JSON file to python dictionary."""
   with open(json_file, 'r') as file:
      stats = json.load(file)
   return stats

def create_machine_stats(stats_dict):
   """Create a json file with statistic for each test on each machine"""

   with open(f"test_results.json", 'a') as fh:
      json.dump(stats_dict, fh, indent=4)

if __name__ == "__main__":

   token = os.environ.get('GITHUB_TOKEN')
   headers = {
      "Accept": "application/vnd.github.v3+json",
      "Authorization": f"Bearer {token}",
      "X-GitHub-Api-Version": "2022-11-28",
      "Accept": "application/vnd.github.raw"
   }
   machines = os.environ.get('MACHINES').split()
   hist_stats = os.environ.get('MACHINE_STATS')
   hist_stats = load_json(hist_stats)
   test_results = {}
   for machine in machines:
      print(machine.upper())
      contents = get_file_info(machine, headers)
      results = parse_file(contents)
      test_results[machine] = compare_results(results, hist_stats, machine)
      print(test_results[machine])
   create_machine_stats(test_results)

   



