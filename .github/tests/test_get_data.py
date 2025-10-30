import requests
import os
import json
from datetime import datetime
import re
import numpy as np
import pytest
import requests_mock
from unittest.mock import patch, Mock
from pathlib import Path
from scripts.get_data import APICall, Log, load_json, create_json

@pytest.mark.parametrize("endpoint", [
   f"commits?path=tests/logs/RegressionTests_ursa.log&per_page=1", #fetch_repo_commits_endpoint
   f"pulls/2882", #get_pr_head_endpoint
   f"contents/tests/logs/RegressionTests_ursa.log", #fetch_log_text_endpoint
   ])
@pytest.mark.parametrize("num_commits", [1, 5, 7])
def test_init_APICall(set_env_vars, endpoint, num_commits):
   
   set_env_vars
   api_call = APICall(endpoint, num_commits)

   assert api_call.token == "fake_github_pat_12BWCMCFZkhj35klj3h34kjh4kkjm3whe4nr"
   assert api_call.base_url == "https://api.github.com/repos/ufs-community/ufs-weather-model"
   assert api_call.endpoint == endpoint
   assert api_call.url == f"https://api.github.com/repos/ufs-community/ufs-weather-model/{endpoint}"
   assert api_call.num_commits == num_commits
   assert api_call.header == {
         "Accept": "application/vnd.github.v3+json",
         "Authorization": f"Bearer fake_github_pat_12BWCMCFZkhj35klj3h34kjh4kkjm3whe4nr",
         "X-GitHub-Api-Version": "2022-11-28",
         "Accept": "application/vnd.github.raw"
      }

def test_init_hercules_Log(herc_log):
   assert herc_log.machine == "hercules"
   assert herc_log.text_per_log == []

def test_call_API(herc_log, set_env_vars):
   pass

def test_fetch_repo_commits(herc_log, set_env_vars):
   pass

def test_get_pr_head(herc_log):
   pass

def test_fetch_log_text_w_no_commits(herc_log): 
   pass
   """herc_log._fetch_log_text('')
   assert herc_log."""

def test_fetch_log_text_w_commits(herc_log, hercules_most_recent_commits, hercules_log_texts_2882): 
   """Check that the log texts extracted by the API are the same as the hercules log texts that we expect."""
   herc_log.pr_head_commit = hercules_most_recent_commits[0]
   herc_log.repo_commits = hercules_most_recent_commits[1:]
   # Need to mock API call
   herc_log._fetch_log_text(herc_log.repo_commits)

   #assert herc_log.text_per_log == hercules_log_texts_2882[1:]

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

def test_create_json(stats_dict_snippet):
   
   path = Path('data')
   path.mkdir(exist_ok = True)
   create_json(stats_dict_snippet, 'stats')

   with open('test_file_stats.json', 'r') as test_stats_file, open ('data/stats.json', 'r') as new_json:
      test_file_content = test_stats_file.read()
      new_json_content = new_json.read()
   
   assert test_file_content == new_json_content


def test_load_json(stats_dict_snippet):
   machine = "orion"
   orion_snippet = load_json('test_file_stats.json')[machine]
   assert orion_snippet == stats_dict_snippet['orion']
