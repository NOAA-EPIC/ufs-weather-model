import requests
import os
import json
import re
import numpy as np
import logging
from pathlib import Path
from .APICall import APICall

class Log():
   """A Regression Test log file."""
   
   def __init__(self, machine):
      """Create the log file object for a specific machine."""
      self.machine = machine.lower()
      self.text_per_log = []

   def _get_pr_head(self):
      """Get SHA for the HEAD of the PR. Structure of response: 
         response = [{"head": {"sha": "a1b2c3d..."}}]
         See GitHub documentation for https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits
      """
      try:
         api_call = APICall(f"pulls/{os.environ.get('PR_NUM')}")
         response = api_call.call_API()
         self.pr_head_commit = [response['head']['sha']]
      except:
         #print(response)
         logging.error(f"{response.status} {response.message}")

   def _fetch_repo_commits(self, num_commits=1):
      """Get a list of commits for the log file from the authoritative repository, with a maximum of 100 and a default of 1. 
      Structure of response: response = [{'sha': '3jl26ka...'}, {'sha': '6ag43sb...'}, ...]
      See GitHub documentation for https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits
      """
      api_call = APICall(f"commits?path=tests/logs/RegressionTests_{self.machine}.log&per_page={num_commits}")
      response = api_call.call_API()
      
      self.repo_commits = []
      for num in range(len(response)): 
         try: 
            self.repo_commits.append(response[num]['sha'])
            #print(response[num]['commit']['author']['date'])
         except: 
            logging.error(f"API Call failed. The sha does not exist!")

   def _fetch_log_text(self, commits): 
      """For each commit of a log, extract the log text."""

      try:
         api_call = APICall(f"contents/tests/logs/RegressionTests_{self.machine}.log")
         
         for num in range(len(commits)): 
            url = api_call.url + (f"?ref={commits[num]}") #Could use a path join?
            r = requests.get(url, headers=api_call.header)
            if commits == self.pr_head_commit:
               # Ensure that the pr log text comes first
               self.text_per_log.insert(0,r.text)
            else:
               self.text_per_log.append(r.text)
      except:
         logging.error("An appropriate commit(s) was not provided. Call _get_pr_head() or _fetch_repo_commits() first.")

   def _get_instance_test_data(self, log_instance):
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
      
   def _compile_historical_log_data(self): # Could split for runtime, mem to make more maintainable
      """Create a dictionary of data with runtime and memory usage for each test over time. Structure:  
         historical_test_data = {
            test: {runtime: [], memory: []}
         }
      """
   
      self.historical_rt_mem_data = {}
      
      # Skip self.text_per_log[0] because it is the log from the PR
      for log_instance in self.text_per_log[1:]:
         
         data = self._get_instance_test_data(log_instance)
         for test in data:
            try: 
               self.historical_rt_mem_data[test]["runtime"].append(data[test][0])
               self.historical_rt_mem_data[test]["memory"].append(data[test][1])
            except KeyError: 
               logging.info("Test key doesn't exist yet. Creating test key.")
               self.historical_rt_mem_data[test] = {"runtime": [data[test][0]], "memory": [data[test][1]]}
      #print(self.historical_rt_mem_data)

   def get_current_pr_data(self):
      """Extract runtime/memory data for the PR's most recent commit."""

      try: 
         self._get_pr_head()
         self._fetch_log_text(self.pr_head_commit)
         pr_log_data = self._get_instance_test_data(self.text_per_log[0])
         #print(pr_log_data)

         return pr_log_data
      except:
         logging.error()

   def gather_historical_data(self, num_commits=2):
      """Extract runtime/memory data for the authoritative repository's last two commits."""
      self._fetch_repo_commits(num_commits) #increase for statistical significance
      self._fetch_log_text(self.repo_commits)
      self._compile_historical_log_data()

   def calculate_stats(self):
      """For each test, calculate the mean and standard deviation of memory and runtime.
      """
      self.test_stats = {}
      for test in self.historical_rt_mem_data:
         runtime_mean = round(np.mean(self.historical_rt_mem_data[test]["runtime"]), 5)
         runtime_stdev = round(np.std(self.historical_rt_mem_data[test]["runtime"]), 5)
         memory_mean = round(np.mean(self.historical_rt_mem_data[test]["memory"]), 5)
         memory_stdev = round(np.std(self.historical_rt_mem_data[test]["memory"]), 5)
         self.test_stats[test] = [runtime_mean, runtime_stdev, memory_mean, memory_stdev]

   def _compare_runtime(self, current_log, previous_logs):
      """Determine whether the test runtime is within normal bounds."""
      
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
            logging.info(f"{test} is new. No comparison data.")
            self.runtime_results[test] = 'New'

   def _compare_memory(self, current_log, previous_logs):
      """Determine whether the test memory usage is within normal bounds."""

      self.memory_results = {}

      for test in current_log:
         try:
            hi_mem = self.test_stats[test][2] + self.test_stats[test][3]
            if current_log[test][1] > hi_mem and previous_logs['last'][test][1] > hi_mem and previous_logs['second_to_last'][test][1] > hi_mem:
               self.memory_results[test] = '❌'
            elif current_log[test][1] > hi_mem:
               self.memory_results[test] = '⚠️'
            else:
               self.memory_results[test] = '✅'
         except KeyError:
            logging.info(f"{test} is new. No comparison data.")
            self.memory_results[test] = 'New'

   def compare_results(self): 
      """Check results from previous two commits to determine whether the test runtime/memory usage is within normal bounds."""

      current_log = self._get_instance_test_data(self.text_per_log[0])
      previous_logs = {"last" : {}, "second_to_last" : {}}

      for index, item in enumerate(previous_logs):
         previous_logs[item] = self._get_instance_test_data(self.text_per_log[index + 1])
      
      self._compare_runtime(current_log, previous_logs)
      self._compare_memory(current_log, previous_logs)

