#!/usr/bin/env bash
set -uo pipefail

input_file="${1:-env4ufs.txt}"

if [[ ! -f "${input_file}" ]]; then
    printf "ERROR: input file not found: %s\n" "${input_file}" >&2
    exit 1
fi

if [[ ! -x ./run_test.sh ]]; then
    printf "ERROR: ./run_test.sh not found or not executable\n" >&2
    exit 1
fi

if [[ ! -f ./env4ufs_run.sh ]]; then
    printf "ERROR: ./env4ufs_run.sh not found\n" >&2
    exit 1
fi

export MACHINE_ID="${MACHINE_ID:-container}"

printf "Preparing automated UFS WM test sequence for MACHINE_ID=%s\n" "${MACHINE_ID}"

# Optional: keep the same container-environment check used in related scripts.
if [[ -n "${APPTAINER_CONTAINER:-}" ]]; then
    export CONTAINER=APPTAINER
elif [[ -n "${SINGULARITY_CONTAINER:-}" ]]; then
    export CONTAINER=SINGULARITY
else
    printf "WARNING: no APPTAINER_CONTAINER or SINGULARITY_CONTAINER detected.\n" >&2
    printf "   You may need to launch Singularity/Apptainer if you expect to be in a running container environment!\n" >&2
    read -r -n 1 -s -p "Press any key to continue, or Ctrl+C to quit... "
    printf "\n"
fi

trim() {
    local s="$1"
    s="${s#"${s%%[![:space:]]*}"}"
    s="${s%"${s##*[![:space:]]}"}"
    printf "%s" "${s}"
}

declare -a compile_ids=()
declare -a make_opts=()
declare -A tests_by_compile_id

first_line_read=false
current_compile_id=""

while IFS= read -r line || [[ -n "${line}" ]]; do

    # Remove possible Windows carriage return.
    line="${line%$'\r'}"

    # Skip empty or whitespace-only lines.  Empty line ends the current
    # TEST_NAME list for the current COMPILE_ID.
    if [[ -z "${line//[[:space:]]/}" ]]; then
        current_compile_id=""
        continue
    fi

    # Skip comment lines beginning with #, allowing leading whitespace.
    if [[ "${line}" =~ ^[[:space:]]*# ]]; then
        continue
    fi

    # ----------------------------------------------------------------------
    # 1. Read the first non-empty, non-comment line.
    #    Pipe-separated format:
    #
    #      RT_COMPILER|TPN|DISKNM|CONTAINERLOC
    #
    #    Field 1 -> RT_COMPILER
    #    Field 2 -> TPN
    #    Field 3 -> DISKNM
    #    Field 4 -> CONTAINERLOC
    # ----------------------------------------------------------------------

    if [[ "${first_line_read}" == false ]]; then

        IFS='|' read -r field1 field2 field3 field4 rest <<< "${line}"

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
    #    If the first field is uppercase, start a new COMPILE_ID block:
    #
    #      COMPILE_ID|MAKE_OPT
    #
    #    Field 1 -> COMPILE_ID, converted to lowercase
    #    Field 2 -> MAKE_OPT, retained for reporting/consistency
    #
    #    The TEST_NAME lines that follow belong to this COMPILE_ID until
    #    the next empty line or the next uppercase COMPILE_ID block.
    # ----------------------------------------------------------------------

    IFS='|' read -r field1 field2 rest <<< "${line}"

    field1="$(trim "${field1:-}")"
    field2="${field2:-}"
    field2="${field2#"${field2%%[![:space:]]*}"}"

    if [[ "${field1}" =~ ^[[:upper:]][[:upper:]0-9_]*$ ]]; then

        current_compile_id="${field1,,}"
        make_opt="${field2}"

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
    printf "ERROR: no uppercase COMPILE_ID sections found in %s\n" "${input_file}" >&2
    exit 1
fi

printf "\nFound %d COMPILE_ID configurations:\n" "${#compile_ids[@]}"

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

printf "\nStarting test sequence...\n"
read -r -n 1 -s -p "Press any key to continue, or Ctrl+C to quit... "
printf "\nContinuing...\n"

declare -a failed_tests=()
declare -a skipped_tests=()

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

# ----------------------------------------------------------------------
# 5. In a loop over all recorded COMPILE_ID values:
#    a) check whether fv3_${COMPILE_ID}.exe exists
#    b) form the TEST_NAME array for this COMPILE_ID
#    c) source env4ufs_run.sh
#    d) run run_test.sh for each TEST_NAME
#    e) if run_test.sh fails, report failure and continue
# ----------------------------------------------------------------------

for i in "${!compile_ids[@]}"; do

    export COMPILE_ID="${compile_ids[$i]}"
    export MAKE_OPT="${make_opts[$i]}"

    printf "=====================================================================\n"
    printf "Processing tests for COMPILE_ID %d of %d\n" "$((i+1))" "${#compile_ids[@]}"
    printf "MACHINE_ID=%s\n" "${MACHINE_ID}"
    printf "RT_COMPILER=%s\n" "${RT_COMPILER}"
    printf "TPN=%s\n" "${TPN}"
    printf "DISKNM=%s\n" "${DISKNM}"
    printf "CONTAINERLOC=%s\n" "${CONTAINERLOC}"
    printf "COMPILE_ID=%s\n" "${COMPILE_ID}"
    printf "MAKE_OPT=%s\n" "${MAKE_OPT}"
    printf "=====================================================================\n"

    if ! fv3_exe="$(find_fv3_exe "${COMPILE_ID}")"; then
        printf "WARNING: fv3_%s.exe not found; skipping tests for COMPILE_ID=%s\n" \
            "${COMPILE_ID}" "${COMPILE_ID}" >&2
        skipped_tests+=( "${COMPILE_ID}:ALL:missing_executable" )
        continue
    fi

    printf "Found executable: %s\n" "${fv3_exe}"

    mapfile -t test_names <<< "${tests_by_compile_id[$COMPILE_ID]}"

    if [[ "${#test_names[@]}" -eq 0 ]]; then
        printf "WARNING: no TEST_NAME entries found for COMPILE_ID=%s; skipping\n" "${COMPILE_ID}" >&2
        skipped_tests+=( "${COMPILE_ID}:ALL:no_tests" )
        continue
    fi

    for TEST_NAME in "${test_names[@]}"; do

        [[ -z "${TEST_NAME}" ]] && continue

        export TEST_NAME
        export TEST_ID="${TEST_NAME}_${RT_COMPILER}"

        printf "%s\n" "-------------------------------------------------------------------\n"
        printf "Preparing run environment\n"
        printf "COMPILE_ID=%s\n" "${COMPILE_ID}"
        printf "TEST_NAME=%s\n" "${TEST_NAME}"
        printf "TEST_ID=%s\n" "${TEST_ID}"
        printf "%s\n" "---------------------------------------------------------------------\n"

        # Source env4ufs_run.sh so variables remain available in this driver.
        # The blank lines answer the interactive prompts by pressing Enter.
	export RTVERBOSE="false"
        source ./env4ufs_run.sh <<< "$(printf '\n%.0s' {1..50})"

        printf "\nRunning test:\n"
        printf "  PATHRT=%s\n" "${PATHRT}"
        printf "  RUNDIR_ROOT=%s\n" "${RUNDIR_ROOT}"
        printf "  TEST_NAME=%s\n" "${TEST_NAME}"
        printf "  TEST_ID=%s\n" "${TEST_ID}"
        printf "  COMPILE_ID=%s\n" "${COMPILE_ID}"

        if ./run_test.sh "${PATHRT}" "${RUNDIR_ROOT}" "${TEST_NAME}" "${TEST_ID}" "${COMPILE_ID}"; then
            printf "SUCCESS: TEST_NAME=%s COMPILE_ID=%s completed successfully\n" \
                "${TEST_NAME}" "${COMPILE_ID}"
        else
            rc=$?
            printf "WARNING: run_test.sh failed for TEST_NAME=%s COMPILE_ID=%s exit_code=%d\n" \
                "${TEST_NAME}" "${COMPILE_ID}" "${rc}" >&2
            printf "         Continuing to the next test.\n" >&2
            failed_tests+=( "${COMPILE_ID}:${TEST_NAME}:${rc}" )
            continue
        fi

    done

done

printf "\n=====================================================================\n"
printf "Finished running run_ufs_tests_from_envfile.sh\n"
printf "=====================================================================\n"

if [[ "${#skipped_tests[@]}" -gt 0 ]]; then
    printf "\nSkipped test groups:\n"
    for skipped in "${skipped_tests[@]}"; do
        IFS=':' read -r skipped_compile_id skipped_test_name skipped_reason <<< "${skipped}"
        printf "  COMPILE_ID=%s TEST_NAME=%s reason=%s\n" \
            "${skipped_compile_id}" "${skipped_test_name}" "${skipped_reason}"
    done
fi

if [[ "${#failed_tests[@]}" -gt 0 ]]; then
    printf "\nFailed tests:\n"
    for failed in "${failed_tests[@]}"; do
        IFS=':' read -r failed_compile_id failed_test_name failed_status <<< "${failed}"
        printf "  COMPILE_ID=%s TEST_NAME=%s exit_code=%s\n" \
            "${failed_compile_id}" "${failed_test_name}" "${failed_status}"
    done
    exit 1
fi

printf "\nAll attempted tests completed successfully.\n"
exit 0
