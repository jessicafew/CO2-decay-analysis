'''This script loads data files for analysis using the CO2 decay technique to measure ventilation rate.
Required input files:
    Data1 is a csv of monitored data containing CO2 data for the space of interest,
other monitored data may also be in this file.
    FDData is a csv of event-monitored front door data for the space of interest. The code assumes that 1 represents
an opening event and 0 represents a closing event.
    IntProxData is a csv of event-monitored internal door and window data for the space of interest. As above,
the code assumes that 1 represents an opening event and 0 represents a closing event.
    OccupancyMaskFile is a csv which contains a DateTime column and an Occupied column with value True if the space is occupied
and False if the space is unoccupied. This file is optional, and can be saved from the output of the FindOccupiedTimes function.

All data frames have a DateTime column, which is not the index.

This code is written assuming that data is recorded every 5 minutes.
    '''

import numpy as N
import pandas as pd
# following line can be used to raise an error if you get the setting with copy warning, which means you get the line number which caused the issue.
#pd.set_option('mode.chained_assignment', 'raise') 
import os
import matplotlib.pyplot as pyplot
import datetime
import PlotFunctions
import SubsettingData 
import DecayAnalysis
import OSA

CaseStudy = 'Loughborough'

#
# Change directory to the folder with the data
# Data1 is a csv of the monitored data and any other environmental data
ColumnList = ['CO2A', 'CO2B', 'CO2C', 'CO2D', 'CO2E', 'CO2Ext', 'CO2F', 'CO2G', 'CO2I', 'CO2J', 'CO2K', 'CO2L', 'DateTime', 'RHA', 'RHB', 'RHC', 'RHD', 'RHE', 'RHExt2', 'RHF', 'RHG', 'RHI', 'RHJ', 'RHK', 'RHL', 'TempA', 'TempB', 'TempC', 'TempD', 'TempE', 'TempExt2', 'TempF', 'TempG', 'TempI', 'TempJ', 'TempK', 'TempL', 'TempExt3', 'RHExt3', 'CO2Ext2', 'TempM', 'RHM', 'CO2M', 'TempN', 'RHN', 'CO2N', 'RawCO2A', 'RawCO2B', 'RawCO2C', 'RawCO2D', 'RawCO2E', 'RawCO2F', 'RawCO2G', 'RawCO2I', 'RawCO2J', 'RawCO2K', 'RawCO2L', 'TempExt', 'WindParallel', 'WindNormal', 'WindSp']
Data1 = pd.read_csv('N:/Documents/PhD/Analysis/CodeForSharing/TestEnvData.csv', skiprows = 1, names = ColumnList) 

Data1['DateTime'] = pd.to_datetime(Data1['DateTime'], format = '%Y/%m/%d %H:%M:%S')

# FDData is a csv of the front door data (only needed if using the occupancy algorithm)
ColumnNames = ['DateTime', 'State']
FDData = pd.read_csv('N:/Documents/PhD/Analysis/CodeForSharing/TestFrontDoorData.csv', skiprows =1, names = ColumnNames)
FDData['DateTime'] = pd.to_datetime(FDData['DateTime'], format = '%Y-%m-%d %H:%M:%S')

# IntProxData is a csv of the internal doors and windows
DoorColumnList = ['DateTime', 'BDState', 'BRState', 'USState']
IntProxData = pd.read_csv('N:/Documents/PhD/Analysis/CodeForSharing/TestProximityData.csv', skiprows =1, names = DoorColumnList)
IntProxData['DateTime'] = pd.to_datetime(IntProxData['DateTime'], format = '%Y-%m-%d %H:%M:%S')


CO2Columns = ['CO2D','CO2E', 'CO2A', 'CO2C', 'CO2B', 'CO2F', 'CO2G']
TempColumns = ['TempD','TempE', 'TempA', 'TempC', 'TempB', 'TempF', 'TempG']
RHColumns = ['RHD','RHE','RHA', 'RHC', 'RHB', 'RHF', 'RHG']
ProxColumns = ['BDState', 'BRState', 'USState']


#Subset the data between the two times given below. All the subsequent analysis will be only for this subset.
StartTime = datetime.datetime(2018, 12, 5, 0, 0, 0)
EndTime = datetime.datetime(2018, 12, 6, 0, 0, 0)


TimeSubset = SubsettingData.SubsetDataByTime(Data1, StartTime, EndTime)
FDSubset = SubsettingData.SubsetDataByTime(FDData, StartTime, EndTime)
ProxSubset = SubsettingData.SubsetDataByTime(IntProxData, StartTime, EndTime)

#Plot the CO2 and door sensors between StartTime and EndTime
PlotFunctions.PlotCO2AndDoorSensorsAllTime(TimeSubset, CO2Columns, ProxSubset, FDSubset, CaseStudy)
# CO2Columns have been zeroed, i.e. CO2int - CO2ext.
CO2Columns = ['CO2D','CO2E', 'CO2A', 'CO2C']
# CO2ColumnsRaw have not been zeroed, i.e. CO2int.
CO2ColumnsRaw = ['RawCO2D','RawCO2E', 'RawCO2A', 'RawCO2C']
# Temperature in the measurement room
TempColumns = ['TempD','TempE', 'TempA', 'TempC']

# Calculate the mean zeroed and raw CO2 concentrations for VR analysis, and mean temp for condition during decays
TimeSubset = TimeSubset.assign(CO2Mean = TimeSubset.loc[:,CO2Columns].mean(1), RawCO2Mean = TimeSubset.loc[:,CO2ColumnsRaw].mean(1),
                               TempMean = TimeSubset.loc[:,TempColumns].mean(1))

# Calculate standard uncertainty on the mean CO2 conc = std deviation / sqrtN
# This is for estimating the uncertainty associated with the VR result
TimeSubset = TimeSubset.assign(CO2StUncert = TimeSubset.loc[:,CO2Columns].std(1)/N.sqrt(len(CO2Columns)))

# Calculate the maximum difference between the sensors used in analysis at each measurement time
# This is for deciding whether the concentrations indicate sufficient mixing. 
TimeSubset = TimeSubset.assign(MaxDiffCO2 = (TimeSubset.loc[:,CO2Columns].max(1) - TimeSubset.loc[:,CO2Columns].min(1)),
                               RawMaxDiffCO2 = (TimeSubset.loc[:,CO2ColumnsRaw].max(1) - TimeSubset.loc[:,CO2ColumnsRaw].min(1)))

######## Code for estimating whether the space is occupied and saving the occupancy mask
##GradientThreshold = 50
##NSmoothingPoints = 3
##PlotOccupancy = True
##OccupancyMask = FindOccupiedTimes(TimeSubset, FDSubset, CO2Columns, ProxSubset, GradientThreshold, PlotResults= PlotOccupancy, nAveragingPoints= NSmoothingPoints)
##OccupancyMaskFilePath = '/Volumes/homeM/Documents/PhD/Analysis/LoughboroughTestHouses/ProcessedData/OccupancyMasks/'
##OccupancyMaskFile = FileMetaData.OccupancyMask(OccupancyMaskFilePath, StartTime, EndTime, GradientThreshold, CaseStudy, NSmoothingPoints)
##OccupancyMask.to_csv((OccupancyMaskFile))

####### Code for using a saved occupancy mask 
OccupancyMaskFile = 'N:/Documents/PhD/Analysis/CodeForSharing/2018126_2018125OccupancyMask3500Test.csv'
OccupancyMask = pd.read_csv(OccupancyMaskFile, index_col=0)
OccupancyMask['DateTime'] = pd.to_datetime(OccupancyMask['DateTime'], format = '%Y-%m-%d %H:%M:%S')

# Split the data into two data frames, one each for occupied and unoccupied times.
UnoccupiedSubset = SubsettingData.SubsetByInferredUnoccupancy(TimeSubset, OccupancyMask['Occupied'])
OccupiedSubset = SubsettingData.SubsetByInferredUnoccupancy(TimeSubset, ~OccupancyMask['Occupied'])
# Find the times during the unoccupied period when the CO2 concentration measured by different sensors indicates spatial homogeneity
HomogThresh =  '10%'
RawOrZeroedData = 'Zeroed' #or 'Raw'
HomogenousUnoccupied,InhomogenousUnoccupied = DecayAnalysis.FindHomogenousCO2(UnoccupiedSubset, RawOrZeroedData,  CO2Columns+ ['CO2Mean'], CO2ColumnsRaw + ['RawCO2Mean'], Threshold = HomogThresh)

# Find the decays in the unoccupied data which meets the homogeneity requirements above
NSmoothingPoints = 3
ZeroedDataBool = True
PlotDecayPeriods = True
LimitDecayLength = True
CO2ForVRCalc = ['CO2Mean'] # Can also have more than one sensor in the list to find the locations of decays for different sensors
DecayStartPositions, DecayEndPositions, RawDecayPeriods = DecayAnalysis.IdentifyDecays(HomogenousUnoccupied, CO2ForVRCalc, CaseStudy, PlotDecays =PlotDecayPeriods, nAveragingPoints = NSmoothingPoints, SplitDecaysOnProximitySensorChange = False, ZeroedData = ZeroedDataBool, DecayLengthLimit = LimitDecayLength, AllData = TimeSubset, OccupiedData = OccupiedSubset)

# Can use this code to make masks for each of the CO2 columns individually all using the same decay times as that identified above using only one sensor, so the ventilation rates calculated using each CO2 sensor individually can be calculated.
# Run this code and then pass more than one column name in CO2ForVRCalc
##DecayStartPositions = MakeMaskForCO2Cols(DecayStartPositions, 'CO2Mean', CO2Columns)
##DecayEndPositions = MakeMaskForCO2Cols(DecayEndPositions, 'CO2Mean', CO2Columns)
##ProxSplitDecayPeriods = MakeMaskForCO2Cols(ProxSplitDecayPeriods, 'CO2BR', CO2Columns)

##
PlotDecays = True
ProportionToPlot = 0.5 # between 0 and 1 to plot a random sample of the decays
ZeroedDataForDecayAnalysis = True
ResultsFrame = DecayAnalysis.FindDecayConstant(TimeSubset, CO2ForVRCalc, DecayStartPositions, DecayEndPositions, CaseStudy, PlotDecayCurves = PlotDecays, ProportionOfPlots = ProportionToPlot, ProxData = ProxSubset, ZeroedData = ZeroedDataForDecayAnalysis)
ResultsFrame['TDiff'] = ResultsFrame['MeanRoomT'] - ResultsFrame['MeanExtT']

# Can use the following code to find the external CO2 variation during and in the hour preceding the decay period. 
ResultsFrame['CO2ExtVariation'] = N.nan
for i in ResultsFrame.index:
    DecayStartTime = ResultsFrame['DecayStartTime'].loc[i]+ datetime.timedelta(hours=-1)
    DecayEndTime = ResultsFrame['DecayEndTime'].loc[i]
    DecayVals = SubsettingData.SubsetDataByTime(TimeSubset, DecayStartTime, DecayEndTime)
    CO2Ext2Variation = DecayVals['CO2Ext2'].max() - DecayVals['CO2Ext2'].min()
    ResultsFrame.loc[i,'CO2ExtVariation'] = CO2Ext2Variation

ResultsFrameFilePath = '/Volumes/homeM/Documents/PhD/Analysis/LoughboroughTestHouses/ProcessedData/VR_Results/'
# Can use this code to save a MetaData file with the results file, recording the key variables used above
#ResultsFrameFile = FileMetaData.VR_ResultsFrame(ResultsFrameFilePath, StartTime, EndTime, CaseStudy, OccupancyMaskFile, NSmoothingPoints, RawOrZeroedData, 'Homog', HomogThresh+'+40ppm', OptionalFileNameStr='90MinMaxDecay_ExtCO2Limit', OptionalExtraInfo = 'DecayConstHours is weighted linearised fit using spread in deltaCO2 for weighting')
#UnoccupiedResultsFrame.to_csv(UnoccupiedResultsFrameFile, index = False)

# Use this code to reject decays calculated when the external variation is too high
ResultsFrameLEC = ResultsFrame[(ResultsFrame['CO2ExtVariation']<40)|(N.isnan(ResultsFrame['CO2ExtVariation']))]



