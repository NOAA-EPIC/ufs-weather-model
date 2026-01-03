import numpy as np
import pytest
from pathlib import Path
from scripts.APICall import APICall
from scripts.Log import Log
from scripts.get_data import *

def test_init_hercules_Log(herc_log):
   assert herc_log.machine == "hercules"
   assert herc_log.text_per_log == []

def test_get_pr_head(herc_log, set_env_vars):
   """Test the API call and it's ability to get the PR 2882's head commit. 
   When running tests locally, create a GitHub token and set it as an environment variable 
   using one of the methods listed in test_fetch_repo_log_commits() above.
   """
   set_env_vars
   herc_log._get_pr_head()

   assert herc_log.pr_head_commit == ["369cead91c98eb5c72da81ff78925250dad08903"]

def test_fetch_log_text_w_no_commits(herc_log, caplog): 
   herc_log.pr_head_commit = None
   herc_log._fetch_log_text(herc_log.pr_head_commit)
   assert caplog.records[0].message == "An appropriate commit(s) was not provided. Call _get_pr_head() or _fetch_repo_log_commits() first."

def test_fetch_log_text_for_pr_head(herc_log, hercules_most_recent_commits, hercules_log_texts_2882): 
   """Check that the log texts extracted by the API are the same as the hercules log texts that we expect."""
   herc_log.pr_head_commit = hercules_most_recent_commits[0]
   #herc_log.repo_commits = hercules_most_recent_commits[1:]
   # Need to mock API call
   #herc_log._fetch_log_text(herc_log.repo_commits)
   herc_log._fetch_log_text(herc_log.pr_head_commit)

   #assert herc_log.text_per_log == hercules_log_texts_2882[1:]
   assert herc_log.text_per_log[0] == hercules_log_texts_2882[0]

def test_fetch_log_text_for_develop(herc_log, hercules_most_recent_commits, hercules_log_texts_2882): 
   """Check that the log texts extracted by the API are the same as the hercules log texts that we expect."""
   herc_log.repo_commits = hercules_most_recent_commits[1:]
   herc_log._fetch_log_text(herc_log.repo_commits)

   assert herc_log.text_per_log[1:] == hercules_log_texts_2882[1:]

def test_get_instance_test_data(herc_log, hercules_log_texts_2882, log_instance_results_2882_0):
   """From the log for PR 2882, extract test data. Compare it with the expected data to be sure it's the same.
   """
   tests_for_log_instance = herc_log._get_instance_test_data(hercules_log_texts_2882[0])
   assert tests_for_log_instance == log_instance_results_2882_0

def test_compile_historical_log_data(herc_log, hercules_log_texts_2882, hercules_sample_historical_log_data): 
   
   herc_log.text_per_log = hercules_log_texts_2882
   herc_log._compile_historical_log_data()
   
   # Are all items in the hercules_sample_historical_log_data in herc_log.historical_rt_mem_data? 
   for test in hercules_sample_historical_log_data:
      assert herc_log.historical_rt_mem_data[test] == hercules_sample_historical_log_data[test]

def test_calculate_stats(herc_log, hercules_sample_historical_log_data, hercules_mean_std):
   
   herc_log.historical_rt_mem_data = hercules_sample_historical_log_data
   herc_log.calculate_stats()

   for test in hercules_mean_std: 
      assert hercules_mean_std[test] == herc_log.test_stats[test]

def test_compare_results(herc_log, hercules_log_texts_2882, log_instance_results_2882_0, hercules_mean_std): 

   current_log = log_instance_results_2882_0
   herc_log.text_per_log = hercules_log_texts_2882
   herc_log.test_stats = hercules_mean_std
   herc_log.compare_results()

   for test in herc_log.test_stats: 
      hi_runtime = herc_log.test_stats[test][0] + herc_log.test_stats[test][1]
      hi_memory = herc_log.test_stats[test][2] + herc_log.test_stats[test][3]

      # Could improve test to check for correct warn vs. fail status
      if current_log[test][0] > hi_runtime:
         assert herc_log.runtime_results[test] != '✅'
      if current_log[test][1] > hi_memory:
         assert herc_log.memory_results[test] != '✅'
