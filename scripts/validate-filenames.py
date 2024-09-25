import argparse
import urllib.request
from pathlib import Path

DATA_TYPES = {
    "climate": "Climate_Projections",
    "insitu": "In_Situ",
    "reanalysis": "Reanalyses",
    "satellite": "Satellite_ECVs",
    "seasonal": "Seasonal_Forecasts",
}

SUBFOLDERS = {
    "climate": ("CMIP6", "CORDEX"),
    "satellite": (
        "Atmosphere_Physics",
        "Atmospheric_Composition",
        "Cryosphere",
        "Land_Biosphere",
        "Land_Hydrology",
        "Ocean",
    ),
}

ASSESSMENT_CATEGORIES = (
    "climate-and-weather-extremes",
    "climate-impact-indicators",
    "climate-monitoring",
    "consistency-assessment",
    "data-completeness",
    "forecast-skill",
    "intercomparison",
    "mean",
    "model-performance",
    "resolution",
    "timeliness",
    "trend-assessment",
    "uncertainty",
    "validation",
    "variability",
)

API_URL = "https://cds.climate.copernicus.eu/api/v2"


def main(paths: list[Path]) -> None:
    for path in paths:
        assert path.stem.islower(), f"{path=!s}: Invalid {path.name=}"
        segments = path.stem.split("_")
        assert len(segments) == 4, f"{path=!s}: Invalid {path.name=}"
        (
            data_type,
            dataset_id,
            assessment_category,
            question_number,
        ) = segments

        # Check data type
        assert data_type in DATA_TYPES, f"{path=!s}: Invalid {data_type=}"
        if subfolders := SUBFOLDERS.get(data_type):
            assert path.parts[-2] in subfolders, f"{path=!s}: Invalid {subfolders=}"
        folder = DATA_TYPES[data_type]
        folder_index = -3 if subfolders else -2
        assert folder in path.parts[folder_index], f"{path=!s}: Invalid {folder=}"

        # Check dataset ID
        url = f"{API_URL}/resources/dataset/{dataset_id}"
        assert (
            urllib.request.urlopen(url).getcode() == 200
        ), f"{path=!s}: Invalid {dataset_id=}"

        # Check assessment category
        assert (
            assessment_category in ASSESSMENT_CATEGORIES
        ), f"{path=!s}: Invalid {assessment_category=}"

        # Check question number
        assert len(question_number) == 3, f"{path=!s}: Invalid {question_number=}"
        assert question_number[0] == "q", f"{path=!s}: Invalid {question_number=}"
        assert question_number[1:].isdigit(), f"{path=!s}: Invalid {question_number=}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
