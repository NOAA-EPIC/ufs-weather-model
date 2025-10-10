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
   """Create a markdown file named summary.md with the PR# in the title."""
   pr_num = os.environ.get('PR_NUM')
   mdFile = MdUtils(file_name='summary.md', title=f'Test Summary for PR #{pr_num}')

   return mdFile

def build_content(category):
   """Load the runtime or memory results dictionary, convert to dataframe, and return the results
   Args: 
      category (str): "runtime" or "memory"
   Returns:
      results: DataFrame containing the runtime/memory testing results. Rows are tests and columns are machines.
   """

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
      warn = '⚠️'
      fail = '❌'
      # If there is a warn or fail in the row, add the row to contents to be printed
      if (data.loc[index] == warn).any() or (data.loc[index] == fail).any():
         contents.append(str(index))
         for item in row:
            contents.append(item)
   
   mdFile.new_table(columns=(len(machines) + 1), rows=(len(data) + 1), text_align='center', text=contents)
   mdFile.new_paragraph('\n')
   mdFile.write('</details>')

   return mdFile

def create_summary():
   """Append a results or memory header and key and call write_contents() to write the runtime/memory table to the file.
   Returns:
      mdFile: A markdown file
   """

   categories = ['runtime', 'memory']

   mdFile = create_mdFile()

   for category in categories: 
      # Create <details> section
      mdFile.write(f"<details><summary><h3>{category.upper()} Results Summary</h3></summary>")
      mdFile.new_paragraph('\n')
      # Add key to section
      mdFile.new_paragraph("<h4>Key:</h4>")
      mdFile.new_paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ = NORMAL: {category}. {category.title()} falls within two standard deviations of the mean.")
      mdFile.new_paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;⚠️ = {category.title()} WARNING: {category.title()} is greater than two standard deviations above the mean.")
      mdFile.new_paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;❌ = {category.title()} FAIL: For the past 2+ PRs, {category} has been greater than two standard deviations above the mean.")
      mdFile.new_paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;N/A = Test does not run on this machine.")
      mdFile.new_paragraph('\n')
      # Create a DataFrame w/the runtime/memory results content
      data = build_content(category)
      # Write the content to a file
      mdFile = write_content(data, mdFile)
   
   return mdFile
   
def main():

   summary = create_summary()
   print(summary.get_md_text())

if __name__ == "__main__":
   
   main()