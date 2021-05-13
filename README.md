# CO2-decay-analysis

## Overview 

This set of Python modules can be used to identify periods when a dwelling is unoccupied and then identify and analyse periods of CO2 decay to use for ventilation rate analysis.

The csv files provided are example data from a monitoring campaign, the scripts can be set to analyse this data so you can see how the analysis works.

## Python scripts

The analysis is controlled from the RunAnalysis.py script. This loads the data, then analyses it using functions from the other modules as required, it finally produces a data frame giving the results of the measured ventilation rates (ach). The following steps are taken to go from data to ventilation rate results:

1. Load monitored data into a number of data frames
2. Find the unoccupied periods using functions from the occupancy status algorithm (OSA) script
3. Find periods of decaying CO2 in the unoccupied subset of data, using functiongs in the DecayAnalysis script. Certain requirements are made on the decay periods for them to be considered valid - including the minimum CO2 concentration allowed, minimum and maximum decay durations, spatial homogeneity of CO2 concentration if more than one measurement is available, etc.
4. Analyse the decay periods identified in step 3 using functions in the DecayAnalysis script.
5. Return a dataframe with the ventilation rate results

My environmental data was every 5 minutes, if yours is different you will need to adjust some sections of the OSA code, the decay identification code, and the conversion to ach.  

Through the code you can set special cases I've done this using the CaseStudy string, i.e. if CaseStudy == 'SpecialCase', do something different. else: do the normal thing. The other place that the CaseStudy string is used is in the LegendList script - this lets you set what the legend should show for each column when the data is plotted.

## Example data 

The code is set up to analyse example the day of data which I've also included - you shouldn't need to change anything except the paths to run the code for this data. You can then set your data to load instead and hopefully then nothing else should need to be changed too much for the analysis to run.
