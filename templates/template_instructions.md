![logo](../LogoLine_horizon_C3S.png)

# Template instructions

```{note}
If anything is unclear with the templates, or if you encounter any problems, please report them at [GH164](https://github.com/ecmwf-projects/c3s2-eqc-quality-assessment/issues/164).
```

Instructions for the [Jupyter Notebook template for quality assessments](./template.ipynb). This template aims to ensure consistency in content and the look and feel of the assessment once it is included in the [Jupyter Book](https://ecmwf-projects.github.io/c3s2-eqc-quality-assessment/intro.html). The syntax includes MyST formatting needed for the Jupyter Book which will not render in all Jupyter Notebook viewers, or GitHub, but works in Jupyter Lab on the Virtual Machine.

```{note}
Some additional formatting required for the Jupyter Book will be automatically applied when the page for a given assessment is built, and so are not included in the template. This includes the extraction of embedded images, 'collapsing' the code cells, and adding a logo line.
```

```{note}
Please follow the headings and subheadings approach used in the template. The level of the heading is determined by the number of hashes before it (#Title, ##Use case, etc.). The following link should be helpful: https://jupyterbook.org/en/stable/reference/cheatsheet.html

Also note that icons have been added to most of the headings. These are standardised so should be the same for each assessment.
```

```{note}
**References in the text should be made in the format`[[1]](https://doi.org/10.1038/s41598-018-20628-2))`, using a doi link wherever possible. The links are checked when the book is built, and broken links will cause an error to be raised.**
```

## Assessment title (no icons)

We do not aim to be completely prescriptive about the title, it should be readable and descriptive, but also include some keywords to increase searchability, e.g. *Seasonal forecasts bias assessment for impact models*.

It could include:

- **Data stream/ECV/variable/index**: Satellite (observations), Insitu (observations), Reanalysis, Seasonal (Forecasts), Climate (projections)
- **Quality area**: bias, forecast skill, completeness, intercomparison of X and Y, comparison to X, trend assessment, extremes, spatial/temporal resolution, reliability, accuracy, etc.
- **Application area**: impact models, risk assessment, climate monitoring, scientific study of X, Y sector, 'region', 'specific C3S application', flood forecasting, etc.

```{note}
The title will be used in the table of contents for the data stream and the side bar of the Jupyter Book, so it needs to be unique, not too long, and help guide users to the assessment by mentioning the key analysis or outcomes. It will also be the title shown in the quality tab on the CDS.
```

```{note}
The title should be the only 'level one' heading (single # before the heading), otherwise the other headings will also appear as separate links in the table of contents for the data stream and sidebar.
```

## Production date and author

Include a production date (approximating when the data was downloaded and code first run, or document first accessed). Optionally, the author(s) can be acknowledge, by name and/or institute, or instead 'EQC evaluator'.

## 🌍 Use case

The use case is listed directly in the heading of the section: `## Use case: ...`

## ❓ User question

User question, or User questions, if more than one question is answered in the assessment, or if a second question helps clarify the aim of the assessment. The question or questions are bold and highlighted with bullet points.

## Context text (no heading or icon)

A section of text with no heading which appears after the user question and before the quality assessment statement. References can be used to link to examples of relevant literature or example applications relevant to the use case and user question. It should be as short as possible, but contain enough information for users to understand the context of the assessment and the main approach to be used. Together with the assessment title, use case and user question, and assessment statement all key information should be contained at the top of the assessment.

## 📢 Quality assessment statement

Key results and guidance including an answer to the user question, as a bulleted list.

```{note}
The blue notification box that contains the quality assessment statement bullet points will not appear in GitHub, but will be rendered when the Jupyter Book page is created.
```

## Figure (no heading or icon)

A key figure should be included if possible, acting as a 'graphical abstract' for the assessment. This could be a figure generated later in the code, or from an external source (if licensing allows reproduction) - in this case the source should be cited in the caption. Images should be dragged and dropped into the markdown cell, which creates an 'attachment code', and the external file is not needed.

Drag and drop the image from a file browser into the cell. If the image file already includes a figure number and the caption then the simple default syntax can be used to add the figure (`![](attachment:... ID from drag and drop)`). Otherwise, figure formatting can be used (see the template), where the attachment code from the drag and drop needs to be wrapped in the figure syntax. This approach should also be followed if images not generated by code are included later in the assessment.

The figure should always include an explanatory caption and/or title.

```{note}
The figure formatting will not render in Github, but will work when the Jupyter Book page is built. Also note that the figure numbering is automatic, and applied across the whole Book (each Notebook does not start at 1 - this may be changed in the future). 
```

## 📋 Methodology

Some text to introduce the methodology, including relevant sources, followed by a numbered list of the analysis steps under the 'analysis and results' section. The headings of each list item should link to the sections within 'Analysis and results' - this needs to be done manually. Extra steps or explanations can be added in the bullets between each numbered item.

The syntax for the link in the methodology list is: `[](section-1)`, where no text in the square brackets is needed (the heading of the corresponding section in 'Analysis and Results' will be shown automatically), and the label in the circle brackets is the manually set label used later to identify the section in question like

```md
(section-1)=
### 1. Section 1 title
```

## 📈 Analysis and results

A series of subsections with the same titles as in the listen in the methodology. In turn, these can have their own subsections. Code cells will be collapsed when the Jupyter Book is built. The final results should be clearly presented and discussed, supporting (but not repeating), the quality assessment statement.

## ℹ️ If you want to know more

Including a key resources subsection, which can link to suggested further reading, code packages used, and the relevant CDS catalogue entries. Try to link to relevant applications of the data, such as the C3S Climate Atlas, for projections, or the relevant parts of the European State of the Climate report for some ECVs.

Including a references subsection, which is a numbered list of the references used throughout the text. However, the references in the text should link to the external source, rather than the references list at the bottom of the assessment.
