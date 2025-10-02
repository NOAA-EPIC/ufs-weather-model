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
   
   table_content = ["Tests", "Runtime", "Memory"]
   fails = 0

   for test in contents:  
      if contents[test][0].startswith("❌ FAIL") or contents[test][1].startswith("❌ FAIL"):
         table_content.append(test)
         table_content.append(contents[test][0])
         table_content.append(contents[test][1])
         fails += 1
   
   # Create a table
   mdFile.write(f"<details><summary>{machine.upper()} - Tests Completed</summary>")
   mdFile.new_paragraph('\n')
   mdFile.new_paragraph(f"RESULTS: {(len(contents) - fails)} / {len(contents)} had normal runtime and memory usage.")
   mdFile.new_paragraph('\n')
   mdFile.new_paragraph(f"Tests with anomolously high runtime or memory usage: ")
   mdFile.new_paragraph('\n')
   mdFile.new_table(columns=3, rows=fails+1, text_align='center', text=table_content)
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