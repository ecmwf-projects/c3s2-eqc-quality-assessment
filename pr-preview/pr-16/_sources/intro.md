![logo](LogoLine_horizon_C3S.png)

# C3S EQC quality assessments 

This Jupyter Book contains a collection of quality assessments of C3S data produced by external evaluators under the C3S2_520 contract, which provides an **evaluation and quality control (EQC)** function for selected datasets on the climate data store (CDS).

C3S has established an EQC framework for all its products and services to ensure that users are served well and that this will continue to be the case as their needs evolve. The main goal of the EQC for CDS datasets function is to develop precise statements about data quality that pertain to well-identified use cases. Those statements, in combination with other documented information about the datasets, constitute a knowledge base that can help users to assess fitness for purpose, given their needs and requirements. 

## Layers of evaluation and quality control

The revised EQC framework makes a distinction between quality assurance, quality assessment and fitness for purpose. 

::::{grid}
:gutter: 3

:::{grid-item-card} ✅ Quality assurance
data quality checks against key requirements
:::

:::{grid-item-card} 🧭 Quality assessments
scientific assessments which answer user questions
:::

:::{grid-item-card} 🏆 Fitness for purpose
deciding whether data is suitable for a particular use
:::
::::

In more detail, **Quality assurance** serves to inform users that data, metadata and documentation comply with a well-defined set of verifiable technical requirements. It provides evidence that this compliance has been checked independently from the producers. Quality assurance for each CDS dataset is implemented by verifying a set of well-defined technical requirements associated with the dataset. Specific assessment criteria for the respective data streams (e.g. reanalysis, projections) are developed to account for the different nature of these and the different types of checks that may have to be applied to verify the requirement. The role of EQC evaluators is to check these criteria and document the outcome to users. 

The purpose of **quality assessments**, on the other hand, is to provide science-based information about accuracy, uncertainties, sources of uncertainty, temporal consistency, strengths, and weaknesses of a dataset in the context of a realistic use cases. 

EQC evaluators are tasked with developing quality assessments that are designed to generate useful statements about fitness for purpose of CDS datasets. The assessments address concrete questions about data quality associated with real use cases. Many of the assessments are implemented in Jupyter notebooks that can be shared, re-used, and modified by users. Assessments can involve multiple CDS datasets and use other sources of reference data. Assessments must build on relevant scientific literature, including published documents developed by producers and users of the datasets.

Taken together, the outcomes of these activities provide the key information needed to determine **fitness for purpose**. This information supports users in determining whether the data is fit for their specific application.  

## Quality assessments

Each quality assessment is comprised of

- **Use Case**: Description of an application of a user from the user perspective. 

- **User Question**: Question from a user regarding quality attributes of a dataset in the context of their application.  

- **Quality Assessment**: Scientific evaluation of quality-related user questions including guidance on suitability for a specific use (“How, and how well can I use the data for my purpose?”, “Is the dataset adequate to address my problem?”, “What is the most suitable C3S dataset to tackle my problem?”) 


These assessments are organised by the type of data they address. Note that while each assessment focusses on addressing the quality of a particular dataset, it may rely on other types of data as well (e.g. reanalysis for bias assessment).


1. [Satellite observations](Satellite_ECVs/satellite.md)
2. [Insitu observations](In_Situ/insitu.md)
3. [Reanalysis](Reanalyses/reanalysis.md)
4. [Seasonal forecasts](Seasonal_Forecasts/seasonal.md)
5. [Climate projections](Climate_Projections/climate.md)

## Running the Notebooks

Most of these quality assessments include Python code to produce data and figures which help answer the user question. This code is included primarily for transparency and traceability, as the software was designed to support evaluators running the assessments on EQC infrastructure, rather than to be easily reproducable. However, sections of it may also be directly applicable to your application and can be adapted or adjusted to your needs.

Most code in the Notebooks is self contained (but does make use of the [custom software](https://github.com/bopen/c3s-eqc-automatic-quality-control/tree/main/c3s_eqc_automatic_quality_control) prepared by [BOpen](https://www.bopen.eu/) for EQC evaluators). Some quality assessments may rely on the outcomes and code of previous assessments, or offline computations.

Some of the analysis in the quality assessments is not compute or data intensive, and so the Notebooks (.ipynb files) can be downloaded, adapted, and run on freely available cloud platforms, or on your own computing resources.
