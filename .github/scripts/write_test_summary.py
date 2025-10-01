import os
import json
import re
from mdutils.mdutils import MdUtils

def load_json():
   """Convert JSON file to python dictionary."""
   with open(os.environ.get('RESULTS'), 'r', encoding='utf-8') as file:
      data = json.load(file)

   return data

def create_mdFile():
   pr_num = os.environ.get('PR_NUM')
   mdFile = MdUtils(file_name='summary.md', title=f'PR Test Summary for PR #{pr_num}')

   return mdFile

def build_content(contents, mdFile, machine):
   
   mdFile.write('<details><summary>Data Set A</summary>')
   
   mdFile.new_header(level=1, title=f'{machine.upper()} - Tests Completed')

   columns = ["Tests", "Runtime", "Memory"]

   table_content = [
      "Tests", "Runtime", "Memory"
   ]

   for test in contents:
      table_content.append(test)
      table_content.append(contents[test][0])
      table_content.append(contents[test][1])
    
   # Create the table
   mdFile.new_table(columns=len(columns), rows=len(contents)+1, text_align='center', text=table_content)
   mdFile.new_paragraph('\n')
   mdFile.write('</details>')


if __name__ == "__main__":

   machines = os.environ.get('MACHINES').split()
   results = os.environ.get('RESULTS')
   contents = load_json()
   file = create_mdFile()
   for machine in machines:
      build_content(contents[machine], file, machine)

   print(file.get_md_text())