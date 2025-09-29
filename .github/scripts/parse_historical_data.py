import requests
import os
import json
from datetime import datetime
import re
import numpy as np

def get_commits(machine, headers):
   """Get a list of commits a given platform's log files."""
   
   url=f"{os.environ.get('BASE_URL')}/commits?path=tests/logs/RegressionTests_{machine}.log"
   response = requests.get(url, headers=headers) #auth=("gspetro-NOAA", token)) 
   response = json.loads(response.text)
   print(response)
   commit_list = []
   for num in range(len(response)): 
      if response[num]['sha']:
         commit_list.append(response[num]['sha'])
      else: 
         print(response[num]['sha'], "does not exist!")

   return commit_list

def get_file_info(commit_list, machine, headers): 
   """For each commit of a machine's log file, extract the file text."""

   file_contents = []
   commit_url=f"{os.environ.get('BASE_URL')}/contents/tests/logs/RegressionTests_{machine}.log"
   
   for num in range(len(commit_list)): 
      url = commit_url + (f"?ref={commit_list[num]}") #Could use a path join?
      r = requests.get(url, headers=headers) #, auth=("gh_username", token))
      file_contents.append(r.text)

   return file_contents

def parse_file(file_contents):
   """Parse file to determine the memory usage and runtime for each test."""
   
   test_data = {}
   test_pattern = r"TEST \'(.*)\' \[\d+:\d+, (\d+):(\d+)\]\((\d+) MB\)"
   
   for item in file_contents: # Refactor into get_date() and get_test_data()
      date_pattern = r"Starting Date/Time: .*\n"
      date_match = re.search(date_pattern, item)
      if date_match:
         date_string = date_match.group(0)[19:].strip()
         # Strip microseconds
         date_string = re.sub(r"\.\d+", "", date_string)
         try:
            date = datetime.strptime(date_string, "%Y%m%d %H:%M:%S")
         except(ValueError):
            date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
         except: 
            print("Skipping log for ", date_string)
            continue
      item = item.splitlines()
      for line in item:
         test_match = re.search(test_pattern, line)
         if test_match:
            test_name, hh, mm, mem = test_match.groups()
            try:
               total_minutes = int(hh) * 60 + int(mm)
               test_data[test_name]["date"].append(date)
               test_data[test_name]["runtime"].append(total_minutes)
               test_data[test_name]["memory"].append(int(mem))
            except(KeyError): 
               total_minutes = int(hh) * 60 + int(mm)
               test_data[test_name] = {"date": [date], "runtime": [total_minutes], "memory": [int(mem)]}

   return test_data

def calculate_stats(test_hist):
   """For each test, calculate the mean and standard deviation of memory and runtime."""
   stats = {}
   for test in test_hist:
      runtime_mean = np.mean(test_hist[test]["runtime"])
      runtime_stdev = np.std(test_hist[test]["runtime"])
      memory_mean = np.mean(test_hist[test]["memory"])
      memory_stdev = np.std(test_hist[test]["memory"])
      stats[test] = [runtime_mean, runtime_stdev, memory_mean, memory_stdev]
      #print("Test: ", test, stats[test])

   return stats

def create_machine_stats(stats_dict):
   """Create a json file with statistic for each test on each machine"""

   with open(f"stats.json", 'a') as fh:
      json.dump(stats_dict, fh, indent=4)

if __name__ == "__main__":

   headers = {
      "Accept": "application/vnd.github.v3+json",
      "Authorization": "Bearer {token}",
      "X-GitHub-Api-Version": "2022-11-28",
      "Accept": "application/vnd.github.raw"
   }
   token = os.environ.get('TOKEN')
   machines = os.environ.get('MACHINES').split()
   stats_by_machine = {}
   for machine in machines:
      print(machine.upper())
      commit_list = get_commits(machine, headers)
      print(commit_list)
      contents = get_file_info(commit_list, machine, headers)
      historical_results = parse_file(contents)
      stats_by_machine[machine] = calculate_stats(historical_results)
   create_machine_stats(stats_by_machine)


   

   



