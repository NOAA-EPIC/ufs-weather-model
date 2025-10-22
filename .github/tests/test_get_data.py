import requests
import os
import json
from datetime import datetime
import re
import numpy as np
import pytest


# Fixtures: 
@pytest.fixture
def enviroment_variables():

   GITHUB_TOKEN = ""
   BASE_URL = ""
   MACHINES = ""

   return

@pytest.fixture
def api_call():
   endpoint = ""
   return APICall(endpoint)

@pytest.fixture
def log():
   return Log("UrSa")


def test_init_APICall(api_call):

   assert api_call.machine == "rhea"
   assert api_call.token == os.environ.get('GITHUB_TOKEN')
   assert api_call.base_url == ""
   assert api_call.endpoint == ""
   assert api_call.url == f"{api_call.base_url}/{api_call.endpoint}"
   assert api_call.num_commits == 1
   assert api_call.header == {
         "Accept": "application/vnd.github.v3+json",
         "Authorization": f"Bearer {api_call.token}",
         "X-GitHub-Api-Version": "2022-11-28",
         "Accept": "application/vnd.github.raw"
      }

def test_init_Log(log):

   assert log.machine == "ursa"
   assert log.text_per_log == []

def test_call_API(api_call):

   response = requests.get(api_call.url, headers=api_call.header)
   response = json.loads(response.text)
   
   assert response == ""
