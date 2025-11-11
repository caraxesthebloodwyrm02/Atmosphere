import sys
from typing import List

from atmosphere_audio.cli import main


def run_cli(args: List[str]) -> int:
	# simulate CLI entry
	return main(args)


def test_cli_version_flag():
	exit_code = run_cli(["--version"])
	assert exit_code == 0


def test_cli_help_runs():
	# no args should print usage and return 0
	exit_code = run_cli([])
	assert exit_code == 0


