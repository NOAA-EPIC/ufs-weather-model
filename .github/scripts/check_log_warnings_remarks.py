import requests
from mdutils.mdutils import MdUtils
import os, sys
import json
import re
import logging

class APICall():
   """A GitHub API call"""

   def __init__(self, endpoint='', num_commits=1):
      self.token = os.environ.get('GITHUB_TOKEN')
      self.base_url = os.environ.get('BASE_URL')
      self.endpoint = endpoint
      self.url = f"{self.base_url}/{self.endpoint}" #Could use a path join?
      self.num_commits = num_commits
      self.header = {
         "Accept": "application/vnd.github.v3+json",
         "Authorization": f"Bearer {self.token}",
         "X-GitHub-Api-Version": "2022-11-28",
         "Accept": "application/vnd.github.raw"
      }

class Log():
   """A Regression Test log file."""
   
   def __init__(self, machine):
      """Create the log file object for a specific machine."""
      self.machine = machine.lower()
      self.text_per_log = []

   def call_API(self, endpoint):
      """Call the GitHub API to get information about the log file."""

      api_call = APICall(endpoint)
      response = requests.get(api_call.url, headers=api_call.header)
      if response.status_code != 200:
         logging.error(f"{response}: API call failed for {api_call.url}")
         sys.exit(1)
      response = json.loads(response.text)
      
      return response

   def _get_commits(self):
      """Get PR head and base commits. Structure of response: 
         response = [{"head": {"sha": "a1b2c3d..."}, "base": {"sha": "b2c3d4e..."}}]
         See GitHub documentation for https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits
      """
      response = self.call_API(f"pulls/{os.environ.get('PR_NUM')}")
      self.pr_head_commit = response['head']['sha']
      self.pr_base_commit = response['base']['sha']

   def _fetch_log_text(self, commit): 
      """For each commit of a log, extract the log text."""

      try:
         api_call = APICall(f"contents/tests/logs/RegressionTests_{self.machine}.log")

         url = api_call.url + (f"?ref={commit}") #Could use a path join?
         r = requests.get(url, headers=api_call.header)
         return r.text
      except:
         logging.error(f"No commit found for the ref {commit}")
         sys.exit(1)

   def _get_pr_warn_rmk(self, log_text):
      """Extract warnings/remarks data for a particular commit.
      Returns:
         log_warn_rmk: A dictionary of tests as the key with a tuple of (warnings, remarks) as the value
      """
      
      log_warn_rmk = {}
      
      # Use non-capturing groups in pattern to indicate warnings/remarks may or may not be present.
      compile_pattern = r"COMPILE \'(.*)\' \[\d+:\d+, \d+:\d+\](?: \( (?:(\d+) warnings)?\s*(?:(\d+) remarks)? \))?"

      log_text = log_text.splitlines()

      for line in log_text:
         test_match_compile = re.search(compile_pattern, line)
         if test_match_compile:
            test_name, warnings, remarks = test_match_compile.groups()
            log_warn_rmk[test_name] = (warnings, remarks)
         
      log_warn_rmk = self._clean_data(log_warn_rmk)
      
      return log_warn_rmk

   def _get_failures(self, log_text):
      """For each instance of a log at a given commit, list of failed or skipped tests and compiles
         Args:
            log_text: Log text for a given commit
         Returns: 
            failures: A dictionary of tests (keys) with a tuple of warnings and remarks as the value for each test
      """

      failures = {}

      # Use non-capturing groups in pattern to indicate warnings/remarks may or may not be present.
      failure_pattern = r"^(?:FAILED|SKIPPED): (?!UNABLE TO (?:COMPLETE COMPARISON|START TEST))(.+?) -- (?:TEST|COMPILE) '([^']+)"
      
      log_text = log_text.splitlines()

      for line in log_text:
         failure_match = re.search(failure_pattern, line)
         if failure_match:
            reason, test = failure_match.groups()
            #print(test, reason)
            try:
               failures[reason].append(test)
            except KeyError:
               failures[reason] = [test]
         
      return failures


   def _clean_data(self, test_data):
      """Convert None values to zeros in the test_data dictionary"""
      clean_data = {
         k: tuple(0 if v is None else int(v) for v in values) 
         for k, values in test_data.items()
      }
      return clean_data

   def compare_results(self, pr_log, base_log): 
      """Compare warnings/remarks for PR head and base commits to determine whether warnings/remarks have increased."""

      increases = {'warnings': {}, 'remarks': {}}

      for test in pr_log:
         if test not in base_log:
            logging.info(f"Skipped test {test}; nothing to compare against.")
            continue
         # Check warnings
         if pr_log[test][0] > base_log[test][0]:
            increases['warnings'].update({test: pr_log[test][0] - base_log[test][0]})
         # Check remarks
         if pr_log[test][1] > base_log[test][1]:
            increases['remarks'].update({test: pr_log[test][1] - base_log[test][1]})
      
      return increases

def print_warn_rmk_results(dict):
   """Print the results from the warnings/remarks comparison in HTML."""
   
   pr_num = os.environ.get('PR_NUM')
   mdFile = MdUtils(file_name='warn_rmk.md', title=f'Increased Warnings/Remarks for PR #{pr_num}')

   for machine, results in dict.items():
      for category in results.keys():
         if results[category]:
            mdFile.write(f"\n<h3>{machine.upper()}</h3>\n")
            unordered_list = [f"**{category.title()}:**", []]
            for test, value in dict[machine][category].items():
               unordered_list[1].append(f"{test}: {value}")
            mdFile.new_list(unordered_list, marked_with='*')
   return mdFile.get_md_text()

def print_failure_results(dict):
   """Print the results from the warnings/remarks comparison in HTML."""
   
   pr_num = os.environ.get('PR_NUM')
   mdFile = MdUtils(file_name='failures.md', title=f'Compile and Test Failures for PR #{pr_num}')

   for machine, failures in dict.items():
      for reason, tests in failures.items():
         mdFile.write(f"\n<h3>{machine.upper()}</h3>\n")
         unordered_list = [f"**{reason.upper()}:**", []]
         for test in tests:
            unordered_list[1].append(f"{test}")
         mdFile.new_list(unordered_list, marked_with='*')
   return mdFile.get_md_text()

def main():
   """For each machine, create a log object, get current PR data, and determine 
   which tests increase warnings and/or remarks on each machine.""" 

   machines = os.environ.get('MACHINES').split()

   # For each machine, tests where warnings and/or remarks increase
   increased_warnings_remarks = {}
   failures = {}

   for machine in machines:
      log = Log(machine)
      log._get_commits()
      log.pr_log_text = log._fetch_log_text(log.pr_head_commit)
      log.pr_warn_rmk = log._get_pr_warn_rmk(log.pr_log_text)
      log.pr_failures = log._get_failures(log.pr_log_text)

      log.base_log_text = log._fetch_log_text(log.pr_base_commit)
      log.base_warn_rmk = log._get_pr_warn_rmk(log.base_log_text)
      
      increased_warnings_remarks[machine] = log.compare_results(log.pr_warn_rmk, log.base_warn_rmk)
      failures[machine] = log.pr_failures

   warn_rmk_results = print_warn_rmk_results(increased_warnings_remarks)
   failure_results = print_failure_results(failures)

   if len(warn_rmk_results) > 81: # Length of HTML header
      print(warn_rmk_results)
      print(failure_results)
      sys.exit(1)
   else:
      print(failure_results)
      sys.exit(0)

if __name__ == "__main__": # pragma: no coverage

   main()
