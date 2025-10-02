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

def build_runtime_content(contents, mdFile):
   table_content = ["Tests", "Runtime"]
   fails = 0

   for test in contents:  
      if contents[test][0].startswith("❌ FAIL"):
         table_content.append(test)
         table_content.append(contents[test][0])
         fails += 1

   return table_content, fails

def build_memory_content(contents, mdFile):
   table_content = ["Tests", "Memory"]
   fails = 0
   
   for test in contents:  
      if contents[test][1].startswith("❌ FAIL"):
         table_content.append(test)
         table_content.append(contents[test][1])
         fails += 1

   return table_content, fails

def build_content(contents, mdFile, machine):

   rt_results, rt_fails = build_runtime_content(contents, mdFile)
   mem_results, mem_fails = build_memory_content(contents, mdFile)
   
   # Create a table
   mdFile.write(f"<details><summary>{machine.upper()} - Runtime/Memory Summary</summary>")
   mdFile.new_paragraph('\n')
   mdFile.new_paragraph(f"RUNTIME: {(len(contents) - rt_fails)} / {len(contents)} had normal runtime.")
   mdFile.new_paragraph(f"Tests with anomolously high runtime: ")
   mdFile.new_paragraph('\n')
   mdFile.new_table(columns=2, rows=rt_fails+1, text_align='center', text=rt_results)
   mdFile.new_paragraph('\n')
   mdFile.new_paragraph(f"MEMORY: {(len(contents) - mem_fails)} / {len(contents)} had normal memory usage.")
   mdFile.new_paragraph(f"Tests with anomolously high memory: ")
   mdFile.new_paragraph('\n')
   mdFile.new_table(columns=2, rows=mem_fails+1, text_align='center', text=mem_results)
   mdFile.write('</details>')


if __name__ == "__main__":

   machines = os.environ.get('MACHINES').split()
   results = os.environ.get('RESULTS')
   contents = load_json()
   file = create_mdFile()
   for machine in machines:
      build_content(contents[machine], file, machine)

   print(file.get_md_text())