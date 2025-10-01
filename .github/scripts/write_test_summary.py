import os
import json
import re
import pandas as pd
from mdutils.mdutils import MdUtils

def load_json(json_file):
   """Convert json file to python dictionary"""

   try:
      with open(json_file, 'r') as file:
         data = json.load(file)
      return data
   except FileNotFoundError:
      return "🚫 **Error:** Test results JSON file not found."
   except json.JSONDecodeError:
      return "🚫 **Error:** Could not parse JSON file."

"""def create_test_summary_df(contents):
   df = pd.DataFrame.from_dict(contents, columns=["Runtime", "Memory"], orient='index')
   df.reset_index(inplace=True, names='Test')
   print(df.head())
   print(df['Runtime'].head())
   return df"""
       
def create_test_summary(contents):
   pass
   
   
   return tests, runtime, memory

def create_mdFile():
   pr_num = os.environ.get('PR_NUM')
   mdFile = MdUtils(file_name='summary.md', title=f'PR Test Summary for PR #{pr_num}')

   return mdFile

def build_content(contents, mdFile, machine):
   
   mdFile.new_header(level=1, title=f'{machine} - Tests Completed')

   columns = ["Tests", "Runtime", "Memory"]

   tests = []
   runtime = []
   memory = []
   # Create a table for results
   table_content = [
      "Tests", "Runtime", "Memory"
   ]

   for test in contents:
      table_content.append(test)
      table_content.append(contents[test][0])
      table_content.append(contents[test][1])
    
   # Create the table
   #print(table_content)
   print(len(contents))
   mdFile.new_table(columns=len(columns), rows=len(contents)+1, text_align='center', text=table_content)
   mdFile.new_paragraph('\n'),
   
   return mdFile.get_md_text()

def create_file(contents):
   """Create a json file with statistic for each test on each machine"""

   with open(f"summary.md", 'a') as fh:
      fh.write(contents)

if __name__ == "__main__":

   token = os.environ.get('GITHUB_TOKEN')
   machines = os.environ.get('MACHINES').split()
   #results = load_json(os.environ.get('RESULTS'))
   results = os.environ.get('RESULTS')
   contents = load_json(results)
   test_data = {}
   file = create_mdFile()
   for machine in machines:
      print(machine.upper())
      build_content(contents[machine], file, machine)
      
   print(file.get_md_text())
