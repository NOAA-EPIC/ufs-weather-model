#!/usr/bin/env bash
set -uo pipefail

input_file="${1:-env4ufs.txt}"
field_sep='|'

if [[ ! -f "${input_file}" ]]; then
    printf "ERROR: input file not found: %s\n" "${input_file}" >&2
    exit 1
fi

if [[ ! -x ./compile.sh ]]; then
    printf "ERROR: ./compile.sh not found or not executable\n" >&2
    exit 1
fi

export MACHINE_ID="${MACHINE_ID:-container}"
echo "MACHINE_ID=$MACHINE_ID"
read -p "  ...press Enter to keep, or type new value: " INPUT
if [[ -n "$INPUT" ]]; then
    export MACHINE_ID="$INPUT"
    echo "Using MACHINE_ID=$MACHINE_ID "
fi

printf "Preparing automated UFS WM compile sequence for MACHINE_ID=%s\n" "${MACHINE_ID}"

if [[ "${MACHINE_ID}" == "container" ]]; then

# Optional: keep the same container-environment check used in env4ufs_compile.sh.
  if [[ -n "${APPTAINER_CONTAINER:-}" ]]; then
      export CONTAINER=APPTAINER
  elif [[ -n "${SINGULARITY_CONTAINER:-}" ]]; then
      export CONTAINER=SINGULARITY
  else
      printf "WARNING: no APPTAINER_CONTAINER or SINGULARITY_CONTAINER detected.\n" >&2
      printf "         Are you in the running container environment to proceed with building the code?\n" >&2
      read -r -n 1 -s -p "Press any key to continue, or Ctrl+C to quit... "
      printf "\n"
  fi
fi

declare -a compile_ids=()
declare -a make_opts=()
declare -A tests_by_compile_id=()

first_line_read=false
current_compile_id=""

trim() {
    local value="$1"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    printf "%s" "${value}"
}

find_fv3_exe() {
    local compile_id="$1"
    local exe_name="fv3_${compile_id}.exe"
    local candidates=(
        "./${exe_name}"
        "./build_fv3_${compile_id}/${exe_name}"
        "./tests/build_fv3_${compile_id}/${exe_name}"
    )

    local candidate
    for candidate in "${candidates[@]}"; do
        if [[ -f "${candidate}" ]]; then
            printf "%s\n" "${candidate}"
            return 0
        fi
    done

    return 1
}

while IFS= read -r line || [[ -n "${line}" ]]; do

    # Remove possible Windows carriage return.
    line="${line%$'\r'}"

    # Skip empty or whitespace-only lines.
    if [[ -z "${line//[[:space:]]/}" ]]; then
        continue
    fi

    # Skip comment lines that begin with # after optional leading whitespace.
    if [[ "${line}" =~ ^[[:space:]]*# ]]; then
        continue
    fi

    # ----------------------------------------------------------------------
    # 1. Read the first non-empty, non-comment line.
    #    Field 1 -> RT_COMPILER
    #    Field 2 -> TPN
    #    Field 3 -> DISKNM
    #    Field 4 -> CONTAINERLOC
    # ----------------------------------------------------------------------

    if [[ "${first_line_read}" == false ]]; then

        IFS="${field_sep}" read -r field1 field2 field3 field4 rest <<< "${line}"

        export RT_COMPILER="$(trim "${field1:-}")"
        export TPN="$(trim "${field2:-}")"
        export DISKNM="$(trim "${field3:-}")"
        export CONTAINERLOC="$(trim "${field4:-}")"

        first_line_read=true

        printf "RT_COMPILER=%s\n" "${RT_COMPILER}"
        printf "TPN=%s\n" "${TPN}"
        printf "DISKNM=%s\n" "${DISKNM}"
        printf "CONTAINERLOC=%s\n" "${CONTAINERLOC}"

        continue
    fi

    # ----------------------------------------------------------------------
    # 2. Read subsequent lines.
    #    If the first field is uppercase:
    #      a) convert first field to lowercase -> COMPILE_ID
    #      b) second field -> MAKE_OPT
    #
    #    Store all COMPILE_ID and MAKE_OPT values in arrays.
    # ----------------------------------------------------------------------

    if [[ "${line}" == *"${field_sep}"* ]]; then
        IFS="${field_sep}" read -r field1 field2 rest <<< "${line}"
    else
        field1="${line}"
        field2=""
    fi

    field1="$(trim "${field1:-}")"
    field2="$(trim "${field2:-}")"

    if [[ "${field1}" =~ ^[[:upper:]][[:upper:]0-9_]*$ ]]; then

        current_compile_id="${field1,,}"
        make_opt="${field2}"

        if [[ -z "${make_opt}" ]]; then
            printf "WARNING: skipping %s because MAKE_OPT field is empty\n" "${field1}" >&2
            current_compile_id=""
            continue
        fi

        compile_ids+=( "${current_compile_id}" )
        make_opts+=( "${make_opt}" )
        tests_by_compile_id["${current_compile_id}"]=""
        continue
    fi

    # ----------------------------------------------------------------------
    # 3. Continue reading.
    #    If the first field starts with a lowercase letter, treat it as a
    #    TEST_NAME belonging to the most recent COMPILE_ID.
    # ----------------------------------------------------------------------

    if [[ "${field1}" =~ ^[[:lower:]] ]]; then

        if [[ -z "${current_compile_id}" ]]; then
            printf "WARNING: test name %s has no active COMPILE_ID; skipping\n" "${field1}" >&2
            continue
        fi

        tests_by_compile_id["${current_compile_id}"]+="${field1}"$'\n'
        continue
    fi

    # ----------------------------------------------------------------------
    # 4. If a line is empty, skip it.
    # ----------------------------------------------------------------------

    # Empty lines are handled near the top of the loop.

done < "${input_file}"

if [[ "${first_line_read}" == false ]]; then
    printf "ERROR: no non-empty, non-comment lines found in %s\n" "${input_file}" >&2
    exit 1
fi

if [[ "${#compile_ids[@]}" -eq 0 ]]; then
    printf "ERROR: no uppercase compile sections found in %s\n" "${input_file}" >&2
    exit 1
fi

printf "\nFound %d compile configurations:\n" "${#compile_ids[@]}"

for i in "${!compile_ids[@]}"; do
    compile_id="${compile_ids[$i]}"

    printf "  %2d: COMPILE_ID=%s\n" "$((i+1))" "${compile_id}"
    printf "      MAKE_OPT=%s\n" "${make_opts[$i]}"

    if [[ -n "${tests_by_compile_id[$compile_id]}" ]]; then
        printf "      TEST_NAME list:\n"
        while IFS= read -r test_name; do
            [[ -z "${test_name}" ]] && continue
            printf "        - %s\n" "${test_name}"
        done <<< "${tests_by_compile_id[$compile_id]}"
    else
        printf "      TEST_NAME list: none\n"
    fi
done

printf "==== Finished reading input file %s =====\n" "${input_file}"
printf "\nStarting compile sequence...\n\n"
read -r -n 1 -s -p "Press any key to continue, or Ctrl+C to quit... "
printf "\nContinuing...\n"

# ----------------------------------------------------------------------
# 5. In a loop over all recorded COMPILE_ID and MAKE_OPT values,
#    run compile.sh, unless fv3_${COMPILE_ID}.exe already exists.
# ----------------------------------------------------------------------

for i in "${!compile_ids[@]}"; do

    export COMPILE_ID="${compile_ids[$i]}"
    export MAKE_OPT="${make_opts[$i]}"

    printf "=====================================================================\n"
    printf "Running compile %d of %d\n" "$((i+1))" "${#compile_ids[@]}"
    printf "MACHINE_ID=%s\n" "${MACHINE_ID}"
    printf "RT_COMPILER=%s\n" "${RT_COMPILER}"
    printf "TPN=%s\n" "${TPN}"
    printf "DISKNM=%s\n" "${DISKNM}"
    printf "CONTAINERLOC=%s\n" "${CONTAINERLOC}"
    printf "COMPILE_ID=%s\n" "${COMPILE_ID}"
    printf "MAKE_OPT=%s\n" "${MAKE_OPT}"
    printf "=====================================================================\n"

    if exe_path="$(find_fv3_exe "${COMPILE_ID}")"; then
        printf "Found executable: %s; proceeding to the next COMPILE_ID\n" "${exe_path}"
        continue
    fi

    printf "Executable fv3_%s.exe not found; compiling COMPILE_ID=%s\n" \
        "${COMPILE_ID}" "${COMPILE_ID}" >&2

    if ./compile.sh "${MACHINE_ID}" "${MAKE_OPT}" "${COMPILE_ID}" "${RT_COMPILER}"; then
        printf "SUCCESS: COMPILE_ID=%s completed successfully\n" "${COMPILE_ID}"
    else
        rc=$?
        printf "ERROR: COMPILE_ID=%s failed with exit code %d\n" "${COMPILE_ID}" "${rc}" >&2
        printf "       Continuing to the next compile configuration.\n" >&2
        continue
    fi

done

printf "==== Finished running run_ufs_compiles_from_envfile.sh =====\n"
