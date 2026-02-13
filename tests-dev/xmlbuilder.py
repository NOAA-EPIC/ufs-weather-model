"""
xmlbuilder.py

Defines RocotoXMLBuilder, a class for constructing Rocoto XML workflows
from modular YAML configurations used in UFS regression testing.

Features:
- Builds compile and test tasks with correct dependencies
- Supports filtering by test_name + compiler
- Resolves machine-specific entities from baseline_setup.yaml
- Outputs well-indented XML with Rocoto-compatible structure

Usage:
    builder = RocotoXMLBuilder(machine, rt_yaml, baseline_yaml)
    builder.generate()
    builder.write("workflow.xml")

Author: Jong Kim
"""

import yaml
import xml.etree.ElementTree as ET
import os
import re
from typing import Optional

def resolve_env_vars(value: str) -> str:
    """
    Resolves environment variables in a string of the form ${VAR}.

    Args:
        value (str): Input string with optional ${VAR} patterns.

    Returns:
        str: String with environment variables substituted.
    """
    if not isinstance(value, str):
        return ""
    pattern = re.compile(r"\$\{(\w+)\}")
    return pattern.sub(lambda m: os.environ.get(m.group(1), m.group(0)), value)

class RocotoXMLBuilder:
    """
    Builds a Rocoto XML workflow from a YAML configuration.

    Attributes:
        machine (str): Target machine name.
        rt_yaml (dict): Runtime YAML configuration.
        baseline_config (dict): Baseline setup configuration.
        project (Optional[str]): Optional project filter.
        filter_tests (Optional[set]): Optional set of test_name_compiler strings to include.
        root (Element): Root XML element for the workflow.
    """

    def __init__(self, machine, rt_yaml, baseline_yaml, project=None, filter_tests=None):
        """
        Initializes the RocotoXMLBuilder.

        Args:
            machine (str): Target machine name.
            rt_yaml (dict or str): Parsed YAML dictionary or path to YAML file.
            baseline_yaml (str): Path to baseline_setup.yaml.
            project (Optional[str]): Optional project filter.
            filter_tests (Optional[set]): Optional set of test_name_compiler strings to include.
        """
        self.machine = machine
        self.project = project
        self.filter_tests = filter_tests
        self.rt_config = rt_yaml if isinstance(rt_yaml, dict) else yaml.safe_load(open(rt_yaml))
        self.baseline_config = yaml.safe_load(open(baseline_yaml))
        self.root = ET.Element("workflow", attrib={
            "realtime": "F",
            "scheduler": "slurm",
            "taskthrottle": "10"
        })

    def _add_cycledef(self):
        """Adds a cycledef element to the XML root."""
        ET.SubElement(self.root, "cycledef", name="forecast", start="2025010100", end="2025123100", interval="06:00:00")

    def _add_log(self):
        """Adds a log element to the XML root."""
        ET.SubElement(self.root, "log").text = "&LOG;/workflow.log"

    def _add_compile_task(self, key, build):
        """
        Adds a compile task to the XML workflow.

        Args:
            key (str): Unique identifier for the test block.
            build (dict): Build configuration dictionary.
        """
        compiler = build.get("compiler", "unknown").lower()
        option = build.get("option", "")
        task_name = f"compile_{key}"
        task = ET.SubElement(self.root, "task", name=task_name)
        cmd = f"&PATHRT;/run_compile.sh &PATHRT; &RUNDIR_ROOT; \"{option}\" {key} 2>&1 | tee &LOG;/compile_{key}.log"
        ET.SubElement(task, "command").text = cmd
        ET.SubElement(task, "jobname").text = task_name
        ET.SubElement(task, "account").text = "GFS-DEV"
        ET.SubElement(task, "queue").text = "batch"
        ET.SubElement(task, "partition").text = self.machine
        ET.SubElement(task, "nodes").text = "1"
        ET.SubElement(task, "walltime").text = "00:30:00"
        ET.SubElement(task, "join").text = f"&RUNDIR_ROOT;/compile_{key}.log"
        ET.Sub
