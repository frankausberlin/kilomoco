import kilomoco.cli as cli
import sys

def test_cli_list_profiles(capsys):
    rc = cli.main(["--list"])
    captured = capsys.readouterr()
    assert "lopr" in captured.out
    assert "Low-Price (Economy)" in captured.out
    assert rc == 0