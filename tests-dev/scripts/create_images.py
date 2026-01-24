import os, sys
import logging
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from .utilities import *

class PlotManager():

   def __init__(self, data, category):
      """Create a Plot Manager object that holds data related to all plots. 
      Args:
         data (dict): Runtime and memory data for each test and machine. Primary key is machine. Secondary key is test. 
         category (str): 'runtime' or 'memory'
      """
      self.data = data
      self.category = category

   def get_test_names(self):
      """Create a set containing all test names by extracting the tests (keys) from the data_by_machine
      Returns:
         all_tests: Set of all test names
      """
      all_tests = set()
      for data_by_machine in self.data.values():
         all_tests.update(data_by_machine.keys())
      
      return all_tests

   def organize_data_by_test(self):
      """Creates new runtime and memory dictionaries that use test name as key and have data for each machine 
      under each test. 
      Returns:
         metrics (dict): Runtime and memory data for each test and machine. Primary key is test. Secondary key is machine. 
      """

      tests = self.get_test_names()

      # Create a three-level deep dictionary where any key access at the first or second level that doesn't exist will automatically be created
      metrics = defaultdict(lambda: dict)

      for test in tests:
         for machine, machine_data in self.data.items():
            if test not in machine_data:
               continue # No data to add
            elif test not in metrics:
               metrics[test] = {machine: machine_data[test][self.category]}
            else:
               metrics[test].update({machine: machine_data[test][self.category]})
      
      return metrics
   
   def detect_statistical_anomalies(self, test_data):
      """Detect statistical anomalies, aka tests w/runtime or memory usage greater than 2 standard deviations above the mean.
      Args:
         test_data (list): Data that needs to be checked for statistical anomalies
      Returns:
         anomalies (list): A boolean list where True indicates the presence of an anomalous value.
      """
      anomalies = [False] * len(test_data)
      mean = np.mean(test_data, dtype=float)
      stdev = np.std(test_data, dtype=float)
      """binmap = []
      for value in enumerate(test_data):
         print(value)
         if value > (mean + (2 * stdev)):
            binmap.append(True)
         else:
            binmap.append(False)"""
      anomalies = [True if value > (mean + (2 * stdev)) else False for i, value in enumerate(test_data)]

      return anomalies

   def rearrange_hashes(self):
      """Rearrange hashes for use in plotting function
      Returns:
         hashes (list): Commit metadata; by default, 30 most recent hashes from the repository plus 'PR Head'.
      """
      hashes = get_hashes() # Default 30 hashes; change quantity in utility function for consistency
      hashes.insert(0, "PR Head")
      hashes.reverse()
      return hashes

   def generate_figure(self, test):
      """For each test, create a plot containing figure metadata (e.g., title, xticks, yticks)."""
      plt.figure(figsize=(14, 6), dpi=200)
      plt.title(f"{self.category} for {test}", fontsize=16)
      plt.xlabel("Commit Hash: oldest --> newest", fontsize=14)
      plt.ylabel(self.category, fontsize=14)
      plt.xticks(np.arange(len(self.hashes)), labels=self.hashes, rotation=45, fontsize=10)
      plt.yticks(fontsize=12)
      plt.grid(True, linestyle='--', alpha=0.5)

      return plt

   def add_test_metrics_by_machine(self, plt, test):
      """For each test, plot lines with data for each machine."""
      
      styles = ['o-', 's--', '^-', 'd:', 'x-.', 'v--', '*-', 'p:']
      
      # Add one line to the plot with data for each machine
      for i, machine in enumerate(self.metrics[test]):
         #print(f"Machine: {machine}, Test: {test}")
         y = self.metrics[test][machine]
         #print(y[::-1])
         anomalies = self.detect_statistical_anomalies(y[::-1])
         #print(self.hashes)
         
         # For new tests, there may be less data available than the number of commits, 
         # so take the most recent hashes for which there is data
         x = self.hashes[:len(y)]
         # Plot lines per machine: reverse direction of data (most recent last/rightmost), then add anomalies for each line
         plt.plot(x, y[::-1], styles[i % len(styles)], label=f"{machine}", linewidth=2, markersize=6)
         #print(anomalies)
         #for idx, val in enumerate(anomalies):
            #print(f"idx, val: {idx}, {val}")
            #if val == True:
               #print(f"hash: {x[idx]}, data: {y[idx]}")
               #plt.plot(x[idx], y[::-1][idx], 'ro', markersize=8)
         [plt.plot(x[idx], y[::-1][idx], 'ro', markersize=8) for idx, val in enumerate(anomalies) if val == True]
         
      plt.legend(fontsize=12)
      plt.tight_layout()

      return plt

   def save_plot_image(self, plt, test):
      
      png_path = f"plots/{test}_{self.category}.png"
      os.makedirs("plots", exist_ok=True)
      plt.savefig(png_path)
      plt.close()

   def plot_results(self):
      """
      Generates anomaly-highlighted plots.
      """

      # Need to see what to do if no data for hash on certain machine
      self.metrics = self.organize_data_by_test()
      self.hashes = self.rearrange_hashes()

      # Create one plot per test
      for test in self.metrics:
         plt = self.generate_figure(test)
         plt = self.add_test_metrics_by_machine(plt, test)
         self.save_plot_image(plt, test)


def main():

   # Don't need to commit/push old plots cuz that has presumably already been done
   # Maybe need to make new plots w/most recent commit? 
   try: 
      data = load_json_from_file(f"{os.environ.get('PLOT_DATA')}/historical_runtime_memory.json")
      for category in ["runtime", "memory"]:
         plot_manager = PlotManager(data, category)
         plot_manager.plot_results()
   except FileNotFoundError:
      logging.error("Could not load JSON file.")
      sys.exit()
   except:
      sys.exit()

   return plot_manager

if __name__ == "__main__":

   main()