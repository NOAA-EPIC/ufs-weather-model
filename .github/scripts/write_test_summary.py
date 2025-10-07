import os
import json
import re
from mdutils.mdutils import MdUtils
import pandas as pd

def load_json(file_path):
   """Convert JSON file to python dictionary."""
   with open(file_path, 'r', encoding='utf-8') as file:
      data = json.load(file)

   return data

def create_mdFile():
   pr_num = os.environ.get('PR_NUM')
   mdFile = MdUtils(file_name='summary.md', title=f'Test Summary for PR #{pr_num}')

   return mdFile

def build_content(category):

   machines = os.environ.get('MACHINES').split()
   contents = load_json(os.environ.get(f"{category.upper()}_RESULTS"))
   results = pd.DataFrame()
   
   for machine in machines:

      machine_results = pd.DataFrame.from_dict(contents[machine], orient='index',columns=[machine])
      results = pd.merge(results, machine_results, left_index=True, right_index=True, how='outer').fillna("N/A")

   return results

def write_content(data, mdFile):
   
   machines = os.environ.get('MACHINES').split()
   
   # Build contents list starting with header row
   contents = ["Test"] + machines

   # Create table

   for index, row in data.iterrows():

      contents.append(str(index))
      for item in row:   
         contents.append(item)
   
   mdFile.new_table(columns=(len(machines) + 1), rows=(len(data) + 1), text_align='center', text=contents)
   mdFile.new_paragraph('\n')
   mdFile.write('</details>')

   return mdFile

def create_summary():
   
   categories = ['runtime', 'memory']

   mdFile = create_mdFile()

   for category in categories: 
      data = build_content(category)
      mdFile.write(f"<details><summary><h3>{category.upper()} Results Summary</h3></summary>")
      mdFile.new_paragraph('\n')
      mdFile.new_paragraph("<h4>Key:</h4>")
      mdFile.new_paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ = <span style='color: green;'>NORMAL</span> {category}. {category.title()} falls within two standard deviations of the mean.")
      mdFile.new_paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;⚠️ = {category.title()} <span style='color: yellow;'>WARNING</span>: {category.title()} is greater than two standard deviations above the mean.")
      mdFile.new_paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;❌ = {category.title()} <span style='color: red;'>FAIL</span>: For the past 2+ PRs, {category} has been greater than two standard deviations above the mean.")
      mdFile.new_paragraph('\n')
      mdFile = write_content(data, mdFile)
   
   return mdFile
   
def main():

   summary = create_summary()
   print(summary.get_md_text())

if __name__ == "__main__":
   
   main()