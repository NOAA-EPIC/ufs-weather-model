import requests
import os
import json
from datetime import datetime
import re
import numpy as np

def get_commits(machine, token):

   url=f"https://api.github.com/repos/ufs-community/ufs-weather-model/commits?path=tests/logs/RegressionTests_{machine}.log"
   headers = {
      "Accept": "application/vnd.github.v3+json",
      "Authorization": "token {token}",
      "X-GitHub-Api-Version": "2022-11-28"
   }

   response = requests.get(url, headers=headers, auth=("gspetro-NOAA", token)) 
   response = json.loads(response.text)
   commits = []
   for num in range(len(response)): 
      commits.append(response[num]['sha'])
   
   return commits

def get_file_info(commits, machine, token): 

   contents = []
   base_url=f"https://api.github.com/repos/ufs-community/ufs-weather-model/contents/tests/logs/RegressionTests_{machine}.log"
   headers = {
      "Accept": "application/vnd.github.v3+json",
      "Authorization": "token {token}",
      "X-GitHub-Api-Version": "2022-11-28",
      "Accept": "application/vnd.github.raw"
   }
   
   for num in range(len(commits)): 
      url = base_url+f"?ref={commits[num]}"
      r = requests.get(url, headers=headers, auth=("gspetro-NOAA", token))
      contents.append(r.text)

   return contents
   
def parse_file(file_contents):
   test_data = {}
   test_pattern = r"TEST \'(.*)\' \[\d+:\d+, (\d+):(\d+)\]\((\d+) MB\)"
   
   for item in file_contents:
      date_pattern = r"Starting Date/Time: .*\n"
      date_match = re.search(date_pattern, item)
      if date_match:
         date_string = date_match.group(0)[19:].strip()
         # Strip microseconds
         date_string = re.sub(r"\.\d+", "", date_string)
         try:
            date = datetime.strptime(date_string, "%Y%m%d %H:%M:%S")
         except(ValueError):
            date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
         except: 
            print("Skipping log for ", date_string)
            continue
      item = item.splitlines()
      for line in item:
         test_match = re.search(test_pattern, line)
         if test_match:
            test_name, hh, mm, mem = test_match.groups()
            try:
               total_minutes = int(hh) * 60 + int(mm)
               test_data[test_name]["date"].append(date)
               test_data[test_name]["runtime"].append(total_minutes)
               test_data[test_name]["memory"].append(int(mem))
            except(KeyError): 
               total_minutes = int(hh) * 60 + int(mm)
               test_data[test_name] = {"date": [date], "runtime": [total_minutes], "memory": [int(mem)]}

   return test_data

def calculate_stats(test_hist):
   stats = {}
   for test in test_hist:
      runtime_mean = np.mean(test_hist[test]["runtime"])
      runtime_stdev = np.std(test_hist[test]["runtime"])
      memory_mean = np.mean(test_hist[test]["memory"])
      memory_stdev = np.std(test_hist[test]["memory"])
      stats[test] = [runtime_mean, runtime_stdev, memory_mean, memory_stdev]
      #print("Test: ", test, stats[test])

   return stats

def create_machine_stats(stats, machine):
   
   with open(f"stats_{machine}.txt", 'a') as fh:
      for test in stats: 
         stats_list = [str(test), str(stats[test][0]), str(stats[test][1]), str(stats[test][2]), str(stats[test][3])]
         stats_string = ", ".join(stats_list)
         fh.write(stats_string + "\n")


if __name__ == "__main__":

   token = os.environ.get('GITHUB_TOKEN')
   machines = ["acorn", "derecho", "gaeac6", "hera", "hercules", "orion", "ursa", "wcoss2"]
   for machine in machines:
      print(machine.upper())
      commits = get_commits(machine, token)
      contents = get_file_info(commits, machine, token)
      historical_results = parse_file(contents)
      stats = calculate_stats(historical_results)
      create_machine_stats(stats, machine)


   

   



