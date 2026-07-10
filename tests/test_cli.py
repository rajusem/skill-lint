"""CLI smoke tests for skill-lint."""

from click.testing import CliRunner

from skill_lint.cli import main


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "skill-lint" in result.output.lower() or "linter" in result.output.lower()


def test_scan_current_dir(tmp_path):
    runner = CliRunner()
    skill = tmp_path / "CLAUDE.md"
    skill.write_text("# Project\nSimple project context.\n")
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 0


def test_scan_nonexistent_path():
    runner = CliRunner()
    result = runner.invoke(main, ["/nonexistent/path"])
    assert result.exit_code == 2
    assert "not found" in result.output.lower()


def test_scan_empty_dir(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 0
    assert "No skill" in result.output


def test_severity_validation():
    runner = CliRunner()
    result = runner.invoke(main, [".", "--severity", "garbage"])
    assert result.exit_code != 0


def test_fail_on_warning(tmp_path):
    skill = tmp_path / "CLAUDE.md"
    skill.write_text("# Project\nSimple.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--fail-on", "warning"])
    assert result.exit_code == 0  # no warnings in simple file


def test_sarif_output(tmp_path):
    skill = tmp_path / "CLAUDE.md"
    skill.write_text("# Project\nSimple.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--format", "sarif"])
    assert result.exit_code == 0
    assert '"$schema"' in result.output


def test_json_output(tmp_path):
    skill = tmp_path / "CLAUDE.md"
    skill.write_text("# Project\nSimple.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--format", "json"])
    assert result.exit_code == 0


def test_verbose_flag(tmp_path):
    skill = tmp_path / "CLAUDE.md"
    skill.write_text("# Project\nSimple.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "-v"])
    assert result.exit_code == 0


def test_disable_rule(tmp_path):
    skill = tmp_path / "CLAUDE.md"
    skill.write_text("# Project\nSimple.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--disable", "TCOST003"])
    assert result.exit_code == 0


def test_report_mode(tmp_path):
    skill = tmp_path / "CLAUDE.md"
    skill.write_text("# Project\nSimple.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--report"])
    assert result.exit_code == 0


def test_nested_skill_discovery(tmp_path):
    d = tmp_path / "plugins" / "my-plugin" / "skills" / "review"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("# Review\nReview code changes.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 0
    assert "SKILL.md" in result.output
