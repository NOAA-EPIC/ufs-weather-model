import os
from datetime import datetime, timedelta
import logging
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from .APICall import APICall
from .utilities import *

def get_test_names(data):
   """Create a set containing all test names by extracting the tests (keys) from the data_by_machine
   Args:
      data (dict): Runtime and memory data for each test and machine. Primary key is machine. Values are tests for each machine. 
   Returns:
      all_tests: Set of all test names
   """
   all_tests = set()
   for data_by_machine in data.values():
      all_tests.update(data_by_machine.keys())
   
   return all_tests

def organize_data_by_test(data, category):
   """Creates new runtime and memory dictionaries that use test name as key and have data for each machine 
   under each test. 
   Args:
      data (dict): Runtime and memory data for each test and machine. Primary key is machine. Secondary key is test. 
   Returns:
      metrics (dict): Runtime and memory data for each test and machine. Primary key is test. Secondary key is machine. 
   """

   tests = get_test_names(data)

   # Create a three-level deep dictionary where any key access at the first or second level that doesn't exist will automatically be created
   metrics = defaultdict(lambda: dict)

   for test in tests:
      for machine, machine_data in data.items():
         if test not in machine_data:
            continue
         elif test not in metrics:
            metrics[test] = {machine: machine_data[test][category]}
         else:
            metrics[test].update({machine: machine_data[test][category]})

   return metrics
   
def detect_statistical_anomalies(test_data):
   """Detect statistical anomalies, aka tests w/runtime or memory usage greater than 2 standard deviations above the mean.
   Args:
      test_data (list)
   """

   anomalies = [False] * len(test_data)
   mean = np.mean(test_data)
   stdev = np.std(test_data)
   anomalies = [True if value > (mean + (2 * stdev)) else False for i, value in enumerate(test_data)]

   return anomalies

def plot_results(data, category):
   """
   Writes metrics to CSV and generates anomaly-highlighted plots.

   Args:
      metrics (dict): Nested dict of metrics.
      hashes (list): Commit metadata.
      category (str): Runtime or memory
   """

   # Need to see what to do if no data for hash on certain machine

   metrics = organize_data_by_test(data, category)
   hashes = get_hashes(10) # Change to 50
   hashes.insert(0, "PR Head")
   print(f"Hashes (from create_images:) {hashes}")

   # Create one plot per test
   for test in metrics:
      plt.figure(figsize=(14, 6), dpi=200)

      styles = ['o-', 's--', '^-', 'd:', 'x-.', 'v--', '*-', 'p:']

      plt.title(f"{category} for {test}", fontsize=16)
      plt.xlabel("Commit Hash", fontsize=14)
      plt.ylabel(category, fontsize=14)
      plt.xticks(np.arange(len(hashes)), labels=hashes, rotation=45, fontsize=10)
      plt.yticks(fontsize=12)
      plt.grid(True, linestyle='--', alpha=0.5)
      

      # Add one line to the plot with data for each machine
      for i, machine in enumerate(metrics[test]):
         y = metrics[test][machine]
         anomalies = detect_statistical_anomalies(y)
         
         # For new tests, there may be less data available than the number of commits, 
         # so take the most recent hashes for which there is data
         x = hashes[:len(y)]
         # Plot lines per machine, then add anomalies for each line
         plt.plot(x, y, styles[i % len(styles)], label=f"{machine}", linewidth=2, markersize=6)
         [plt.plot(x[idx], y[idx], 'ro', markersize=8) for idx, val in enumerate(anomalies) if val == True]
         
      plt.legend(fontsize=12)
      plt.tight_layout()
      #plt.show()

      png_path = f"plots/{test}_{category}.png"
      os.makedirs("plots", exist_ok=True)
      plt.savefig(png_path)
   
      plt.close()

def main():

   # Don't need to commit/push old plots cuz that has presumably already been done
   # Maybe need to make new plots w/most recent commit? 
   try: 
      data = load_json_from_file(f"{os.environ.get('PLOT_DATA')}/historical_runtime_memory.json")
      for category in ["runtime", "memory"]:
         plot_results(data, category)
   except FileNotFoundError:
      logging.error("Could not load JSON file.")

if __name__ == "__main__":

   main()