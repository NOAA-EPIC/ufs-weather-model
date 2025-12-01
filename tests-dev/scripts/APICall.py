import os
import requests
import json

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
   
   def set_endpoint(self, endpoint):
      self.endpoint = endpoint

   def call_API(self):
      """Call the GitHub API."""

      response = requests.get(self.url, headers=self.header)
      response = json.loads(response.text)
      
      return response