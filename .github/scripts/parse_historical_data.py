


import requests
import os
import json
from datetime import datetime
import re

def get_commits(machine, token):

   base_url="https://api.github.com/repos/ufs-community/ufs-weather-model/"
   commit_endpoint=f"commits?path=tests/logs/RegressionTests_{machine}.log"
   headers = {
      "Accept": "application/vnd.github.v3+json",
      "Authorization": "token {token}",
      "X-GitHub-Api-Version": "2022-11-28"
   }

   response = requests.get(base_url+commit_endpoint, headers=headers, auth=("gspetro-NOAA", token)) 
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
   #date_pattern = "Starting Date/Time: *\n"
   #date = re.search(date_pattern)
   
   test_data = {}

   #PASS -- TEST 'cpld_control_p8_mixedmode_intel' [08:49, 06:43](2189 MB)
   test_pattern = r"TEST \'(.*)\' \[\d+:\d+, (\d+):(\d+)\]\((\d+) MB\)"
   
   for item in file_contents:
      date_pattern = r"Starting Date/Time: .*\n"
      date_match = re.search(date_pattern, item)
      print(date_match)
      if date_match:
         date_string = date_match.group(0)[19:].strip()
         try:
            date = datetime.strptime(date_string, "%Y%m%d %H:%M:%S")
            print("Date:", date)
            test_data[date] = {}
         except(ValueError):
            date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            print("Date:", date)
            test_data[date] = {}
         except: 
            print("Skipping log for ", date_string)
            continue
      item = item.splitlines()
      for line in item:
         test_match = re.search(test_pattern, line)
         if test_match:
            print("Match Groups:", test_match.groups())
            test_name, hh, mm, mem = test_match.groups()
            total_minutes = int(hh) * 60 + int(mm)
            test_data[date][test_name] = {
               "core_minutes": total_minutes,
               "memory_MB": int(mem)
            }
            print(test_data[date][test_name])
   return test_data

def calculate_stdev(data):
   pass

if __name__ == "__main__":

   
   token = os.environ.get('GITHUB_TOKEN')
   commits = get_commits("ursa", token)
   contents = get_file_info(commits, "ursa", token)
   historical_results = parse_file(contents)


   with open("sample.txt", 'w') as fh:
      fh.write(contents[0])

   



