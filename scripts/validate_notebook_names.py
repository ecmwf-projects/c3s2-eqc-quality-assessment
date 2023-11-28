import argparse
import pathlib
import urllib.request
import uuid

DATA_TYPES = (
    "climate",
    "insitu",
    "reanalysis",
    "satellite",
    "seasonal",
)

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
    "trend-assessment",
    "uncertainty",
    "variability",
)

API_URL = "https://cds.climate.copernicus.eu/api/v2"


def main(directory: str):
    for path in pathlib.Path(directory).glob("**/*.ipynb"):
        assert path.stem.islower(), f"{path=!s}: Invalid {path.name=}"

        segments = path.stem.split("_")
        assert len(segments) == 5, f"{path=!s}: Invalid {path.name=}"
        (
            data_type,
            dataset_id,
            assessment_category,
            question_number,
            task_id,
        ) = segments

        assert data_type in DATA_TYPES, f"{path=!s}: Invalid {data_type=}"

        url = f"{API_URL}/resources/dataset/{dataset_id}"
        assert (
            urllib.request.urlopen(url).getcode() == 200
        ), f"{path=!s}: Invalid {dataset_id=}"

        assert (
            assessment_category in ASSESSMENT_CATEGORIES
        ), f"{path=!s}: Invalid {assessment_category=}."

        assert len(question_number) == 3, f"{path=!s}: Invalid {question_number=}"
        assert question_number[0] == "q", f"{path=!s}: Invalid {question_number=}"
        assert question_number[1:].isdigit(), f"{path=!s}: Invalid {question_number=}"

        try:
            uuid.UUID(task_id)
        except ValueError:
            raise ValueError(f"{path=!s}: Invalid {task_id=}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=str)
    args = parser.parse_args()
    main(args.directory)
