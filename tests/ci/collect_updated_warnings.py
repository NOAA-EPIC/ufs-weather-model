import re
import os
import subprocess

# 🔧 Thresholds
MEMORY_THRESHOLD_RATIO = 0.50
TIME_THRESHOLD_RATIO = 0.50

MACHINES = ["hera", "gaeac6", "ursa", "orion", "hercules", "derecho", "wcoss2", "acorn"]

def parse_test_resources(log_path):
    pattern = r"TEST \'(.*)\' \[\d+:\d+, (\d+):(\d+)\]\((\d+) MB\)"
    results = {}
    with open(log_path) as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                test_name, hh, mm, mem = match.groups()
                total_minutes = int(hh) * 60 + int(mm)
                results[test_name] = {
                    "core_minutes": total_minutes,
                    "memory_MB": int(mem)
                }
    return results

def log_was_updated(file_path):
    try:
        result = subprocess.run(
            ["git", "diff", "origin/develop...HEAD", "--", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False

def compare_logs(machine, feature_dir, baseline_dir):
    file_name = f"RegressionTests_{machine}.log"
    f_path = os.path.join(feature_dir, file_name)
    b_path = os.path.join(baseline_dir, file_name)

    if not os.path.exists(f_path):
        return f"- ❌ `{machine}`: Feature log not found.\n"
    if not os.path.exists(b_path):
        return f"- ❌ `{machine}`: Baseline log not found.\n"
    if not log_was_updated(f_path):
        return f"- ⏸️ `{machine}`: Log unchanged in feature branch.\n"

    f_data = parse_test_resources(f_path)
    b_data = parse_test_resources(b_path)

    warnings = []
    for test in f_data:
        if test in b_data:
            f_mem = f_data[test]["memory_MB"]
            b_mem = b_data[test]["memory_MB"]
            f_time = f_data[test]["core_minutes"]
            b_time = b_data[test]["core_minutes"]

            mem_increase = (f_mem - b_mem) / b_mem if b_mem > 0 else 0
            time_increase = (f_time - b_time) / b_time if b_time > 0 else 0

            if mem_increase > MEMORY_THRESHOLD_RATIO or time_increase > TIME_THRESHOLD_RATIO:
                warning = f"- ⚠️ `{test}` exceeded threshold:"
                if mem_increase > MEMORY_THRESHOLD_RATIO:
                    warning += f"\n  • Memory: {b_mem} → {f_mem} MB (+{mem_increase*100:.1f}%)"
                if time_increase > TIME_THRESHOLD_RATIO:
                    warning += f"\n  • Core time: {b_time} → {f_time} min (+{time_increase*100:.1f}%)"
                warnings.append(warning)
        else:
            warnings.append(f"- ℹ️ `{test}`: No baseline found")

    if warnings:
        return f"<details><summary>🔍 `{machine}` Resource Warnings</summary>\n\n" + "\n".join(warnings) + "\n</details>\n"
    return ""

def collect_all_warnings(feature_dir, baseline_dir, output_path):
    with open(output_path, "w") as out:
        out.write("🚨 **Regression Resource Warnings**\n\n")
        for machine in MACHINES:
            summary = compare_logs(machine, feature_dir, baseline_dir)
            if summary:
                out.write(summary + "\n")
