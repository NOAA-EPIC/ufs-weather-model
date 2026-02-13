from dataclasses import dataclass
import os

@dataclass
class EnvConfig:
    pathrt: str = os.getenv("PATHRT", "")
    machine_id: str = os.getenv("MACHINE_ID", "")
    ufs_test_yaml: str = os.getenv("UFS_TEST_YAML", "")
    keep_rundir: str = os.getenv("KEEP_RUNDIR", "false")
    rocoto: str = os.getenv("ROCOTO", "false")
    create_baseline: str = os.getenv("CREATE_BASELINE", "false")
    compile_only: str = os.getenv("COMPILE_ONLY", "false")

    @property
    def regression_log(self) -> str:
        return f"{self.pathrt}/logs/RegressionTests_{self.machine_id}.log"

    @property
    def test_changes_list(self) -> str:
        return f"{self.pathrt}/test_changes.list"

