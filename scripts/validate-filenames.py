import argparse
from pathlib import Path

import requests

DATA_TYPES = {
    "application": "Applications",
    "climate": "Climate_Projections",
    "derived": "Derived_Datasets",
    "indicator": "Indicators",
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
    "completeness",
    "consistency",
    "extremes-detection",
    "resolution",
    "timeliness",
    "uncertainty-quality-flags",
    "validation",
    # Deprecated
    "climate-and-weather-extremes",
    "climate-impact-indicators",
    "climate-monitoring",
    "consistency-assessment",
    "data-completeness",
    "forecast-skill",
    "intercomparison",
    "mean",
    "model-performance",
    "trend-assessment",
    "uncertainty",
    "variability",
)

API_URL = "https://cds.climate.copernicus.eu/api/catalogue/v1/collections"


def main(paths: list[Path]) -> None:
    for path in paths:
        assert path.stem.islower(), f"{path=!s}: Invalid {path.name=}"
        segments = path.stem.split("_")
        assert len(segments) == 4, f"{path=!s}: Invalid {path.name=}"
        (
            data_type,
            collection_id,
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
        url = "/".join([API_URL, collection_id])
        try:
            requests.get(url).raise_for_status()
        except Exception as exc:
            raise RuntimeError(f"{path=!s}: Invalid {url=}") from exc

        # Check assessment category
        assert assessment_category in ASSESSMENT_CATEGORIES, (
            f"{path=!s}: Invalid {assessment_category=}"
        )

        # Check question number
        assert len(question_number) == 3, f"{path=!s}: Invalid {question_number=}"
        assert question_number[0] == "q", f"{path=!s}: Invalid {question_number=}"
        assert question_number[1:].isdigit(), f"{path=!s}: Invalid {question_number=}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", action="store", type=Path, nargs="*")
    args = parser.parse_args()
    main(args.paths)
