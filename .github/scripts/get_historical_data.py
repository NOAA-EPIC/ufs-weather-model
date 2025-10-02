import requests
import os
import json
from datetime import datetime
import re
import numpy as np

class Log():
   """A Regression Test log file."""
   
   def __init__(self, machine):
      """Initialize the log file with a corresponding machine."""
      self.machine = machine

   # Update number of commits to 50 before merging
   def get_commits(self, num_commits=10):
      """Get a list of commits for the log, with a maximum (and default) of 100."""
      
      endpoint = f"commits?path=tests/logs/RegressionTests_{self.machine}.log&per_page={num_commits}"
      api_call = APICall(endpoint)
      response = requests.get(api_call.url, headers=api_call.header)
      response = json.loads(response.text)
      self.commits = []
      for num in range(len(response)): 
         if response[num]['sha']:
            self.commits.append(response[num]['sha'])
         else: 
            print(response[num]['sha'], "does not exist!")

   def get_log_text(self): 
      """For each commit of a log, extract the log text."""
      if not self.commits:
         return "ERROR: This log has no commit list. Log text cannot be extracted. "
      
      self.log_text = []
      endpoint = f"contents/tests/logs/RegressionTests_{self.machine}.log"
      api_call = APICall(endpoint)
      
      for num in range(len(self.commits)): 
         url = api_call.url + (f"?ref={self.commits[num]}") #Could use a path join?
         r = requests.get(url, headers=api_call.header)
         self.log_text.append(r.text)

   # Do we need this one?
   def get_date(self, text): # Change this to get/save date based on 
      """Get the date for a specific commit of a log.
         Ags:
            text: text of log file at specific commit
      """
      date_pattern = r"Starting Date/Time: .*\n"
      date_match = re.search(date_pattern, text)
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
            return
      return date

   def get_instance_test_data(self, log_instance):
      """For each instance of a log at a given commit, extract runtime and memory data from the log text
         Args:
            log_instance: Log text for a given commit
         Returns: 
            tests_for_log_instance: A dictionary of tests (keys) with an array of date, total runtime, and memory use as the value for each test
      """

      tests_for_log_instance = {}

      date = self.get_date(log_instance)
      pattern = r"TEST \'(.*)\' \[\d+:\d+, (\d+):(\d+)\]\((\d+) MB\)"
      log_instance = log_instance.splitlines()

      for line in log_instance:
         if date == None:
            continue #skip
         test_match = re.search(pattern, line)
         if test_match:
            test_name, hh, mm, mem = test_match.groups()
            total_minutes = int(hh) * 60 + int(mm)
            tests_for_log_instance[test_name] = [date, total_minutes, int(mem)]
      
      return tests_for_log_instance     
      
   def get_historical_log_data(self): # Could split for runtime, mem to make more maintainable
      """Create a dictionary of data with runtime and memory usage for each test over time. Structure:  
         historical_test_data = {
            test: {
               runtime: []
               memory: []
            }
         }
      """
   
      self.historical_rt_mem_data = {}
      
      for log_instance in self.log_text:
         
         data = self.get_instance_test_data(log_instance)
         for test in data:
            try: 
               self.historical_rt_mem_data[test]["runtime"].append(data[test][1])
               self.historical_rt_mem_data[test]["memory"].append(data[test][2])
            except KeyError: 
               # Create key if it doesn't exist yet
               self.historical_rt_mem_data[test] = {"runtime": [data[test][1]], "memory": [data[test][2]]}
               
   def calculate_stats(self):
      """For each test, calculate the mean and standard deviation of memory and runtime."""
      self.test_stats = {}
      for test in self.historical_rt_mem_data:
         runtime_mean = round(np.mean(self.historical_rt_mem_data[test]["runtime"]), 5)
         runtime_stdev = round(np.std(self.historical_rt_mem_data[test]["runtime"]), 5)
         memory_mean = round(np.mean(self.historical_rt_mem_data[test]["memory"]), 5)
         memory_stdev = round(np.std(self.historical_rt_mem_data[test]["memory"]), 5)
         self.test_stats[test] = [runtime_mean, runtime_stdev, memory_mean, memory_stdev]

class APICall():
   """An API call"""

   def __init__(self, endpoint='', num_commits=1):
      self.token = os.environ.get('GITHUB_TOKEN')
      self.base_url = os.environ.get('BASE_URL')
      self.endpoint = endpoint
      self.url = f"{self.base_url}/{self.endpoint}" #Could use a path join?
      self.num_commits = num_commits
      self.header = {
         "Accept": "application/vnd.github.v3+json",
         "Authorization": f"Bearer {self.token}",
         "X-GitHub-Api-Version": "2022-11-28",
         "Accept": "application/vnd.github.raw"
      }

def create_machine_stats(stats_dict):
   """Create a json file with statistic for each test on each machine"""

   with open(f"stats.json", 'a') as fh:
      json.dump(stats_dict, fh, indent=4)

def main():
   machines = os.environ.get('MACHINES').split()
   stats_by_machine = {}
   for machine in machines:
      print(machine.upper())
      log = Log(machine)
      log.get_commits()
      log.get_log_text()
      log.get_historical_log_data()
      log.calculate_stats()
      stats_by_machine[machine] = log.test_stats
   create_machine_stats(stats_by_machine)

if __name__ == "__main__":

   main()
   

   



