import os
from pathlib import Path
from typing import Generator

import pytest
from typer.testing import CliRunner

from advent_of_code import app, extract_parts, rot13_decode, rot13_encode

runner = CliRunner()


@pytest.fixture
def temp_puzzle_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create temporary puzzle directory."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_cwd)


def test_rot13_encode_decode() -> None:
    """Test ROT13 encoding and decoding."""
    text = "Hello, World!"
    encoded = rot13_encode(text)
    assert encoded != text
    decoded = rot13_decode(encoded)
    assert decoded == text


def test_extract_parts_part1_only() -> None:
    """Test extracting only part 1 from HTML."""
    html = """
    <article>
        <h2>--- Day 1: Test ---</h2>
        <p>Part 1 content</p>
    </article>
    """
    part1, part2 = extract_parts(html)
    assert "Part 1 content" in part1
    assert part2 is None


def test_extract_parts_both_parts() -> None:
    """Test extracting both parts from HTML."""
    html = """
    <article>
        <h2>--- Day 1: Test ---</h2>
        <p>Part 1 content</p>
        <h2>--- Part Two ---</h2>
        <p>Part 2 content</p>
    </article>
    """
    part1, part2 = extract_parts(html)
    assert "Part 1 content" in part1
    assert "Part 2 content" in part2


def test_download_command_no_session(temp_puzzle_dir: Path) -> None:
    """Test download command fails without session."""
    result = runner.invoke(app, ["download", "2023", "1"])
    assert result.exit_code == 2
    assert "AOC_SESSION environment variable not set" in result.stdout


def test_read_command_missing_file(temp_puzzle_dir: Path) -> None:
    """Test read command fails with missing file."""
    result = runner.invoke(app, ["read", "2023", "1", "1"])
    assert result.exit_code != 0
    assert "Question file not found" in result.stdout


def test_submit_command_missing_answer(temp_puzzle_dir: Path) -> None:
    """Test submit command fails with missing answer file."""
    result = runner.invoke(app, ["submit", "2023", "1", "1"])
    assert result.exit_code != 0
    assert "Answer file not found" in result.stdout


def test_update_results_command_no_puzzles(temp_puzzle_dir: Path) -> None:
    """Test update-results command fails with no puzzles."""
    result = runner.invoke(app, ["update-results", "2023"])
    assert result.exit_code != 0
    assert "No puzzles found for year 2023" in result.stdout


def test_update_results_command_creates_table(temp_puzzle_dir: Path) -> None:
    """Test update-results command creates results table."""
    # Create puzzle directory with some results
    puzzle_dir = temp_puzzle_dir / "puzzles" / "year_2023" / "day_01"
    puzzle_dir.mkdir(parents=True)

    # Create answer and result files
    (puzzle_dir / "answer_part1.txt").write_text("42")
    (puzzle_dir / "result_part1.md").write_text("That's the right answer!")

    result = runner.invoke(app, ["update-results", "2023"])
    assert result.exit_code == 0

    # Check README.md was created with table
    readme = Path("README.md").read_text()
    assert "| Day | Part 1 | Part 2 |" in readme
    assert "|  1  | ✅" in readme
