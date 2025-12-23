import numpy as np
import pytest
from pathlib import Path
from scripts.APICall import APICall
from scripts.Log import Log
from scripts.utilities import *
from scripts.get_data import *

def test_create_json(stats_dict_snippet):
   
   path = Path('data')
   path.mkdir(exist_ok = True)
   create_json(stats_dict_snippet, 'stats')

   with open('test_file_stats.json', 'r') as test_stats_file, open ('data/stats.json', 'r') as new_json:
      test_file_content = test_stats_file.read()
      new_json_content = new_json.read()
   
   assert test_file_content == new_json_content

def test_load_json_from_file(stats_dict_snippet):
   machine = "orion"
   orion_snippet = load_json_from_file('test_file_stats.json')[machine]
   assert orion_snippet == stats_dict_snippet['orion']

@pytest.mark.parametrize("num", [1, 7, 10, 12])
def test_get_hashes(num):
   """Retrieve the last "num" commit hashes from the repository.
   """
   hashes = get_hashes(num)
   
   assert len(hashes) == num

def test_main_e2e_cached_stats(monkeypatch, set_env_vars):
   """Test that main function runs to completion."""

   set_env_vars
   monkeypatch.setenv("MACHINES", "hercules")
   monkeypatch.setenv("TEST_STATS", "data")
   exit_code = main()

   assert exit_code == 0

def test_main_e2e_no_cached_stats(monkeypatch, set_env_vars):
   """Test that main function runs to completion."""

   set_env_vars
   monkeypatch.setenv("MACHINES", "hercules")
   exit_code = main()

   assert exit_code == 0