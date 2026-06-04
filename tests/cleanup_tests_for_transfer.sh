#!/bin/bash
set -euo pipefail

cd /contrib/Natalie.Perlin/UFS-WM/ufs-wm-gnuC/tests

echo "Removing *.exe files directly under tests/"
find . -maxdepth 1 -type f -name "*.exe" -print -delete

echo "Cleaning test directories under ./run_container/"
find ./run_container -mindepth 2 -maxdepth 2 \
  ! -name out \
  ! -name err \
  ! -name 'PET000*' \
  -print -exec rm -rf {} +

echo "Cleanup complete."
