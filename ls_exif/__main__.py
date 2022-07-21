# type: ignore[attr-defined]
from typing import Optional

import functools
import pathlib
from enum import Enum

import typer
from rich.console import Console

from ls_exif import version
from ls_exif.cli import print_tabular_listing, walk_directory


app = typer.Typer(
    name="ls-exif",
    help="An 'ls' companion displaying EXIF metadata columns",
    add_completion=False,
)
console = Console()


def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]ls_exif[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


@app.command(name="")
def main(
    path: str = typer.Argument(default=".", help="The directory to list (the current working directory by default)"),
    tabular: bool = typer.Option(False, help="Display as table (default: imitate ls)"),
    recursive: bool = typer.Option(False, help="Whether to descend into subdirectories recursively"),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the ls_exif package.",
    ),
) -> None:
    """TODO"""

    walk_directory(pathlib.Path(path), pathlib.Path(path), functools.partial(print_tabular_listing, console), recursive)


if __name__ == "__main__":
    app()
