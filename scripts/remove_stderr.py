import argparse
from pathlib import Path

import nbformat


def is_stderr(output: nbformat.notebooknode.NotebookNode) -> bool:
    """Check if an output is an stderr."""
    return output.output_type == "stream" and output.name == "stderr"


def remove_stderr(notebook: nbformat.notebooknode.NotebookNode) -> None:
    """Go through all cells in a notebook and remove stderr outputs in-place."""
    for cell in notebook.cells:
        # Skip markdown cells
        if cell["cell_type"] != "code":
            continue

        # Remove stderr outputs
        cell.outputs = [output for output in cell.outputs if not is_stderr(output)]


def remove_stderr_file(path: Path | str) -> None:
    """Open a file, remove stderr outputs, overwrite original."""
    # Read file
    notebook = nbformat.read(path, nbformat.NO_CONVERT)

    # Remove stderrs
    remove_stderr(notebook)

    # Save file
    nbformat.write(notebook, path)


def main(paths: list[Path]) -> None:
    """Apply remove_stderr_file to all files."""
    for path in paths:
        remove_stderr_file(path)


# Execute
if __name__ == "__main__":
    # Get filenames
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()

    # Execute
    main(args.paths)
