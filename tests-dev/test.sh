python build_rocotoxml.py \
  --machine orion \
  --user_yaml ufs_test.yaml \
  --baseline_yaml baseline_setup.yaml \
  --output workflow.xml

python build_rocotoxml.py \
  --machine orion \
  --name_case "datm_cdeps_control_cfsr intel" \
  --yamls_dir tests-yamls/configs/by_app \
  --baseline_yaml baseline_setup.yaml \
  --output workflow.xml

python build_rocotoxml.py \
  --machine orion \
  --changes_list test_changes.list \
  --yamls_dir tests-yamls/configs/by_app \
  --baseline_yaml baseline_setup.yaml \
  --output workflow.xml

python build_rocotoxml.py \
  --machine orion \
  --manifest app_manifest.yaml \
  --yamls_dir tests-yamls/configs/by_app \
  --baseline_yaml baseline_setup.yaml \
  --output workflow.xml
