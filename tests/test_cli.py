"""CLI smoke tests for skill-lint."""

from click.testing import CliRunner

from skill_lint.cli import main


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.3.0" in result.output


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


def test_scan_single_claude_md(tmp_path):
    f = tmp_path / "CLAUDE.md"
    f.write_text("# Project\nSimple project context.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(f)])
    assert result.exit_code == 0
    assert "CLAUDE.md" in result.output


def test_scan_single_skill_md(tmp_path):
    d = tmp_path / "skills" / "foo"
    d.mkdir(parents=True)
    f = d / "SKILL.md"
    f.write_text("# Foo\nDo foo things.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(f)])
    assert result.exit_code == 0
    assert "SKILL.md" in result.output


def test_scan_single_file_json(tmp_path):
    f = tmp_path / "CLAUDE.md"
    f.write_text("# Project\nSimple.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(f), "--format", "json"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert isinstance(data, list)


def test_scan_gemini_md(tmp_path):
    f = tmp_path / "GEMINI.md"
    f.write_text("# Project\nGemini CLI instructions.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 0
    assert "GEMINI.md" in result.output


def test_rule_show_valid():
    runner = CliRunner()
    result = runner.invoke(main, ["rule", "TCOST001"])
    assert result.exit_code == 0
    assert "TCOST001" in result.output
    assert "token-cost" in result.output
    assert "warning" in result.output
    assert "Fix:" in result.output


def test_rule_show_invalid():
    runner = CliRunner()
    result = runner.invoke(main, ["rule", "FAKE999"])
    assert result.exit_code != 0
    assert "Unknown rule" in result.output


def test_rule_list_all():
    runner = CliRunner()
    result = runner.invoke(main, ["rule"])
    assert result.exit_code == 0
    assert "token-cost" in result.output
    assert "TCOST001" in result.output
    assert "CROSS001" in result.output


def test_rule_case_insensitive():
    runner = CliRunner()
    result = runner.invoke(main, ["rule", "tcost001"])
    assert result.exit_code == 0
    assert "TCOST001" in result.output


def test_explicit_scan_subcommand(tmp_path):
    skill = tmp_path / "CLAUDE.md"
    skill.write_text("# Project\nSimple.\n")
    runner = CliRunner()
    result = runner.invoke(main, ["scan", str(tmp_path)])
    assert result.exit_code == 0


def test_bare_command_defaults_scan(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0


def test_rules_dict_sync():
    import re
    from pathlib import Path

    from skill_lint.rules import RULES

    scanner_path = Path(__file__).parent.parent / "src" / "skill_lint" / "scanner.py"
    source = scanner_path.read_text()
    found_ids = set(re.findall(r'rule_id="([A-Z]+\d+)"', source))
    found_ids.discard("RULE_ERR")
    rules_ids = set(RULES.keys())
    assert rules_ids == found_ids, (
        f"RULES dict out of sync. Missing from RULES: {found_ids - rules_ids}. "
        f"Extra in RULES: {rules_ids - found_ids}"
    )


def test_include_from_yaml_config(tmp_path):
    d = tmp_path / "prompts"
    d.mkdir()
    (d / "system.md").write_text("# System\nSystem prompt instructions.\n")
    cfg = tmp_path / ".skill-lint.yaml"
    cfg.write_text("include:\n  - 'prompts/*.md'\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 0
    assert "system.md" in result.output


def test_include_cli_overrides_config(tmp_path):
    cfg_dir = tmp_path / "config_dir"
    cfg_dir.mkdir()
    (cfg_dir / "config.md").write_text("# Config\nFrom config.\n")
    cli_dir = tmp_path / "cli_dir"
    cli_dir.mkdir()
    (cli_dir / "cli.md").write_text("# CLI\nFrom CLI.\n")
    cfg = tmp_path / ".skill-lint.yaml"
    cfg.write_text("include:\n  - 'config_dir/*.md'\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--include", "cli_dir/*.md"])
    assert result.exit_code == 0
    assert "cli.md" in result.output
    assert "config.md" not in result.output


def test_fail_under_passes(tmp_path):
    f = tmp_path / "CLAUDE.md"
    f.write_text("# Project\nSimple project.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--fail-under", "50"])
    assert result.exit_code == 0


def test_fail_under_fails(tmp_path):
    f = tmp_path / "CLAUDE.md"
    content = "---\ndescription: " + "x" * 1200 + "\n---\n"
    content += "\n".join([f"line {i}" for i in range(100)])
    f.write_text(content)
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--fail-under", "95"])
    assert result.exit_code == 1


def test_fail_under_at_threshold_passes(tmp_path):
    f = tmp_path / "CLAUDE.md"
    f.write_text("# Project\nSimple project.\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--fail-under", "99"])
    assert result.exit_code == 0


def test_fail_under_and_fail_on_or(tmp_path):
    f = tmp_path / "CLAUDE.md"
    content = "---\ndescription: " + "x" * 1200 + "\n---\n"
    content += "\n".join([f"line {i}" for i in range(100)])
    f.write_text(content)
    runner = CliRunner()
    result = runner.invoke(main, [
        str(tmp_path), "--fail-on", "warning", "--fail-under", "50",
    ])
    assert result.exit_code == 1


def test_fail_under_from_config(tmp_path):
    f = tmp_path / "CLAUDE.md"
    content = "---\ndescription: " + "x" * 1200 + "\n---\n"
    content += "\n".join([f"line {i}" for i in range(100)])
    f.write_text(content)
    cfg = tmp_path / ".skill-lint.yaml"
    cfg.write_text("fail_under: 95\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 1


def test_fix_message_shows_rule_link(tmp_path):
    f = tmp_path / "CLAUDE.md"
    content = "\n".join([f"instruction line {i}" for i in range(55)])
    f.write_text(content)
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "-v"])
    assert "Run: skill-lint rule" in result.output


def test_exclude_from_config(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# Project\nInstructions.\n")
    (tmp_path / "AGENTS.md").write_text("# Agents\nAgent rules.\n")
    cfg = tmp_path / ".skill-lint.yaml"
    cfg.write_text('exclude:\n  - "CLAUDE.md"\n')
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 0
    assert "AGENTS.md" in result.output
    assert "CLAUDE.md" not in result.output or "No skill" in result.output
