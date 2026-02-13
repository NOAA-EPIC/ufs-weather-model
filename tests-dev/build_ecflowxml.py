"""
build_ecflowxml.py

Generates an ECFLOW-compatible XML workflow file from modular YAML configurations.

Supports:
- --user_yaml: Use a custom YAML directly
- --name_case: Target a specific test_name + compiler pair
- --changes_list: Filter tests based on a test_changes.list file
- --manifest: Merge app YAMLs listed in a manifest file

Additional features:
- --dry_run: Preview matched tests without writing XML
- --project: Filter tests by project tag
- --output: Specify output XML filename
- --machine: Target machine for entity resolution

Author: Jong Kim
"""

import argparse
import yaml
from pathlib import Path
from ecflowbuilder import ECFLOWXMLBuilder

def parse_test_changes(path):
    test_map = {}
    raw_entries = []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            test_name, compiler = parts
            test_map[(test_name, compiler.lower())] = True
            raw_entries.append(f"{test_name}_{compiler}")
    return test_map, raw_entries

def load_manifest(manifest_path):
    with open(manifest_path) as f:
        return yaml.safe_load(f).get("apps", [])

def load_baseline_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

def load_all_app_yamls(yaml_dir):
    merged = {}
    for path in Path(yaml_dir).glob("*.yaml"):
        with open(path) as f:
            merged.update(yaml.safe_load(f))
    return merged

def merge_app_yamls(apps, base_dir):
    merged = {}
    for app in apps:
        app_path = Path(base_dir) / f"{app}.yaml"
        if app_path.exists():
            with open(app_path) as f:
                merged.update(yaml.safe_load(f))
        else:
            print(f"⚠️ Missing app YAML: {app_path}")
    return merged

def filter_yaml_by_test_map(rt_yaml, test_map):
    filtered = {}
    matched = set()

    for key, block in rt_yaml.items():
        build = block.get("build", {})
        compiler = build.get("compiler", "unknown").lower()

        matched_tests = []
        for test in block.get("tests", []):
            for test_name in test:
                if (test_name, compiler) in test_map:
                    matched_tests.append(test)
                    matched.add(f"{test_name}_{compiler}")

        if matched_tests:
            filtered[key] = {
                "build": build,
                "tests": matched_tests
            }

    return filtered, matched

def main():
    parser = argparse.ArgumentParser(description="Generate ECFLOW XML workflow")
    parser.add_argument("--machine", required=True)
    parser.add_argument("--baseline_yaml", default="baseline_setup.yaml")
    parser.add_argument("--yamls_dir", default="tests-yamls/configs/by_app")
    parser.add_argument("--manifest", default="app_manifest.yaml")
    parser.add_argument("--changes_list", default=None)
    parser.add_argument("--user_yaml", default=None)
    parser.add_argument("--name_case", default=None)
    parser.add_argument("--output", default="ecflow_workflow.xml")
    parser.add_argument("--project", default=None)
    parser.add_argument("--dry_run", action="store_true")

    args = parser.parse_args()
    baseline_config = load_baseline_config(args.baseline_yaml)

    if args.user_yaml:
        with open(args.user_yaml) as f:
            rt_yaml = yaml.safe_load(f)
        filter_tests = None

    elif args.name_case:
        parts = args.name_case.strip().split()
        if len(parts) != 2:
            raise ValueError("❌ --name_case must be in format 'test_name compiler'")
        test_name, compiler = parts
        compiler = compiler.lower()
        full_yaml = load_all_app_yamls(args.yamls_dir)

        matched_key = None
        for key, block in full_yaml.items():
            block_compiler = block.get("build", {}).get("compiler", "unknown").lower()
            if block_compiler != compiler:
                continue
            for test in block.get("tests", []):
                if test_name in test:
                    matched_key = key
                    break
            if matched_key:
                break

        if not matched_key:
            raise ValueError(f"❌ Test name '{test_name}' with compiler '{compiler}' not found in any YAML")

        rt_yaml = {matched_key: full_yaml[matched_key]}
        filter_tests = {f"{test_name}_{compiler}"}

    elif args.changes_list:
        test_map, raw_entries = parse_test_changes(args.changes_list)
        full_yaml = load_all_app_yamls(args.yamls_dir)
        rt_yaml, matched = filter_yaml_by_test_map(full_yaml, test_map)
        filter_tests = set(matched)

        if args.dry_run:
            print("\n🧪 Dry Run: Matched Tests")
            for entry in sorted(matched):
                print(f"  ✅ {entry}")
            skipped = [entry for entry in raw_entries if entry not in matched]
            if skipped:
                print("\n⚠️ Skipped Entries:")
                for entry in skipped:
                    print(f"  ❌ {entry}")
            print("\n🛑 Dry run complete. No XML written.\n")
            return

    else:
        apps = load_manifest(args.manifest)
        rt_yaml = merge_app_yamls(apps, args.yamls_dir)
        filter_tests = None

    builder = ECFLOWXMLBuilder(
        machine=args.machine,
        rt_yaml=rt_yaml,
        baseline_yaml=args.baseline_yaml,
        project=args.project,
        filter_tests=filter_tests
    )
    builder.generate()
    builder.write(args.output)

if __name__ == "__main__":
    main()
