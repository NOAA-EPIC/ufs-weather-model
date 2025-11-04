import os
import json
import re
from mdutils.mdutils import MdUtils
import pandas as pd
from scripts.write_test_summary import *

def test_load_json(stats_dict_snippet):

   content = load_json('test_file_stats.json')
   assert stats_dict_snippet == content

def test_create_mdFile():

   mdFile = create_mdFile()
   assert mdFile.get_md_text() == "\nTest Summary for PR #2882\n=========================\n"
   assert mdFile.file_name == 'summary.md'

def test_build_content(sample_runtime_results, actual_passes_per_test, actual_passes_per_machine):

   os.environ["RUNTIME_RESULTS"] = "runtime_results.json"
   content = build_content("runtime").sort_index()

   # Create comparison DataFrame from fixtures
   sample_runtime_results["Passing"] = actual_passes_per_test
   actual_results = pd.DataFrame.from_dict(sample_runtime_results).fillna("N/A")
   actual_passes_per_machine = pd.DataFrame.from_dict(actual_passes_per_machine, orient='index', columns=["hercules","orion","ursa","Passing"])
   actual_results = pd.concat([actual_results,actual_passes_per_machine]).sort_index()

   assert content.equals(actual_results)

def test_write_content():
   
   pass

def test_create_summary():
   
   pass

def test_count_passes_per_machine(sample_runtime_results, actual_passes_per_machine):
   """Tests whether the calculated number of tests passing per machine is the same as the actual number of tests passing per machine."""
   
   # Set up dataframe with test results
   results = pd.DataFrame()

   for machine in sample_runtime_results.keys():
      machine_results = pd.DataFrame.from_dict(sample_runtime_results[machine], orient='index',columns=[machine])
      results = pd.merge(results, machine_results, left_index=True, right_index=True, how='outer').fillna("N/A")

   # Calculate passing tests per machine
   results = count_passes_per_machine(results)
   actual_values = pd.DataFrame.from_dict(actual_passes_per_machine, orient='index', columns=["hercules","orion","ursa","Passing"])
   
   assert results.equals(actual_values)

def test_count_passes_per_test(sample_runtime_results, actual_passes_per_test):
   """Tests whether the calculated number of tests passing is the same as the actual number of tests passing."""
   
   # Set up dataframe with test results
   results = pd.DataFrame()

   for machine in sample_runtime_results.keys():
      machine_results = pd.DataFrame.from_dict(sample_runtime_results[machine], orient='index',columns=[machine])
      results = pd.merge(results, machine_results, left_index=True, right_index=True, how='outer').fillna("N/A")

   # Calculate passing tests
   results = count_passes_per_test(results)['Passing']

   # Sort by index before comparing calculated and actual values for equality
   assert results.sort_index().equals(pd.Series(actual_passes_per_test, name='Passing').sort_index())
