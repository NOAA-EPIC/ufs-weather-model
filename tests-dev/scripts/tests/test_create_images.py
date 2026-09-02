from pathlib import Path
import pytest
import requests
import numpy as np
from scripts.Manager import *
from scripts.create_images import PlotManager
from scripts.create_images import *

@pytest.mark.parametrize('category', ['runtime', 'memory'])
def test_initialize_PlotManager(set_env_vars, category):
   """Check that PlotManager is initialized properly."""
   plot_manager = PlotManager(category)
   assert plot_manager.category == category

@pytest.mark.parametrize('category', ['runtime', 'memory'])
def test_get_test_names(set_env_vars, category):
   """Check that get_test_names() extracts all test names by comparing with rt.conf.
   """

   plot_manager = PlotManager(category)

   response = requests.get('https://raw.githubusercontent.com/ufs-community/ufs-weather-model/refs/heads/develop/tests/rt.conf')
   response = response.text.splitlines()
   tests = set()

   compiler = ''
   for line in response:
      if line.startswith('COMPILE'):
         compiler = line.split("|")[2].strip()
      elif line.startswith('RUN'):
         tests.add(line.split('|')[1].strip() + f"_{compiler}")
   
   assert tests == plot_manager.get_test_names()

@pytest.mark.parametrize('category', ['runtime', 'memory'])
def test_organize_data_by_test(set_env_vars, test_data, data_by_test, category):
   """Check that organize_data_by_test() creates new dictionaries that use test name as primary key instead of machine as primary key. 
   """
   plot_manager = PlotManager(category)
   plot_manager.historical_data = test_data
   # Need to add current PR data? 
   actual_data_by_test = plot_manager.organize_data_by_test()
   expected_data_by_test = data_by_test
   
   for test in expected_data_by_test:
      for machine in ['hera', 'ursa']:
         try:
            assert expected_data_by_test[test][category][machine] == actual_data_by_test[test][category][machine]
         except KeyError:
            continue

def test_detect_statistical_anomalies(set_env_vars, test_data):

   data = [2091, 1195, 2699, 1896, 2098, 2712, 2249, 1620, 1938, 1132, 1978, 1215, 1523, 2257, 1852, 1184, 1541, 1803, 2004, 1962, 2030, 2680, 1306, 1471, 2292, 1740, 2831, 1746, 1255, 1668]

   plot_manager = PlotManager('memory')

   actual_anomalies = plot_manager.detect_statistical_anomalies(data)
   mean = 1865.6
   stdev = 474.02543
   expected_anomalies = []

   for num in data: 
      if num > mean + 2 * stdev:
         expected_anomalies.append(True)
      else:
         expected_anomalies.append(False)

   assert actual_anomalies == expected_anomalies

def test_rearrange_hashes(set_env_vars, test_data, hashes):
   plot_manager = PlotManager('runtime')
   plot_manager.hashes = plot_manager.rearrange_hashes()
   hashes = ['PR Head'] + plot_manager.get_hashes()
   hashes.reverse()
   assert plot_manager.hashes == hashes

@pytest.mark.parametrize('category', ['runtime', 'memory'])
def test_generate_figure(set_env_vars, category, hashes):
   plot_manager = PlotManager(category)
   plot_manager.hashes = hashes
   plot = plot_manager.generate_figure("cpld_sample_test")
   
   assert plot.gca().get_title() == f"{category} for cpld_sample_test"
   assert plot.gca().get_ylabel() == category
   assert plot.gca().get_xlabel() == "Commit Hash: oldest --> newest"

@pytest.mark.parametrize('category', ['runtime', 'memory'])
@pytest.mark.parametrize('test', ['cpld_control_pdlib_p8_gnu', 'cpld_debug_pdlib_p8_gnu',
                         'datm_cdeps_control_cfsr_gnu', 'control_gfs_mpas_gnu', 
                         'pm_ideal_supercell_intel', 'control_p8_intel',
                         'control_p8_ugwpv1_tempo_aerosol_hail_intel'])
def test_add_test_metrics_by_machine(set_env_vars, test_data_subset, data_by_test, category, hashes, test):
   """Test hash retrieval and metrics restructuring prior to plotting."""
   plot_manager = PlotManager(category)
   plot_manager.historical_data = test_data_subset
   plot_manager.metrics = plot_manager.organize_data_by_test()
   plot_manager.hashes = hashes[-11:]
   plot = plot_manager.generate_figure(test)
   plot = plot_manager.add_test_metrics_by_machine(plot, test)
   lines = plot.gca().get_lines()
   
   for line in lines:
      if not line.get_label().startswith("_child"): #anomaly points are labeled "_child#"
         expected_data = data_by_test[test][category][line.get_label()]
         expected_data.reverse()
         actual_data = line.get_ydata()
         assert np.array_equal(actual_data, expected_data)
      


@pytest.mark.run_manual
@pytest.mark.parametrize('category', ['runtime', 'memory'])
def test_plot_results(set_env_vars, test_data_subset, category):
   """
   Check that plotting runs error-free and generates expected files. 
   """

   # Delete files in plots dir first?
   plot_manager = PlotManager(category)
   plot_manager.metrics = test_data_subset
   plot_manager.plot_results()

   tests = ['cpld_control_pdlib_p8_gnu', 'cpld_debug_pdlib_p8_gnu',
            'datm_cdeps_control_cfsr_gnu', 'control_gfs_mpas_gnu', 
            'pm_ideal_supercell_intel', 'control_p8_intel',
            'control_p8_ugwpv1_tempo_aerosol_hail_intel', ]

   for test in tests:
      filepath = Path(f"plots/{test}_{category}.png")
      assert filepath.is_file(), f"File not found: {filepath}"

def test_save_plot_image(set_env_vars, ):
   pass

def test_load_data(set_env_vars, ):
   pass

def test_process_data(set_env_vars, ):
   pass
