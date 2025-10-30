import kilomoco.cli as cli
import sys

def test_cli_list_profiles(capsys):
    rc = cli.main(["--list"])
    captured = capsys.readouterr()
    assert "Default" in captured.out
    assert rc == 0