# c3s2-eqc-quality-assessment

> [!WARNING]
> Please note that this repository is used for development and review, so quality assessments should be considered work in progress until they are merged into the main branch

> [!NOTE]
> If anything is unclear with the templates, or if you encounter any problems, please report them at [GH164](https://github.com/ecmwf-projects/c3s2-eqc-quality-assessment/issues/164).

## Quick start

To run the quality assurance checks:

```bash
pip install pre-commit
make qa
```

To build the book:

```bash
pip install -r requirements.txt
make build-book
```

## Naming convention

`{data-type}_{dataset-id}_{assessment-category}_q{question-number}.ipynb`

Data types:

- climate
- insitu
- reanalysis
- satellite
- seasonal

Assessment categories:

- completeness
- consistency
- extremes-detection
- resolution
- timeliness
- uncertainty-quality-flags
- validation

## License

```
Copyright 2023, European Union.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
