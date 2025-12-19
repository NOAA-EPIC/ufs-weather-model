import os
import json
from .APICall import APICall

"""This file contains utility functions to (1) create a JSON file from log data and (2) load data from a 
JSON file into a python dictionary. 
"""

# Utilities for file I/O & plotting
def create_json(dictionary, file_name):
   """Create a json file with statistics for each test on each machine"""

   with open(f"data/{file_name}.json", 'w') as fh:
      json.dump(dictionary, fh, indent=4)

def load_json_from_file(file_path):
   """Convert JSON file to python dictionary."""
   with open(file_path, 'r', encoding='utf-8') as file:
      data = json.load(file)

   return data

def get_hashes(num=1):
   """Retrieve the last "num" commit hashes from the repository.
   Args: 
      num (int): The number of commit hashes to be retrieved. 
   Returns:
      hashes: list of commit hashes
   """
   hashes = []
   api_call = APICall(f"commits?per_page={num}")
   response = api_call.call_API()
   response = api_call.load_json_from_api_call(response)

   for item in response:
      hashes.append(item['sha'][:8])
   #print(hashes)
   return hashes
