import requests
import os
import json
from datetime import datetime
import re
import numpy as np

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

class Log():
   """A Regression Test log file."""
   
   def __init__(self, machine):
      """Initialize the log file with a corresponding machine."""
      self.machine = machine
      self.text_per_log = []

   def call_API(self, endpoint):

      api_call = APICall(endpoint)
      response = requests.get(api_call.url, headers=api_call.header)
      response = json.loads(response.text)

      return response

   # Update number of commits to 50 before merging
   def get_repo_commits(self, num_commits=1):
      """Get a list of commits for the log, with a maximum of 100 and a default of 1. Structure of response: 
      response = [{
      "sha":"#######...",
      "node_id":"C_...",
      "commit":{
         "author":{
            "name":"First Last",
            "email":"########+username@users.noreply.github.com",
            "date":"YYYY-MM-DDTHH:mm:SSZ"
         }, ... ]
      """
      endpoint = f"commits?path=tests/logs/RegressionTests_{self.machine}.log&per_page={num_commits}"
      response = self.call_API(endpoint)
      
      self.repo_commits = []
      for num in range(len(response)): 
         if response[num]['sha']:
            self.repo_commits.append(response[num]['sha'])
         else: 
            print(response[num]['sha'], "does not exist!")


   def get_pr_head(self):
      """Get SHA for the HEAD of the PR. Structure of response: 
         response = [{
            "head": {
               "label": "user:feature-branch",
               "ref": "feature-branch",
               "sha": "a1b2c3d..."
            // ...
            }, ...
         }]
      """
      endpoint = f"pulls/{os.environ.get('PR_NUM')}"
      response = self.call_API(endpoint)
      self.pr_head_commit = [response['head']['sha']]
      print(self.pr_head_commit)


   def get_log_text(self, commits): 
      """For each commit of a log, extract the log text."""

      if not commits:
         return "ERROR: This log has no commit list. Log text cannot be extracted. "
      
      api_call = APICall(f"contents/tests/logs/RegressionTests_{self.machine}.log")
      
      for num in range(len(commits)): 
         url = api_call.url + (f"?ref={commits[num]}") #Could use a path join?
         r = requests.get(url, headers=api_call.header)
         if commits == self.pr_head_commit:
            # Ensure that the pr log text comes first
            self.text_per_log.insert(0,r.text)
         else:
            self.text_per_log.append(r.text)

   def get_instance_test_data(self, log_instance):
      """For each instance of a log at a given commit, extract runtime and memory data from the log text
         Args:
            log_instance: Log text for a given commit
         Returns: 
            tests_for_log_instance: A dictionary of tests (keys) with an array of total runtime and memory use as the value for each test
      """

      tests_for_log_instance = {}

      pattern = r"TEST \'(.*)\' \[\d+:\d+, (\d+):(\d+)\]\((\d+) MB\)"
      log_instance = log_instance.splitlines()

      for line in log_instance:
         test_match = re.search(pattern, line)
         if test_match:
            test_name, hh, mm, mem = test_match.groups()
            total_minutes = int(hh) * 60 + int(mm)
            tests_for_log_instance[test_name] = [total_minutes, int(mem)]

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
      
      # Skip self.text_per_log[0] because it is the log from the PR
      for log_instance in self.text_per_log[1:]:
         
         data = self.get_instance_test_data(log_instance)
         for test in data:
            try: 
               self.historical_rt_mem_data[test]["runtime"].append(data[test][0])
               self.historical_rt_mem_data[test]["memory"].append(data[test][1])
            except KeyError: 
               # Create key if it doesn't exist yet
               self.historical_rt_mem_data[test] = {"runtime": [data[test][0]], "memory": [data[test][1]]}
               
   def calculate_stats(self):
      """For each test, calculate the mean and standard deviation of memory and runtime."""
      self.test_stats = {}
      for test in self.historical_rt_mem_data:
         runtime_mean = round(np.mean(self.historical_rt_mem_data[test]["runtime"]), 5)
         runtime_stdev = round(np.std(self.historical_rt_mem_data[test]["runtime"]), 5)
         memory_mean = round(np.mean(self.historical_rt_mem_data[test]["memory"]), 5)
         memory_stdev = round(np.std(self.historical_rt_mem_data[test]["memory"]), 5)
         self.test_stats[test] = [runtime_mean, runtime_stdev, memory_mean, memory_stdev]

   def get_current_pr_data(self):

      self.get_pr_head()
      self.get_log_text(self.pr_head_commit)
      pr_log_data = self.get_instance_test_data(self.text_per_log[0])
      
      return pr_log_data

   def gather_historical_data(self):
      self.get_repo_commits(num_commits=10) #increase for statistical significance
      self.get_log_text(self.repo_commits)
      self.get_historical_log_data()
      self.calculate_stats()

   def compare_runtime(self, current_log, previous_logs):
      
      self.runtime_results = {}

      for test in current_log:

         try:
            hi_rt = self.test_stats[test][0] + self.test_stats[test][1]
            if current_log[test][0] > hi_rt and previous_logs['last'][test][0] > hi_rt and previous_logs['second_to_last'][test][0] > hi_rt:
               self.runtime_results[test] = '❌'
            elif current_log[test][0] > hi_rt:
               self.runtime_results[test] = '⚠️'
            else:
               self.runtime_results[test] = '✅'
         except KeyError:
            print(test, "is new. No comparison data.")
            self.runtime_results[test] = 'New'


   def compare_memory(self, current_log, previous_logs):

      self.memory_results = {}

      for test in current_log:
         try:
            hi_mem = self.test_stats[test][2] + self.test_stats[test][3]
            if current_log[test][0] > hi_mem and previous_logs['last'][test][0] > hi_mem and previous_logs['second_to_last'][test][0] > hi_mem:
               self.memory_results[test] = '❌'
            elif current_log[test][0] > hi_mem:
               self.memory_results[test] = '⚠️'
            else:
               self.memory_results[test] = '✅'
         except KeyError:
            print(test, "is new. No comparison data.")
            self.runtime_results[test] = 'New'

   def compare_results(self): 
   
      current_log = self.get_instance_test_data(self.text_per_log[0])
      previous_logs = {"last" : {}, "second_to_last" : {}}

      for index, item in enumerate(previous_logs):
         previous_logs[item] = self.get_instance_test_data(self.text_per_log[index + 1])
      
      self.compare_runtime(current_log, previous_logs)
      self.compare_memory(current_log, previous_logs)

def create_machine_stats(stats_dict):
   """Create a json file with statistic for each test on each machine"""

   with open(f"data/stats.json", 'a') as fh:
      json.dump(stats_dict, fh, indent=4)

def create_machine_results(results_dict, file_name):
   """Create a json file with statistic for each test on each machine"""

   with open(f"data/{file_name}.json", 'a') as fh:
      json.dump(results_dict, fh, indent=4)

def main():
   machines = os.environ.get('MACHINES').split()
   stats_by_machine = {}
   runtime_results_by_machine = {}
   mem_results_by_machine = {}
   for machine in machines:
      print(machine.upper())
      log = Log(machine)
      log.get_current_pr_data()
      log.gather_historical_data()
      log.compare_results()
      stats_by_machine[machine] = log.test_stats
      runtime_results_by_machine[machine] = log.runtime_results
      mem_results_by_machine[machine] = log.memory_results
   create_machine_stats(stats_by_machine)
   create_machine_results(runtime_results_by_machine, "runtime_results")
   create_machine_results(mem_results_by_machine, "memory_results")

if __name__ == "__main__":

   main()


