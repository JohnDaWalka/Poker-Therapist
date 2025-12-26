import codecs
import os
import re
from pathlib import Path
from typing import Annotated, Optional

import httpx
import typer
from bs4 import BeautifulSoup
from markdownify import markdownify as md

app = typer.Typer()


def get_session() -> str:
    """Get AOC session from environment variable."""
    session = os.getenv("AOC_SESSION")
    if not session:
        raise typer.BadParameter("AOC_SESSION environment variable not set")
    return session


def get_headers(session: str) -> dict[str, str]:
    """Get request headers with session cookie."""
    return {
        "Cookie": f"session={session}",
        "User-Agent": "github.com/sourcery-ai/autonomous-advent-of-code",
    }


def rot13_encode(text: str) -> str:
    """ROT13 encode text."""
    return codecs.encode(text, "rot13")


def rot13_decode(text: str) -> str:
    """ROT13 decode text."""
    return codecs.decode(text, "rot13")


def ensure_puzzle_dir(year: int, day: int) -> Path:
    """Ensure puzzle directory exists and return path."""
    puzzle_dir = Path(f"puzzles/year_{year}/day_{day:02d}")
    puzzle_dir.mkdir(parents=True, exist_ok=True)
    return puzzle_dir


def extract_parts(html: str) -> tuple[str, Optional[str]]:
    """Extract puzzle parts from HTML content."""
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article")
    if not article:
        raise typer.BadParameter("Could not find puzzle content")

    # Convert to markdown and split on "--- Part Two ---"
    markdown = md(str(article))
    parts = markdown.split("--- Part Two ---")

    part1 = parts[0].strip()
    part2 = parts[1].strip() if len(parts) > 1 else None

    return part1, part2


@app.command()
def download(
    year: Annotated[int, typer.Argument(help="Year of puzzle")],
    day: Annotated[int, typer.Argument(help="Day of puzzle")],
) -> None:
    """Download puzzle content and input."""
    session = get_session()
    headers = get_headers(session)

    # Fetch puzzle content
    url = f"https://adventofcode.com/{year}/day/{day}"
    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.raise_for_status()

    # Extract parts
    part1, part2 = extract_parts(response.text)

    # Create puzzle directory
    puzzle_dir = ensure_puzzle_dir(year, day)

    # Save part 1
    part1_path = puzzle_dir / "question_part1_rot13.md"
    part1_path.write_text(rot13_encode(part1))

    # Save part 2 if it exists
    if part2:
        part2_path = puzzle_dir / "question_part2_rot13.md"
        combined = f"{part1}\n\n--- Part Two ---\n\n{part2}"
        part2_path.write_text(rot13_encode(combined))

    # Fetch and save input
    input_url = f"{url}/input"
    input_response = httpx.get(input_url, headers=headers, follow_redirects=True)
    input_response.raise_for_status()

    input_path = puzzle_dir / "input.txt"
    input_path.write_text(input_response.text)

    print(2 if part2 else 1)


@app.command()
def read(
    year: Annotated[int, typer.Argument(help="Year of puzzle")],
    day: Annotated[int, typer.Argument(help="Day of puzzle")],
    part: Annotated[int, typer.Argument(help="Part number (1 or 2)")],
) -> None:
    """Read puzzle content."""
    puzzle_dir = ensure_puzzle_dir(year, day)
    question_path = puzzle_dir / f"question_part{part}_rot13.md"

    if not question_path.exists():
        raise typer.BadParameter(f"Question file not found: {question_path}")

    encoded_content = question_path.read_text()
    decoded_content = rot13_decode(encoded_content)
    print(decoded_content)


@app.command()
def submit(
    year: Annotated[int, typer.Argument(help="Year of puzzle")],
    day: Annotated[int, typer.Argument(help="Day of puzzle")],
    part: Annotated[int, typer.Argument(help="Part number (1 or 2)")],
) -> int:
    """Submit answer for puzzle."""
    puzzle_dir = ensure_puzzle_dir(year, day)
    answer_path = puzzle_dir / f"answer_part{part}.txt"

    if not answer_path.exists():
        raise typer.BadParameter(f"Answer file not found: {answer_path}")

    session = get_session()
    headers = get_headers(session)

    answer = answer_path.read_text().strip()

    # Submit answer
    url = f"https://adventofcode.com/{year}/day/{day}/answer"
    data = {"level": str(part), "answer": answer}
    response = httpx.post(url, headers=headers, data=data, follow_redirects=True)
    response.raise_for_status()

    # Extract response content
    soup = BeautifulSoup(response.text, "html.parser")
    article = soup.find("article")
    if not article:
        raise typer.BadParameter("Could not find response content")

    result_markdown = md(str(article))

    # Save response
    result_path = puzzle_dir / f"result_part{part}.md"
    result_path.write_text(result_markdown)

    # Print response
    print(result_markdown)

    return 0 if "That's the right answer" in result_markdown else 1


@app.command()
def update_results(
    year: Annotated[int, typer.Argument(help="Year of puzzle")],
) -> None:
    """Update results table in README."""
    results: dict[int, dict[int, str]] = {}
    puzzles_dir = Path(f"puzzles/year_{year}")

    if not puzzles_dir.exists():
        raise typer.BadParameter(f"No puzzles found for year {year}")

    # Collect results for each day
    for day_dir in sorted(puzzles_dir.glob("day_*")):
        day = int(day_dir.name.replace("day_", ""))
        results[day] = {1: "NOT_SUBMITTED", 2: "NOT_SUBMITTED"}

        for part in [1, 2]:
            answer_file = day_dir / f"answer_part{part}.txt"
            result_file = day_dir / f"result_part{part}.md"

            if answer_file.exists() and result_file.exists():
                result_content = result_file.read_text()
                if "That's the right answer" in result_content:
                    results[day][part] = "CORRECT"
                else:
                    results[day][part] = "INCORRECT"

    # Generate results table
    table_lines = [
        "| Day | Part 1 | Part 2 |",
        "|-----|--------|--------|",
    ]

    max_day = max(results.keys())
    for day in range(1, max_day + 1):
        day_results = results.get(day, {1: "NOT_SUBMITTED", 2: "NOT_SUBMITTED"})
        symbols = {
            "NOT_SUBMITTED": "",
            "INCORRECT": "❌",
            "CORRECT": "✅",
        }
        table_lines.append(
            f"| {day:2d}  | {symbols[day_results[1]]:8} | {symbols[day_results[2]]:8} |"
        )

    table = "\n".join(table_lines)

    # Update README.md
    readme_path = Path("README.md")
    if not readme_path.exists():
        readme_path.write_text("")

    content = readme_path.read_text()
    pattern = f"<!-- begin-results: {year} -->.*?<!-- end-results: {year} -->"
    replacement = f"<!-- begin-results: {year} -->\n{table}\n<!-- end-results: {year} -->"

    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        new_content = f"{content}\n\n{replacement}\n"

    readme_path.write_text(new_content)


if __name__ == "__main__":
    app()
