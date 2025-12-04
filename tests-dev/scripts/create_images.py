import os
import logging
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from .APICall import APICall

def get_test_names(data):
   """Create a set containing all test names by extracting the tests (keys) from the data_by_machine
   Args:
      data (dict): Runtime and memory data for each test and machine. Primary key is machine. 
   Returns:
      Set of all test names
   """
   print(data)
   all_tests = set()
   for data_by_machine in data.values():
      all_tests.update(data_by_machine.keys())
   
   return all_tests

def organize_data_by_test(data, category):
   """Creates new runtime and memory dictionaries that use test name as key and have data for each machine 
   under each test. 
   Args:
      data (dict): Runtime and memory data for each test and machine. Primary key is machine. 
   
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

   #print(metrics)

   return metrics
   
def get_hashes():
   """Save hashes for x-axis of plot
   """
   api_call = APICall("commits", 10) # Change to 50
   response = api_call.call_API()
   hashes = []

   for item in response:
      hashes.append(item['sha'][:8])
   #print(hashes)

   return hashes

def detect_anomalies(test_data):

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

   # Need to see what to do if no data for mash on certain machine

   metrics = organize_data_by_test(data, category)
   #print(metrics)
   hashes = get_hashes()

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
         #print(test)
         y = metrics[test][machine]
         anomalies = detect_anomalies(y)
         
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
      