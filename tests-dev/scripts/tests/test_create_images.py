import os
import pytest
import requests
import re
import logging
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from scripts.get_data import *
from scripts.APICall import APICall
from scripts.Log import Log
from scripts.create_images import *


def test_get_test_names(test_data):
   """Check that get_test_names() extracts all test names by comparing with rt.conf.
   """

   response = requests.get('https://raw.githubusercontent.com/ufs-community/ufs-weather-model/refs/heads/develop/tests/rt.conf')
   response = response.text.splitlines()
   tests = set()

   compiler = ''
   for line in response:
      if line.startswith('COMPILE'):
         compiler = line.split("|")[2].strip()
      elif line.startswith('RUN'):
         tests.add(line.split('|')[1].strip() + f"_{compiler}")
   
   assert tests == get_test_names(test_data)

@pytest.mark.parametrize('category', ['runtime', 'memory'])
def test_organize_data_by_test(test_data, data_by_test, category):
   """Check that organize_data_by_test() creates new dictionaries that use test name as primary key instead of machine as primary key. 
   """
   expected_data_by_test = data_by_test
   actual_data_by_test = organize_data_by_test(test_data, category)
   for test in expected_data_by_test:
      for machine in ['hera', 'ursa']:
         try:
            assert expected_data_by_test[test][category][machine] == actual_data_by_test[test][category][machine]
         except KeyError:
            pass
   
def test_detect_statistical_anomalies():

   data = [2091, 1195, 2699, 1896, 2098, 2712, 2249, 1620, 1938, 1132, 1978, 1215, 1523, 2257, 1852, 1184, 1541, 1803, 2004, 1962, 2030, 2680, 1306, 1471, 2292, 1740, 2831, 1746, 1255, 1668]

   actual_anomalies = detect_statistical_anomalies(data)
   mean = 1865.6
   stdev = 474.02543
   expected_anomalies = []

   for num in data: 
      if num > mean + 2 * stdev:
         expected_anomalies.append(True)
      else:
         expected_anomalies.append(False)

   assert actual_anomalies == expected_anomalies

@pytest.mark.parametrize('category', ['runtime', 'memory'])
def test_get_plotting_data(test_data, data_by_test, category):
   """Test hash retrieval and metrics restructuring prior to plotting."""
   metrics, hashes = get_plotting_data(test_data, category)

   tests = ['cpld_control_pdlib_p8_gnu', 'cpld_debug_pdlib_p8_gnu',
            'datm_cdeps_control_cfsr_gnu', 'control_gfs_mpas_gnu', 
            'pm_ideal_supercell_intel', 'control_p8_intel',
            'control_p8_ugwpv1_tempo_aerosol_hail_intel', ]

   # Create a subset of the metrics dictionary to test
   subset_dict = {}
   for key, value in metrics.items():
      if key in tests:
         subset_dict[key] = value

   category_data_by_test = {} # Reshape data_by_test to contain either runtime or memory data (not both)
   for test in data_by_test:
      category_data_by_test[test] = data_by_test[test][category]

   assert len(hashes) == 31
   assert subset_dict == category_data_by_test

def test_plot_results():
   """
   Generates anomaly-highlighted plots.

   Args:
      metrics (dict): Nested dict of metrics.
      hashes (list): Commit metadata.
      category (str): Runtime or memory
   """

   assert False

