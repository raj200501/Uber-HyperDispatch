from __future__ import annotations

import re

import pytest

from hyperdispatch_sim import runner


def test_runner_main_smoke_steps(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["runner", "--seed", "123", "--scenario", "baseline_city", "--steps", "3"],
    )
    monkeypatch.setattr(runner.time, "sleep", lambda _seconds: None)

    runner.main()

    output = capsys.readouterr().out
    assert "seed=123 scenario=baseline_city" in output
    assert len(re.findall(r"request=req-", output)) == 3


def test_runner_invalid_args(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.argv", ["runner", "--scenario", "unknown_city"])

    with pytest.raises(SystemExit):
        runner.main()

    err = capsys.readouterr().err
    assert "invalid choice" in err
    assert "baseline_city" in err
