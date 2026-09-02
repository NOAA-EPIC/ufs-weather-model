import pytest
import os
import logging
from mdutils.mdutils import MdUtils
from scripts.Manager import *
from scripts.generate_message_text import *

#@pytest.mark.parametrize("category", ["runtime", "memory"])
def test_init_MessageManager(self):

   message_manager = MessageManager()

   assert message_manager.contents.keys == ["runtime", "memory"]
   assert message_manager.results.keys == ["runtime", "memory"]
   assert message_manager.message_content == ""


def test_get_test_names(self, data):
         """Create a set containing all test names by extracting the tests (keys) from the data
         Returns:
            all_tests: Set of all test names
         """
         all_tests = set()
         for data_by_machine in data.values():
            all_tests.update(data_by_machine.keys())
         
         return all_tests

def test_organize_data_by_test(self, data):
         """Creates new runtime/memory dictionaries that use test name as key and have data for each machine 
         under each test. 
         Returns:
            results (dict): Pass/fail data for each test and machine. Primary key is test. Secondary key is machine:
               {'datm_cdeps_ciceC_cfsr_intel': 
                  {'acorn': {'cb16f329': 188, 'ead2c35f': 188, ...}
                  'gaeac6': {'cb16f329': 119, 'ead2c35f': 120, ...}}
               }
         """

         tests = self.get_test_names(data)

         results = {}

         for test in tests:
            for machine, test_data in data.items():
               if test not in test_data:
                  continue # No data to add
               else:
                  results.setdefault(test, {}).update({machine: test_data[test]})
                  
         return results

# For runtime and memory! 
def test_create_message_content(self, data, category):
      """If there are tests whose runtime/memory results are 2 standard deviations above the mean for 3+ tests, 
      append this information to self.message_content.
      """
      fail = '❌'
      self.results[category].update(self.organize_data_by_test(data))

      matching = {}
      for test, result in self.results[category].items(): 
         for machine, is_fail in result.items():
            if is_fail == fail:
               matching.setdefault(test, []).append(machine)
               
      if matching:
         self.message_content += f"\nFor the past three PRs, {category.upper()} has been greater than two standard deviations above the mean for the following tests: \n\n"
         for test, machines in matching.items():
            self.message_content+=f"  * {test}: {(", ").join(machines)}\n"

# For runtime, mem, both, and neither
def test_create_md_file(self):
      if self.message_content:
         mdFile = MdUtils(file_name='pr_post.md')
         mdFile.write("### ⚠️ Test Suite Performance Threshold Exceeded")
         mdFile.new_paragraph(self.message_content)
         mdFile.new_paragraph("@gspetro-NOAA")
         mdFile.create_md_file()
         print(mdFile.get_md_text())
         return mdFile
      else:
         logging.error(f"No tests with high runtime or memory.")
         return ""


def test_main():
   
   message_manager = MessageManager()

   for category in message_manager.categories: 
      message_manager.contents[category].update(message_manager.load_json_from_file(os.environ.get(f"{category.upper()}_RESULTS")))
      message_manager.create_message_content(message_manager.contents[category], category)
   
   return message_manager.create_md_file()


if __name__ == "__main__":

   main()
