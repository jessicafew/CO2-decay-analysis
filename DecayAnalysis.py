'''Module for identifying decays and calculating decay constants'''
import numpy as N
import pandas as pd
import os
import matplotlib.pyplot as pyplot
import datetime
import PlotFunctions
import SubsettingData
import sys
from statsmodels.stats.stattools import durbin_watson
from scipy.optimize import curve_fit
import LegendListGeneral

def IdentifyDecays(InputData, CO2Columns, CaseStudy, nAveragingPoints = 1, SplitDecaysOnProximitySensorChange = True,
                   PlotDecays = False, ZeroedData = False, AllData = None, OccupiedData = None, Threshold = 50, MinDecayPoints=8, DecayLengthLimit=False):
    '''Function for identifying periods where the CO2 level is decaying for
    more than MinDecayPoints. 
    InputData should be a data frame containing the datetime, CO2 data.
    If DecayLengthLimit = True then the data are split into max 1 hour long decays, assuming the data are recorded every 5 minutes.  '''
    
    ContinuousTimeSteps = MinDecayPoints # 8 for half an hour, 14 for 1 hour. Edge effects because can't tell exactly between data points the occupancy ended/ started.

    # Average the CO2 data by nAveragingPoints, no averaging by default
    AveragedCO2 = InputData[CO2Columns].rolling(window=nAveragingPoints,center=True, min_periods=1).mean()

    # Shift all data up by one to compare t0 to t1 at the same array position
    NextTimeStepAveragedCO2 = AveragedCO2.shift(-1)

    # Boolean dataframe mask of decaying CO2, ie. if the next time step t2 is smaller than the current step t1 then the value at t1 will be true
    if ZeroedData:
        InitialDecayingCO2Positions = (AveragedCO2 > NextTimeStepAveragedCO2) & (AveragedCO2>Threshold) & (~N.isnan(InputData[CO2Columns])) # added > 100 to code to deal with decays in the noise, added isnan to remove nan values filled in by long smooths
    else:
        InitialDecayingCO2Positions = (AveragedCO2 > NextTimeStepAveragedCO2) & (AveragedCO2>(450+Threshold)) &  (~N.isnan(InputData[CO2Columns])) # added > 500 to code to deal with decays in the noise

    # loop for finding a series of decaying values, will retain a true value if there are more than MinDecayPoints decaying points in a row. 
    # Initialise data frames for the for loop
    TimeStepi = InitialDecayingCO2Positions   
    TimeStepi2 = TimeStepi # Initialise the value

    for i in N.arange(1,ContinuousTimeSteps):
        TimeStepi2 = TimeStepi2.shift(-1) # Shift the data frame up by one
        # The value is true if the i+1th point after the current time step is decaying
        TimeStepi = (TimeStepi == True) & (TimeStepi2 == True) # True if both the current step and the next one are decaying
        
    # Restore all the decays from the end of the list which are removed by shifting the dataframe, except the last one because can't tell when the decay stopped
    # Initialise values for the for loop
    TimeStepi2 = TimeStepi.shift(0) 
    TimeStepi = (((TimeStepi == True) & (TimeStepi2== True)) | ((TimeStepi == False) & (TimeStepi2 == True)) |  ((pd.isnull(TimeStepi) == True) & (TimeStepi2 == True)))
    
    for i in N.arange(1,ContinuousTimeSteps):
        TimeStepi2 = TimeStepi2.shift(1)
        TimeStepi = (((TimeStepi == True) & (TimeStepi2== True)) | ((TimeStepi == True) & (TimeStepi2 == False)) | ((TimeStepi == False) & (TimeStepi2 == True)) |  ((TimeStepi == True) & (pd.isnull(TimeStepi2)== True)) |  ((pd.isnull(TimeStepi)==True) & (TimeStepi2 == True)))

    # Record decay positions
    RawDecayPeriods = TimeStepi

    #Record start point of the decay
    DecayPeriodsi2 = RawDecayPeriods.shift(1)
    DecayStartPositions = ((RawDecayPeriods == True) & (DecayPeriodsi2 == False)) | ((RawDecayPeriods == True) & (pd.isnull(DecayPeriodsi2) == True))
    
    # Record the last point of the decay
    DecayPeriodsi2 = RawDecayPeriods.shift(-1)
    DecayEndPositions = ((RawDecayPeriods == True) & (DecayPeriodsi2 == False)) | ((RawDecayPeriods == True) & (pd.isnull(DecayPeriodsi2) == True))

    ######

    if DecayLengthLimit == True:
        # This splits the decay into multiple shorter decays. The long decay is split into as many hour-long decays as possible. If there is <1hr30 left at the end then the final section is split in half
        DecayStartPositions, DecayEndPositions = LimitDecayLength(DecayStartPositions, DecayEndPositions, CO2Columns)
    

    ######             
    if PlotDecays == True:
        PlotFunctions.PlotIdentifyDecayCurves(InputData, CO2Columns, RawDecayPeriods, DecayStartPositions, DecayEndPositions,
                                nAveragingPoints, CaseStudy, AllData, OccupiedData)
        # Plot the decay periods with the rest of the data.          

    ######
    return DecayStartPositions, DecayEndPositions, RawDecayPeriods

####

def LimitDecayLength(DecayStartPositions, DecayEndPositions, CO2Columns):
    '''Function for limiting the maximum allowed length of CO2 decays to 1 hour 25 mins'''
    for CO2Sensor in CO2Columns: #loop over the decay start / end positions for each sensor
        StartIndex = N.flatnonzero(DecayStartPositions[CO2Sensor]) # The positions of the decay start positions for CO2Sensori
        EndIndex = N.flatnonzero(DecayEndPositions[CO2Sensor])
        for idx in range(0,len(StartIndex)): # loop over each decay start position found for this sensor
            NDecayPoints = EndIndex[idx]- StartIndex[idx]
            NCompleteHours = NDecayPoints//12
            NRemainingPoints = NDecayPoints%12

            if NCompleteHours ==1:
                if NRemainingPoints > 7:
                    DecayEndPositions[CO2Sensor].iloc[StartIndex[idx]+((12+NRemainingPoints)//2)] = True
                    DecayStartPositions[CO2Sensor].iloc[StartIndex[idx]+((12+NRemainingPoints)//2+1)] = True
                    
                
            if NCompleteHours > 1:
                if NRemainingPoints < 7: # this will allow up to 1.5 hour decay at the end
                    for i in N.arange(1, NCompleteHours):
                       DecayStartPositions[CO2Sensor].iloc[StartIndex[idx]+12*i] = True # i.e. start a new decay for each complete hour after the decay began
                       DecayEndPositions[CO2Sensor].iloc[StartIndex[idx]+12*i-1] = True # i.e. end the decay at 55 mins after each decay starts, so the data at 1 hour is not used in two decays.

                elif NRemainingPoints >= 7:
                    for i in N.arange(1, NCompleteHours):
                       DecayStartPositions[CO2Sensor].iloc[StartIndex[idx]+12*i] = True # i.e. start a new decay for each complete hour after the decay began
                       DecayEndPositions[CO2Sensor].iloc[StartIndex[idx]+12*i-1] = True
                    # Split final 1.5-2 hours into two equal decays   
                    DecayEndPositions[CO2Sensor].iloc[StartIndex[idx]+(12*(NCompleteHours-1)+((12+NRemainingPoints)//2))] = True
                    DecayStartPositions[CO2Sensor].iloc[StartIndex[idx]+(12*(NCompleteHours-1)+((12+NRemainingPoints)//2)+1)] = True

    return DecayStartPositions, DecayEndPositions



def ExponentialModel(ElapsedTime, DecayConst, InitialCO2):
    return InitialCO2*N.exp(-DecayConst*ElapsedTime)

##

def FindDecayConstant(InputData, CO2Columns, DecayStartPositions, DecayEndPositions, CaseStudy, PlotDecayCurves = False, ProportionOfPlots = 1, ProxData = [], ZeroedData = False):
    '''Function for finding the decay constant of a CO2 decay period given a data frame
    of the input data, and Boolean masks of this dataframe for the DecayStartPositions and
    DecayPeriods.'''
    # Initialise results
    NumberOfDecays = sum((DecayStartPositions == True).sum())
    ResultsColumns = ['CO2Sensor','DecayStartTime', 'DecayEndTime', 'CO2Start', 'CO2End', 'DecayConstHours', 'MeanRoomT',
                      'MeanExtT', 'DurbinWatson', 'ExpRMS', 'LinRMS',
                      'UncertaintyVRFitSpread', 'UncertaintyVRFitSensorUncert', 'CO2DiffVals', 'WindSpMidas', 'WindDirMidas',
                      'Config', 'ProportionOpenWindows', 'CO2StUncertMeanMaxMin', 'DecayConstCurveFit', 'DecayConstNWLin']
    ResultsFrame = pd.DataFrame(index = range(1,NumberOfDecays+1), columns = ResultsColumns)
    n = 1 # For keeping track of which row the results go in
    
    for i in CO2Columns: # i is the CO2Sensor column name
        StartIndexi = N.flatnonzero(DecayStartPositions[i]) # The positions of the decay start positions for CO2Sensori
        EndIndexi = N.flatnonzero(DecayEndPositions[i])
        # Find the estimated background CO2 level for this CO2 sensor
        if ZeroedData:
            ExternalCO2 = 0
        elif CaseStudy == 'MRes':
            ExternalCO2 = FindIndividualSensorBkgCO2(InputData[['DateTime', i]], i, CaseStudy)
        elif CaseStudy == 'Loughborough':
            if (i == 'RawCO2BR') | (i=='RawCO2US'):
                ExternalCO2 = 430
            else:
                if i[0:3]== 'Raw':
                    ApproxExtCO2 = pd.read_csv('/Volumes/homeM/Documents/PhD/Analysis/LoughboroughTestHouses/CombinedData/SensorApproxCO2ExternalUsingUnoccupiedPeriod.csv') ## the code for calculating these offsets is in the sensor consistency.py file, this uses the FindIndividualSensorBkgCO2 function.
                    ExternalCO2 = ApproxExtCO2[i[3:]][0] # [3:] is to get rid of Raw at the beginning of the sensor name so the column matches that in the file.
                else:
                    ApproxExtCO2 = pd.read_csv('/Volumes/homeM/Documents/PhD/Analysis/LoughboroughTestHouses/CombinedData/SensorApproxCO2ExternalUsingUnoccupiedPeriod.csv') ## the code for calculating these offsets is in the sensor consistency.py file, this uses the FindIndividualSensorBkgCO2 function.
                    ExternalCO2 = ApproxExtCO2[i][0]
 


        for j in range(0,len(StartIndexi)): # loop each decay found for this sensor
            # This loop analyses the data associated with the jth decay. 
            
            DecayStartTime = InputData['DateTime'].iloc[StartIndexi[j]]
            DecayEndTime = InputData['DateTime'].iloc[EndIndexi[j]]

            # Extract decay values
            DecayVals = InputData[i].iloc[StartIndexi[j]:EndIndexi[j]+1] # because subsetting like [a:b] returns a slice with index locations a:b-1
            
            CO2DiffVals = DecayVals - ExternalCO2
            lnCO2DiffVals = N.log(CO2DiffVals)

            # These are the standard uncertainties on the mean CO2 during the decay period.
            CO2StUncertVals = InputData['CO2StUncert'].iloc[StartIndexi[j]:EndIndexi[j]+1]
            # Can use the following code to calculate the uncertainty diffierently depending on the particular case study / sensor
##            if (CaseStudy == 'Loughborough') & (i== 'CO2BR') | (CaseStudy == 'Loughborough') & (i== 'RawCO2BR'):
##                CO2StUncertVals = InputData['BRStUncert'].iloc[StartIndexi[j]:EndIndexi[j]+1] # +1 at end because subsetting like [a:b] returns a slice with index locations a:b-1
##            elif (CaseStudy == 'Loughborough') & (i== 'CO2US') | (CaseStudy == 'Loughborough') & (i== 'RawCO2US'):
##                CO2StUncertVals = InputData['USStUncert'].iloc[StartIndexi[j]:EndIndexi[j]+1] # 
##          # If don't want to calculate an uncertainty:            
##            else:
##                CO2StUncertVals = N.array([N.nan, N.nan])
            # Extract decay times and convert to a time difference starting at t =0 (hours) for fit
            DecayTime = InputData['DateTime'].iloc[StartIndexi[j]:EndIndexi[j]+1]
            DeltaTime = DecayTime - DecayTime.iloc[0]
            DeltaTime = DeltaTime / N.timedelta64(1, 'h') # convert time differences into hours

            # Fit log data to a 1st order polynomial
            # weight the fit according to the spread in delta CO2 values. 
            Weighting = 1/(CO2StUncertVals/DecayVals) 
            LinModelDecayParams = N.polyfit(DeltaTime, lnCO2DiffVals, 1, full = True, w=Weighting) # full means the residuals are returned as well
            LinModelDecayConst = -1*LinModelDecayParams[0][0] # Air change hours
            LinModelLnCO2DiffT0 = LinModelDecayParams[0][1] # Fitted ln(CO2(t=0))
            LinModelLnCO2DiffVals = -1*LinModelDecayConst*DeltaTime + LinModelLnCO2DiffT0
            LinModelCO2DiffVals = N.exp(LinModelLnCO2DiffT0)*N.exp(-LinModelDecayConst*DeltaTime)
            LinModelResiduals = CO2DiffVals-LinModelCO2DiffVals # Residuals between measured CO2 diff vals and linear model CO2 diff vals (not difference between linearised data and linearised model)
            LinRMS = N.sqrt((LinModelResiduals**2).sum()/len(CO2DiffVals))
            LinModelDW = durbin_watson(LinModelResiduals)

            # fit not weighted by uncertainty in CO2
            NWLinModelDecayParams = N.polyfit(DeltaTime, lnCO2DiffVals, 1, full = True)  # full means the residuals are returned as well
            NWLinModelDecayConst = -1*NWLinModelDecayParams[0][0] # Air change hours
            NWLinModelLnCO2DiffT0 = NWLinModelDecayParams[0][1] # Fitted ln(CO2(t=0))
            NWLinModelLnCO2DiffVals = -1*NWLinModelDecayConst*DeltaTime + NWLinModelLnCO2DiffT0
            NWLinModelCO2DiffVals = N.exp(NWLinModelLnCO2DiffT0)*N.exp(-NWLinModelDecayConst*DeltaTime)
            NWLinModelResiduals = CO2DiffVals-NWLinModelCO2DiffVals # Residuals between measured CO2 diff vals and linear model CO2 diff vals (not difference between linearised data and linearised model)
            NWLinRMS = N.sqrt((NWLinModelResiduals**2).sum()/len(CO2DiffVals))
            
            
            # Fit non-log data to curve
            CO2DiffValsNoNans = CO2DiffVals[~N.isnan(CO2DiffVals)]
            DeltaTimeNoNans = DeltaTime[~N.isnan(CO2DiffVals)]
            ExpModelDecayParams = curve_fit(ExponentialModel, DeltaTimeNoNans, CO2DiffValsNoNans)
            ExpModelDecayConst = ExpModelDecayParams[0][0] # Air change hours
            ExpModelCO2DiffT0 = ExpModelDecayParams[0][1] # Fitted (CO2(t=0))
            ExpModelLnCO2DiffT0 = N.log(ExpModelCO2DiffT0)
            ExpModelCO2DiffVals = ExpModelCO2DiffT0*N.exp(-ExpModelDecayConst*DeltaTime)
            ExpModelResiduals = CO2DiffVals-(ExpModelCO2DiffVals)
            ExpRMS = N.sqrt((ExpModelResiduals**2).sum()/len(CO2DiffVals))
            ExpModelDW = durbin_watson(ExpModelResiduals)

            # Calculate the standard uncertainties on the ln(Delta CO2) values from the standard uncertainty of the DeltaCO2 values
            if (ZeroedData) and ((i=='CO2BR')| (i=='RawCO2BR')):
                UncertaintyDecayVals = InputData['BRStUncert'].iloc[StartIndexi[j]:EndIndexi[j]+1]
                UncertaintyLnDecayVals = (UncertaintyDecayVals) / (DecayVals)
            elif (i=='CO2Mean'):
                UncertaintyDecayVals = InputData['CO2StUncert'].iloc[StartIndexi[j]:EndIndexi[j]+1]
                UncertaintyLnDecayVals = (UncertaintyDecayVals) / (DecayVals)
            
            # Can also use the following function to calculate the uncertainty on the VR using the stated accuracy of the sensor.
            # Note that the stated accuracy from Eltek is intended to represent a worst case scenario, not the expected uncertainty, so this is likely to be an overestimate.
            elif i == 'YourSensor':
                UncertaintyDecayVals, UncertaintyLnDecayVals = CalculateDecayValUncertaintyEltekAccuracy(DecayVals, ExternalCO2, lnCO2DiffVals)

            # Calculate the uncertainty on the decay curve. If using the standard uncertainty from the lines above, this gives an estimate of the uncertainty due to spatial inhomogeneity. 
            UncertaintyDecayConst = CalculateDecayConstantUncertainty(UncertaintyLnDecayVals, DeltaTime)

            # The following lines calculate the uncertainty on the ventilation rate due to sensor uncertainty associted with each measurement of DeltaCO2
            # Note that the values in the following lines were based on my experiments - probably worth chatting through this bit if you want to do something similar
            if (i=='CO2Mean'):
                SensorUncert = N.sqrt(4*((1/4)*N.sqrt(5**2+1.5**2))**2 + 5**2)
            
            UncertaintyLnDecayVals = N.log(SensorUncert)/DecayVals
            UncertaintyDecayConstSensorUncert = CalculateDecayConstantUncertainty(UncertaintyLnDecayVals, DeltaTime)
            
            # Plot the data & fit and associated information if the following condition is met
            if ((PlotDecayCurves == True) & (N.random.rand() < ProportionOfPlots)):
                # Export additional data either side of the decay so can see overall shape of data
                ExtendedDecayData = InputData.iloc[StartIndexi[j]-12:EndIndexi[j]+12]
                if isinstance(ProxData, pd.DataFrame):
                    ProxDataDecay = SubsettingData.SubsetDataByTime(ProxData, (DecayStartTime+ datetime.timedelta(hours=-1)), DecayEndTime+ datetime.timedelta(hours=1))
                    ProxDataDecay = ProxDataDecay.assign(DeltaTime = (ProxDataDecay.loc[:,'DateTime'] - DecayStartTime)/N.timedelta64(1,'h'))
                    
                ProxData = ProxData.assign(DeltaTime= (ProxData.loc[:,'DateTime'] - DecayStartTime)/N.timedelta64(1,'h'))
                PlotFunctions.PlotDecayCurveFit(ExtendedDecayData, DecayTime, i, CO2DiffVals, lnCO2DiffVals, DeltaTime, LinModelLnCO2DiffT0, LinModelDecayConst,  LinModelLnCO2DiffVals, LinModelDW, ExpModelCO2DiffT0, ExpModelDecayConst, ExpModelCO2DiffVals, ExpModelDW, DecayStartTime, UncertaintyDecayVals, UncertaintyLnDecayVals, ExternalCO2, CO2Columns, CaseStudy, ProxData)
                
            # Find the average internal temperature during the decay
            # Choose the relevant temperature sensor
            if (i == 'CO2BR') | (i == 'RawCO2BR'):
                TempSensor = 'TempBR'
            elif i == 'CO2Mean':
                TempSensor = 'TempMean'
                
            TempVals = InputData[TempSensor][StartIndexi[j]:EndIndexi[j]]
            MeanRoomT = TempVals.mean()

            # Find the outdoor temperaure during the decay. 
            if (CaseStudy == 'Loughborough') | (CaseStudy == 'ExampleCaseStudy'):
                OutdoorTemp = InputData['TempExt'][StartIndexi[j]:EndIndexi[j]]
                MeanExtT = N.nanmean(OutdoorTemp)
                if (N.isnan(MeanExtT)) & (CaseStudy == 'Loughborough'):# use ext hobo sensor for temperature if Virginia's temperature data are missing.
                    OutdoorTemp = InputData['TempExt2'][StartIndexi[j]:EndIndexi[j]]
                    MeanExtT = N.nanmean(OutdoorTemp)
            else:
                MeanExtT = N.nan

            # Find MIDAS wind during the decay if available for this case study
            if (CaseStudy == 'Loughborough'):
                WindSpMidas, WindDirMidas = FindMIDASWeather(DecayStartTime,  InputData['DateTime'].iloc[EndIndexi[j]], CaseStudy)
            else:
                WindSpMidas = None
                WindDirMidas = None
                
            # This finds the proportion of windows open during the decay if you code your case study and sensors into the function.
            if (CaseStudy == '2A') | (CaseStudy == '2B') | (CaseStudy == '2D') | (CaseStudy == '2C'):
                ProportionOpenWindows, Config = FindProportionOpenWindowsAndConfigDescription(DecayStartTime, ProxData, CaseStudy, i)
            else:
                ProportionOpenWindows = -1
                Config = 'Not yet coded!'

            # Record results for further analysis
            ResultsFrame.loc[n,'CO2Sensor'] = i
            ResultsFrame.loc[n,'DecayStartTime'] = DecayStartTime
            ResultsFrame.loc[n,'DecayEndTime'] =  InputData['DateTime'].iloc[EndIndexi[j]]
            ResultsFrame.loc[n,'CO2Start'] =  InputData[i].iloc[StartIndexi[j]]
            ResultsFrame.loc[n,'CO2End'] =  InputData[i].iloc[EndIndexi[j]]
            ResultsFrame.loc[n,'DecayConstHours'] = LinModelDecayConst
            ResultsFrame.loc[n,'MeanRoomT'] = MeanRoomT
            ResultsFrame.loc[n,'MeanExtT'] = MeanExtT
            ResultsFrame.loc[n,'DurbinWatson'] = LinModelDW
            ResultsFrame.loc[n,'ExpRMS'] = ExpRMS
            ResultsFrame.loc[n,'LinRMS'] = LinRMS
            ResultsFrame.loc[n,'UncertaintyVRFitSpread'] = UncertaintyDecayConst
            ResultsFrame.loc[n,'UncertaintyVRFitSensorUncert'] = UncertaintyDecayConstSensorUncert
            ResultsFrame.loc[n,'CO2DiffVals'] = [CO2DiffVals]
            ResultsFrame.loc[n,'WindSpMidas'] = WindSpMidas
            ResultsFrame.loc[n,'WindDirMidas'] = WindDirMidas
            ResultsFrame.loc[n,'Config']= Config
            ResultsFrame.loc[n,'ProportionOpenWindows'] = ProportionOpenWindows
            ResultsFrame.loc[n,'CO2StUncertMeanMaxMin'] = [CO2StUncertVals.mean(), CO2StUncertVals.max(), CO2StUncertVals.min()] 
            ResultsFrame.loc[n,'DecayConstCurveFit'] = ExpModelDecayConst
            ResultsFrame.loc[n,'DecayConstNWLin'] = NWLinModelDecayConst

            n= n+1 # Increment the index for the next result
            
 
    return ResultsFrame


def FindProportionOpenWindowsAndConfigDescription(StartTime, ProxData, CaseStudy, CO2Sensor):

    ProportionOpen = 0

    if CaseStudy == '2A':
        WindowCols = ['LivWLH', 'LivWM', 'LivWRH', 'BedW']
        DoorCols = ['LivD', 'BedD', 'BathD']
    if (CaseStudy == '2B')  | (CaseStudy == '2C'):
        WindowCols = ['LivWLH', 'LivWRH', 'BedW']
        DoorCols = ['BathD']
    if CaseStudy == '2D':
        DoorCols = ['LivD', 'BathD', 'BedD']
        WindowCols = ['LivW1', 'LivW2', 'LivW3', 'BedW', 'KitW']
##        ExtraSensorInstall = datetime.datetime(2019, 7, 31, 18, 30, 0)
##        if StartTime < ExtraSensorInstall:
##            WindowCols = ['BedW', 'KitW']
##        else:
##            

    # find entry for last door/window change event before the start of the decay.
    IndexPosition = ProxData['DateTime'].searchsorted(StartTime)[0] - 1 # minus 1 finds the last entry BEFORE the StartTime
                
    
    for Window in WindowCols:
        if ProxData.iloc[IndexPosition][Window]==1:
            ProportionOpen = ProportionOpen + (1/len(WindowCols))
     
    ConfigDescription = GenerateDescription(ProxData[WindowCols+DoorCols].iloc[IndexPosition], WindowCols, DoorCols)
                    
    return ProportionOpen, ConfigDescription


def GenerateDescription(ProxRow, WindowCols, DoorCols):
    Description = 'WO: '

    if (ProxRow[WindowCols]).sum() == len(WindowCols):
        Description= Description+'All '
    elif (ProxRow[WindowCols]).sum() == 0:
        Description= Description+'None '
    else:
        for Window in WindowCols:
            if ProxRow[Window] == 1:
                Description= Description+ Window
            if ProxRow[Window] == -99:
                Description = Description + Window +'NI'

    Description= Description+' DO: '

    if (ProxRow[DoorCols]).sum() == len(DoorCols):
        Description= Description+'All'
    elif (ProxRow[DoorCols]).sum() == 0:
        Description = Description+'None'                 
    else:
        for Door in DoorCols:
            if ProxRow[Door] == 1:
                Description= Description+Door

    return Description




def FindMIDASWeather(StartTime, EndTime, CaseStudy):
    '''Find the average wind speed and wind direction between StartTime and EndTime. The weather data cam be downloaded from MIDAS, then use the CaseStudy variable as below to indicate
which file should be opened for each case study.'''
    
    MIDASColumnList = ['DateTime', 'StationID', 'WindDir', 'WindSp', 'AirT', 'DewPoint', 'WetBulbT']
    if CaseStudy == 'ExampleCaseStudy':
        MidasWindFile = pd.read_excel('ExampleFilePath+FileName.xlsx', skiprows = 2, names = MIDASColumnList)
        MidasWindFile['DateTime'] = pd.to_datetime(MidasWindFile['DateTime'], format = '%d/%m/%Y %H:%M')
    else:
        return (None, None)

    MidasWindFile = MidasWindFile.replace({' ': None}) # Replace missing values with python none
    MidasWindFile.iloc[:,1:7] = MidasWindFile.iloc[:,1:7].astype(float)

    MIDASStartHour = StartTime.replace(minute = 0, second =0) + datetime.timedelta(hours = 1) # this is because the MIDAS data is hourly, and the the data at time 1100 reports the mean values between 1000 and 1100.
    MIDASEndHour = EndTime.replace(minute = 0, second = 0) + datetime.timedelta(hours = 1) # this is because the MIDAS data is hourly, and the the data at time 1100 reports the mean values between 1000 and 1100.

    MIDASDifference = (MIDASEndHour - MIDASStartHour).total_seconds()/3600
    
    if MIDASStartHour > MidasWindFile['DateTime'].iloc[-1]:
        AvgWindSp = N.nan
        AvgWindDir = N.nan

    elif MIDASDifference == 0:
        AvgWindSp = MidasWindFile['WindSp'][MidasWindFile['DateTime'] == MIDASStartHour].values[0]
        AvgWindDir = MidasWindFile['WindDir'][MidasWindFile['DateTime'] == MIDASStartHour].values[0]

    
    elif MIDASDifference == 1:
        # Wind speed average is the scalar average, wind direction is the vector average.
        TotalDecayLength = ((EndTime - StartTime).total_seconds())/3600
        TimeInFirstWindHour = ((MIDASStartHour - StartTime).total_seconds())/3600
        TimeInLastWindHour = 1-((MIDASEndHour - EndTime).total_seconds())/3600 # 1- because want time from beginning of hour to end of decay time.

        WindSpStart = MidasWindFile['WindSp'][MidasWindFile['DateTime'] == MIDASStartHour].values[0]
        WindSpEnd = MidasWindFile['WindSp'][MidasWindFile['DateTime'] == MIDASEndHour].values[0]
        WindDirStart = MidasWindFile['WindDir'][MidasWindFile['DateTime'] == MIDASStartHour].values[0]
        WindDirEnd = MidasWindFile['WindDir'][MidasWindFile['DateTime'] == MIDASEndHour].values[0]
            
        AvgWindSp = (TimeInFirstWindHour*WindSpStart + TimeInLastWindHour*WindSpEnd)/(TotalDecayLength)

        # Vector average wind direction
        ResultantNorthComponent = ((TimeInFirstWindHour/TotalDecayLength)*WindSpStart*N.cos(WindDirStart*2*N.pi/360) + (TimeInLastWindHour/TotalDecayLength)*WindSpEnd*N.cos(WindDirEnd*2*N.pi/360)) 
        ResultantEastComponent = ((TimeInFirstWindHour/TotalDecayLength)*WindSpStart*N.sin(WindDirStart*2*N.pi/360) + (TimeInLastWindHour/TotalDecayLength)*WindSpEnd*N.sin(WindDirEnd*2*N.pi/360)) 
        
        AvgWindDir = (N.arctan2(ResultantEastComponent, ResultantNorthComponent)*180/N.pi)
        if AvgWindDir <0:
            AvgWindDir = AvgWindDir+360

    elif MIDASDifference >1:
        # Wind speed average is the scalar average, wind direction is the vector average.
        TotalDecayLength = ((EndTime - StartTime).total_seconds())/3600
        TimeInFirstWindHour = ((MIDASStartHour - StartTime).total_seconds())/3600
        TimeInLastWindHour = 1-((MIDASEndHour - EndTime).total_seconds())/3600 # 1- because want time from beginning of hour to end of decay time.
        WindSpStart = MidasWindFile['WindSp'][MidasWindFile['DateTime'] == MIDASStartHour].values[0]
        WindSpEnd = MidasWindFile['WindSp'][MidasWindFile['DateTime'] == MIDASEndHour].values[0]
        WindDirStart = MidasWindFile['WindDir'][MidasWindFile['DateTime'] == MIDASStartHour].values[0]
        WindDirEnd = MidasWindFile['WindDir'][MidasWindFile['DateTime'] == MIDASEndHour].values[0]

        MiddleData = (MidasWindFile[['DateTime', 'WindSp', 'WindDir']][(MidasWindFile['DateTime'] > MIDASStartHour) & (MidasWindFile['DateTime'] < MIDASEndHour)])
        
        # Scalar average of wind speed
        AvgWindSp = (TimeInFirstWindHour*WindSpStart + TimeInLastWindHour*WindSpEnd + MiddleData['WindSp'].sum())/(TotalDecayLength)
        # Vector average wind direction
        ResultantNorthComponent = ((TimeInFirstWindHour/TotalDecayLength)*WindSpStart*N.cos(WindDirStart*2*N.pi/360) + (TimeInLastWindHour/TotalDecayLength)*WindSpEnd*N.cos(WindDirEnd*2*N.pi/360)) + ((1/TotalDecayLength)*(MiddleData['WindSp'])*N.cos(list(MiddleData['WindDir']*N.pi/180))).sum()
        ResultantEastComponent = ((TimeInFirstWindHour/TotalDecayLength)*WindSpStart*N.sin(WindDirStart*2*N.pi/360) + (TimeInLastWindHour/TotalDecayLength)*WindSpEnd*N.sin(WindDirEnd*2*N.pi/360)) + ((1/TotalDecayLength)*(MiddleData['WindSp'])*N.sin(list(MiddleData['WindDir']*N.pi/180))).sum()
        
        AvgWindDir = (N.arctan2(ResultantEastComponent, ResultantNorthComponent)*180/N.pi)
        if AvgWindDir <0:
            AvgWindDir = AvgWindDir+360            


    return (AvgWindSp, AvgWindDir)

            
def CalculateDecayValUncertaintyEltekAccuracy(DecayVals, ExternalCO2, lnCO2DiffVals):
    '''Find the uncertainty on each point in the decay curve, given the quoted uncertainty on the CO2 sensor'''
    
    UncertaintyDecayVals = DecayVals*0.03+50 # This is the quoted uncertainty on the CO2 sensor

    BackgroundUncertainty = ExternalCO2*0.05+50 # 50+5% for Hobo CO2 sensor, 50+3% for Eltek sensor.
    DifferenceUncertainty = N.sqrt((UncertaintyDecayVals**2)+(BackgroundUncertainty**2))
    UncertaintyLnDecayVals = DifferenceUncertainty/DecayVals
    
    return(UncertaintyDecayVals, UncertaintyLnDecayVals)

    
def CalculateDecayConstantUncertainty(UncertaintyLnDecayVals, DeltaTime):
    '''Find the uncertainty on the decay constant, given the uncertainty in the ln(deltaCO2)
    Hughes & Hase page 70'''

    WeightedUncertainty = (UncertaintyLnDecayVals**-2)
    SumWeightedUncertainty = WeightedUncertainty.sum()

    WiXi2 = WeightedUncertainty*(DeltaTime**2)
    SumWiXi2 = WiXi2.sum()

    SumWiXi = (WeightedUncertainty*DeltaTime).sum()

    Denominator = SumWeightedUncertainty*SumWiXi2 - SumWiXi**2

    DecayUncertainty = N.sqrt(SumWeightedUncertainty/Denominator)
    
    return DecayUncertainty


def StartEndTimesForResultsFrame(ResultsFrame, InputData, CO2Columns):
    NewDecayStartTimes = pd.DataFrame(index=InputData.index)
    NewDecayStartTimes[CO2Columns] = False
    NewDecayStartTimes[CO2Columns][InputData['DateTime'].isin(ResultsFrame['DecayStartTime'])] = True

    NewDecayEndTimes = pd.DataFrame(index=InputData.index)
    NewDecayEndTimes[CO2Columns] = False
    NewDecayEndTimes[CO2Columns][InputData['DateTime'].isin(ResultsFrame['DecayEndTime'])] = True

    return(NewDecayStartTimes, NewDecayEndTimes)


def FindHomogenousCO2(InputData, RawOrZeroed, CO2Columns, RawCO2Columns, Threshold = 'StatedAccuracy', CaseStudyStr = ''):
    ''''Find the times when the CO2 sensors in the RawOrZeroed columns all agree within the given threshold. If Threshold = 'StatedAccuracy' as the
    default, then the Eltek stated accuracy is used with the raw data columns. StatedAccuracy refers to an EltekGD47.'''
    HomogenousCO2 = InputData.copy()
    InhomogenousCO2 = InputData.copy()


    if Threshold == 'StatedAccuracy':
        if RawOrZeroed == 'Zeroed':
            print('To use the stated accuracy of the sensors as the homogeneity threshold, this function needs Raw CO2 data')
        elif RawOrZeroed == 'Raw':
            Threshold = 100 + 0.03*(HomogenousCO2.loc[:,RawCO2Columns].min(1) + HomogenousCO2.loc[:,RawCO2Columns].max(1))

    elif Threshold[-1] == '%':
        Threshold =  int(Threshold[:-1])*0.01*(HomogenousCO2.loc[:,CO2Columns].max(1)) # Use CO2 diff to calculate what threshold % is for each row
        if CaseStudyStr == '2A':
            MinCutOff = 50
        else:
            MinCutOff = 40
        Threshold[Threshold<MinCutOff]=MinCutOff # can choose a cut off so the min allowed difference is an int, e.g. to account for precision.

    if RawOrZeroed == 'Raw':
        HomogenousCO2.loc[HomogenousCO2['RawMaxDiffCO2']>Threshold, CO2Columns+RawCO2Columns] = N.nan
        InhomogenousCO2.loc[InhomogenousCO2['RawMaxDiffCO2']<Threshold, CO2Columns+RawCO2Columns] = N.nan
    elif RawOrZeroed == 'Zeroed':
        HomogenousCO2.loc[HomogenousCO2['MaxDiffCO2']>Threshold, CO2Columns+RawCO2Columns] = N.nan
        InhomogenousCO2.loc[InhomogenousCO2['MaxDiffCO2']<Threshold, CO2Columns+RawCO2Columns] = N.nan
    else:
        print('''RawOrZeroed value should be either 'Raw' or 'Zeroed' ''')
        HomogenousCO2 = 'Not calculated - Invalid RawOrZeroed value given'
        InhomogenousCO2 = 'Not calculated - Invalid RawOrZeroed value given'

    return HomogenousCO2, InhomogenousCO2
    

def FindTDiffDistribution(DataSubset, VRResultsFrame, CaseStudy):
    pyplot.set_cmap('viridis')
    cmap = pyplot.cm.viridis
    pyplot.hist(DataSubset['TDiff'].dropna(), normed = True, alpha = 0.7, color = cmap(0))
    pyplot.hist(VRResultsFrame['TDiff'].dropna(), normed= True, alpha = 0.7, color = cmap(0.8))
    pyplot.legend(['Occupied', 'Measurement'])
    pyplot.xlabel('Delta T')
    pyplot.ylabel('Normalised Frequency')
    pyplot.show()    


def FindWindSpDistribution(DataSubset, VRResultsFrame, CaseStudy):
    pyplot.set_cmap('viridis')
    cmap = pyplot.cm.viridis
    pyplot.hist(DataSubset['WindSpMidas'].dropna(), normed = True, alpha = 0.7, color = cmap(0))
    pyplot.hist(VRResultsFrame['WindSpMidas'].dropna(), normed= True, alpha = 0.7, color = cmap(0.8))
    pyplot.legend(['Occupied', 'Measurement'])
    pyplot.xlabel('Wind Speed')
    pyplot.ylabel('Normalised Frequency')
    pyplot.show() 
    
                  
def FindWindDirDistribution(DataSubset, VRResultsFrame, CaseStudy):
    pyplot.set_cmap('viridis')
    cmap = pyplot.cm.viridis
    pyplot.hist(DataSubset['WindDirMidas'].dropna(), normed = True, alpha = 0.7, color = cmap(0))
    pyplot.hist(VRResultsFrame['WindDirMidas'].dropna(), normed= True, alpha = 0.7, color = cmap(0.8))
    pyplot.legend(['Occupied', 'Measurement'])
    pyplot.xlabel('Wind Direction')
    pyplot.ylabel('Normalised Frequency')
    pyplot.show() 
