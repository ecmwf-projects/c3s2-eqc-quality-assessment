Introduction

ERA5-Drought is a global reconstruction of two standardised drought indices from 1940 to present. The dataset comprises of both:

```
• the Standardised Precipitation Index (SPI).
• the Standardised Precipitation-Evaporation Index (SPEI).
```

Both indices are widely-employed in meteorology, and operate on the same principle, namely quantifying the amount of precipitation and potential evapotranspiration over a given time frame at a given location relative to its historical climatology. In ERA5-Drought, SPI and SPEI are calculated using precipitation and potential evapotranspiration from the fifth generation of the ECMWF atmospheric reanalyses (ERA5). Both drought indices are calculated for a range of accumulation windows (1/3/6/12/24/36/48 months) using the reference period (1991-2020). Data in ERA5-Drought is interpolated and regridded to a 0.25° × 0.25°, making it suitable for common applications.

The dataset includes ERA5's deterministic reanalysis as well as 10 propagated members of the ERA5-EDA ensemble, enabling uncertainty assessment of drought occurrence and intensity. Furthermore, dataset provides multiple quality flags of the derived indices such as a test of normality via. Shapiro-Wilks significance testing, that allow users to filter data.

Key strengths

```
• Coverage: ERA5-Drought provides a consistent decades long (1940-) time series with global coverage. This enables meteorological studies in locations with limited or no support by other datasets, particularly with local validation data such as in-situ measurements (weather stations, rain-gauge data). The temporal coverage enables long-term climatological comparisons and correlation with historical meteorological trends. However, it is important to note the limitations and uncertainties in the underpinning ERA5 data, which also vary over space and time (Hersbach et al., 2020).

• Timescale: the ERA5-Drought dataset provides analysis-ready drought indices evaluated for short-term and long-term accumulation windows. These are useful for probing short-term and long-term drought impact on the environment, from soil moisture and flow in small creeks, to groundwater recharge and reservoir storage, respectively [reference needed].

• Uncertainty: whilst the dataset does not provide an uncertainty on its data that is ready for download by the user, a proxy for the uncertainty on the drought-indices may be readily calculated with the download of the 10-member ensemble for each drought index, for each accumulation window, globally. This relative, "synoptic" uncertainty provides an estimate of the uncertainty that takes into account the uncertainty in the underlying forecast model (used to propagate the analysis state between assimilation cycles) and in the assimilated observations. It is important to note however that uncertainty estimates may be slightly underestimated due to the ensemble spready not fully including systematic effects.

• Quality control: this is performed on both the input data (ERA5) and the derived dataset (ERA5-Drought). The quality on the derived dataset is assessed by testing if the distribution of the estimated drought index over the reference period follows a normal distribution with mean 0 and standard deviation 1 using the Shapiro-Wilks test for normality, with a p-value of 0.05. This is done for both drought indices and every calendar month, within the reference period (1991-2020) and is available for download by users to filter data. Quality control on input data is provided only for SPI, with the probability of zero precipitation "pzero" available for download per calendar month, calculated within the reference period. This allows users to set reasonable thresholds (e.g. use site only if 10 months or fewer are with zero precipitation, < 0.33), and use indices in regions with less than 30 months of precipitation larger than zero.

• Tailoredness: the ERA5-Drought dataset contains the two most important drought indices for drought studies in a single analysis-ready dataset. Indices are provided for temporal accumulation windows most appropriate and used. This relieves users of the burden of processing underpinning datasets themselves.

• Spatial resolution: the  0.25° by 0.25° spatial grid for ERA5-Drought makes the dataset suitable for studies on spatial scales from global to local. The gridding is finer than comparable datasets such as the Copernicus Global Drought Observatory (GDO)[(https://drought.emergency.copernicus.eu/tumbo/gdo/download)] and CSIC [[Franch-Pardo+25](https://doi.org/10.48088/ejg.i.fra.16.2.286.297)] and the Spanish National Research Council (CSIC)[(https://spei.csic.es/)]. Regridding is only required for the ensemble dataset, as the ensemble dataset for ERA5 is on a coarser 0.5° by 0.5° spatial grid.
```

Key limitations

```
• Timeliness: the "consolidated" dataset is updated 2-3 months behind real time while the "intermediate" dataset is update with 1 month of delay. Whilst this is sufficient for many use cases such as historical anaylsis of crop yields, it is too long for (near-) real time uses cases such as early warning drought systems that require updates every few days.
        
• Validation: comparible datasets are at coarser resolutions than ERA5-Drought (i.e. at 1° and 0.5°, while ERA5-Drought is available at 0.25°), so only a qualatitive validation was performed to ensure the dataset was free from "clerical errors". Since other datasets use other input data, make other assumptions and use other reference periods, a fair comparison differences may arise from these factors when estimating drought indices. The ERA5-Drought dataset has however been validated against the underlying dataset (ERA5), ensuring the indices themselves are reproducible (can we reference the reproducibility notebook here?).

• Early reanalysis data: the scarcity of observational data pre-satellite era before 1980 leads to increased uncertainy in the reanalysis outputs (https://doi.org/10.1002/qj.4174). Furthermore, data prior to 1960 may be more strongly influenced by intial conditions used in the reanalysis model, therefore users should interpret early renalysis data (1940-1980) with caution.

• Exreme precipitation events: a validation study  of the underlying ERA5 precipitation dataset that compared against in-situ observations across Europe found extreme precipitation events tend to underestimated [(21. Lavers, D. A., Simmons, A., Vamborg, F. & Rodwell, M. J. An evaluation of era5 precipitation for climate monitoring. Quarterly Journal of the Royal Meteorological Society 148, 3152–3165 (2022).)]. This is likely to translate to extreme wet events categorised by the drought indices to be underestimated.
```

Example applications

```
• Drought identification & monitoring: the SPI and SPEI indices have been extensively used to identify and capture major droughts across the globe (https://doi.org/10.1038/sdata.2014.1)(https://doi.org/10.1016/j.pce.2018.07.001)(https://doi.org/10.1175/2010JHM1307.1), with the WMO recommending the SPI as the main meteorological drought index that countries should use to monitor and follow drought conditions (Hayes, 2011)(https://digitalcommons.unl.edu/droughtfacpub/94/). The inclusion of temperature along with precipitation data allows for SPEI to be applicable for all climate regimes, and looking at the impact of climate change in model output under future scenarios.

• Crop yield modelling: early crop prediction from combined use of satellite observational data such as the Normalized Difference Vegetation Index (NDVI) has allowed the prediction of wheat and barley production in February, four months before harvest (Vicente‐Serrano et al., ‘Early Prediction of Crop Production Using Drought Indices at Different Time‐scales and Remote Sensing Data’.). This is useful for managing crop production, along with early prediction of crop losses.

• Tree-ring width series: 

• Streamflow data: 

• Parametric insurance:
```

Further considerations

```
•  Distribution parameters:

•  Batch quality flag download: mutliple accumulation windows in a single CDS request may be specified, but only the final accumulation window is downloaded for the quality flags such as "pzero" and the "significance" datas. Users of these quality flags must specify separate CDS requests per accumulation window, which is not instructed, and may prove to be an obstacle for filtering data. 

• Improper ensemble formatting: only for ensemble dataset. Perhaps also mention variable names? And longitude coords not following usual convention.
```
