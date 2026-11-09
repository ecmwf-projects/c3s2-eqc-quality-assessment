# Map the files changed by a pull request to its labels.
# Input: the slurped pages of GET /repos/{owner}/{repo}/pulls/{number}/files
# Repo-wide edits to notebooks usually come with tooling changes, so those count as maintenance only.
# Anything else (pages, images, deleted notebooks) is maintenance too, so every PR gets a type.
# A theme is added when all the notebooks a PR adds or changes are in one theme's folder.
def notebook: (.filename | endswith(".ipynb")) and (.filename | startswith("templates/") | not);
def tooling: .filename | test("^(\\.github|scripts|templates)/|^(Makefile|pyproject\\.toml|uv\\.lock|\\.pre-commit-config\\.yaml|_config\\.yml|_toc\\.yml|myst\\.yml|lychee\\.toml|\\.gitignore)$");
def theme: {
    "Applications": "theme: application",
    "Climate_Projections": "theme: climate projection",
    "Derived_Datasets": "theme: derived dataset",
    "In_Situ": "theme: in situ",
    "Indicators": "theme: climate indicator",
    "Reanalyses": "theme: reanalysis",
    "Satellite_ECVs": "theme: satellite",
    "Seasonal_Forecasts": "theme: seasonal forecast"
  }[.filename | split("/")[0]];

add
| any(.[]; tooling) as $tooling
| [.[] | select(notebook and .status != "removed")] as $notebooks
| [ (if any($notebooks[]; .status == "added") then "type: new notebook" else empty end),
    (if ($tooling | not) and any($notebooks[]; .status != "added") then "type: notebook update" else empty end),
    (if $tooling then "type: maintenance" else empty end) ]
| if length == 0 then ["type: maintenance"] else . end
| . + (if $tooling then [] else [$notebooks[] | theme] | unique | if length == 1 and .[0] != null then . else [] end end)
| .[]
