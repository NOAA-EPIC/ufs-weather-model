import requests
import os
import json
from datetime import datetime
import re
import numpy as np
import pytest
import requests_mock
from unittest.mock import patch, Mock
from scripts.get_data import APICall, Log

# Fixtures: 
@pytest.fixture
def set_env_vars():
   os.environ["GITHUB_TOKEN"] = "fake_github_pat_12BWCMCFZkhj35klj3h34kjh4kkjm3whe4nr"
   os.environ["BASE_URL"] = "https://api.github.com/repos/ufs-community/ufs-weather-model"

@pytest.fixture
def herc_log():
   return Log("Hercules")

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
   herc_log.fetch_log_text('')
   pass

def test_fetch_log_text_w_commits(herc_log, hercules_most_recent_commits, hercules_log_texts_2882): 
   """Check that the log texts extracted by the API are the same as the hercules log texts that we expect."""
   herc_log.pr_head_commit = hercules_most_recent_commits[0]
   herc_log.repo_commits = hercules_most_recent_commits[1:]
   # Need to mock API call
   herc_log.fetch_log_text(herc_log.repo_commits)

   #assert herc_log.text_per_log == hercules_log_texts_2882[1:]

def test_get_instance_test_data(herc_log, hercules_log_texts_2882, log_instance_results_2882_0):
   """From the log for PR 2882, extract test data. Compare it with the expected test data to be sure it's the same.
   """

   tests_for_log_instance = herc_log.get_instance_test_data(hercules_log_texts_2882[0])
   print(f"Tests dict: {tests_for_log_instance}")

   assert tests_for_log_instance == log_instance_results_2882_0

      
def test_compile_historical_log_data(herc_log): # Could split for runtime, mem to make more maintainable
   pass
               
def test_calculate_stats(herc_log):
   pass

def test_compare_runtime(herc_log):
   pass

def test_compare_memory(herc_log):
   pass

def test_compare_results(herc_log): 
   pass

def test_get_current_pr_instance_data(herc_log, hercules_log_texts_2882):
   pass

def test_gather_historical_data(herc_log, num_commits=5):
   pass

def test_create_machine_stats():
   pass

def test_create_machine_results():
   pass

def test_load_json():
   pass

