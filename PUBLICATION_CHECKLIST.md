# Publication Checklist

Before publishing this project, verify the following:

- Raw experimental data is not present in the working tree.
- Video files are not present in the working tree.
- IDE settings are not present in the working tree.
- Python cache files are not present in the working tree.
- Generated analysis outputs are not present in the working tree.
- Local absolute paths are not present in source files.
- `README.md` explains how to install and run the project.
- `requirements.txt` contains all runtime dependencies.
- `examples/` contains only synthetic data.
- `templates/` contains only schemas and placeholder data.

## Important Git History Note

If raw data or personal information was committed in earlier commits, do not publish the existing repository history as-is.

Recommended safe options:

1. Create a fresh public repository and copy only the cleaned working tree into it.
2. Create an orphan publication branch with no previous history.
3. Rewrite history with a dedicated cleanup tool, then verify that removed files are no longer reachable.

For the safest publication path, use a fresh repository or an orphan branch.
