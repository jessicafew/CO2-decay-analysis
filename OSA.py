# Import packages and data
import numpy as N
import pandas as pd
import matplotlib.pyplot as pyplot
import os
from SubsettingData import *
from PlotFunctions import *
import datetime


def FindPreviousEltekTime(FDTimeStamp, InputTimeIndex):
    '''This function finds the previous Eltek time before the given timestamp. ie. if the time was hh:49 it would find hh:45.'''
    IdxPos = InputTimeIndex.get_loc(FDTimeStamp, method = 'ffill')
    EltekTime = InputTimeIndex[IdxPos]
    return(EltekTime)

def FindNextEltekTime(FDTimeStamp, InputTimeIndex):
    '''This function finds the next Eltek time after the given timestamp. ie. if the time was hh:41 it would find hh:45.'''
    IdxPos = InputTimeIndex.get_loc(FDTimeStamp, method = 'bfill')
    EltekTime = InputTimeIndex[IdxPos]
    return(EltekTime)

def FindNearestEltekTime(TimeStamp, InputTimeIndex):
    '''This function finds the closest time in the InputData time column.'''

    IdxPos = InputTimeIndex.get_loc(FDTimeStamp, method = 'nearest')
    EltekTime = InputTimeIndex[IdxPos]
    return(EltekTime)

def SetFDStateChangesOccupied(FrontDoorStateChange, OccupancyMask, InputTimeIndex):
    '''Update occupancy mask to show times when there is a change in state of the front door as occpuied.
    Only make the next subsequent Eltek data point occupied, not also the preceding once, since this is the
    data point which has collected data from the 5 minutes preceding the timestamp.'''
    for StateChangeTime in FrontDoorStateChange['DateTime']:
        EltekTime = FindNextEltekTime(StateChangeTime, InputTimeIndex)
        OccupancyMask['Occupied'].loc[OccupancyMask['DateTime']== EltekTime] = True
    return(OccupancyMask)


def FindTimesBetweenDoorChanges(FrontDoorStateChange, CloseTimeIndex, InputTimeIndex):
    Eltek_t0 = FindPreviousEltekTime(FrontDoorStateChange['DateTime'].iloc[CloseTimeIndex], InputTimeIndex)
    Eltek_t1 = FindPreviousEltekTime(FrontDoorStateChange['DateTime'].iloc[CloseTimeIndex+1], InputTimeIndex)
    return(Eltek_t0, Eltek_t1)

def CleanNaNsinProxData(InputData, ProxColumns):
    
    if InputData[ProxColumns].isnull().values.any():
        IntermediateProxData = InputData.copy() 
        IntermediateProxData2 = pd.DataFrame(index=InputData[ProxColumns].index, columns= ProxColumns)
        FinalProxData = pd.DataFrame(index=InputData[ProxColumns].index, columns= ProxColumns)
        for ProxSensor in ProxColumns:
            if IntermediateProxData[ProxSensor].isnull().values.any():
                while not (IntermediateProxData[ProxSensor].equals(IntermediateProxData2[ProxSensor])):
                    IntermediateProxData2[ProxSensor] = IntermediateProxData[ProxSensor]
                    ProxSensorNaNsMask = IntermediateProxData[ProxSensor].isnull()
                    NextStepProxData = IntermediateProxData[ProxSensor].shift(-1)
                    IntermediateProxData.loc[ProxSensorNaNsMask, ProxSensor] = NextStepProxData.loc[ProxSensorNaNsMask]
            FinalProxData[ProxSensor] = IntermediateProxData[ProxSensor]
    else:
        FinalProxData = InputData[ProxColumns]
    return(FinalProxData)

def AnyDoorChangesEltek(InputData, ProxColumns):
    # Take the first data point off the proximity data since the proximity data is state-logged not event logged, so there can be a delay between the door actually closing and the recording of the data
    #print(InputData)
    DataToAnalyse = InputData.loc[InputData.index[1]:,]
    N_points = len(DataToAnalyse)
    DoorChanges = False
    for ProxSensor in ProxColumns:
        if (DoorChanges == True):
            continue
        elif (DataToAnalyse[ProxSensor].sum() == 0) | (DataToAnalyse[ProxSensor].sum() == N_points):
            DoorChanges = False
        else:
            DoorChanges = True
    return(DoorChanges)

def AnyDoorChangesHobo(ProxData, FDData, CloseTimeIndex):
    StartTime = FDData['DateTime'].iloc[CloseTimeIndex]
    EndTime = FDData['DateTime'].iloc[CloseTimeIndex+1]
    SubsetProxData = SubsetDataByTime(ProxData, StartTime, EndTime)
##    print(StartTime, EndTime)
##    print(SubsetProxData)
    if len(SubsetProxData) == 0:
        DoorChanges = False
    elif len(SubsetProxData) > 0:
        DoorChanges = True
    return(DoorChanges)



def AnyGradientOverThreshold(InputData, CO2Columns, ThresholdGradient =20):
    GradientOverThreshold = False
    for CO2Sensor in CO2Columns:
        if GradientOverThreshold == True:
            continue
        else:
            #print(CO2Sensor, N.gradient(InputData[CO2Sensor], (1/12)))
            if (N.gradient(InputData[CO2Sensor],(1/12))>ThresholdGradient).any():
                #print(CO2Sensor, N.nanmax(N.gradient(InputData[CO2Sensor], (1/12))), ThresholdGradient)
##                print((N.gradient(InputData[CO2Sensor],(1/12))>ThresholdGradient).any())
##                print((N.gradient(InputData[CO2Sensor],(1/12))))
                #print(InputData[CO2Sensor])
                GradientOverThreshold = True
    return(GradientOverThreshold)


def FindDataForGradientAssessment(InputData, CO2Columns, nAveragingPoints = 3):
    SmoothedCO2 = InputData.loc[:,CO2Columns].rolling(window=nAveragingPoints,center=True).mean()
    #print(SmoothedCO2)
    if len(InputData)> 11:
        StartIndexPos = InputData.index[0]
        GradientFunctionData = SmoothedCO2.loc[StartIndexPos+5:,:]
    else:
        GradientFunctionData = SmoothedCO2.copy()
    return GradientFunctionData

def MakeOccupancyMaskForCO2Cols(OccupancyMask, CO2Columns):
    CO2OccDict = {}
    for CO2Sensor in CO2Columns:
        CO2OccDict[CO2Sensor] = OccupancyMask['Occupied']

    CO2OccupancyMask = pd.DataFrame(CO2OccDict)
    return CO2OccupancyMask

def MakeMaskForCO2Cols(FrameToCopy, NameOfColToCopy, CO2Columns):
    CO2OccDict = {}
    for CO2Sensor in CO2Columns:
        CO2OccDict[CO2Sensor] = FrameToCopy[NameOfColToCopy]

    CO2Mask = pd.DataFrame(CO2OccDict)
    return CO2Mask

        

def FindOccupiedTimes(InputData, FrontDoorData, CO2Columns, Prox, ThresholdGradient, nAveragingPoints = 3, PlotResults = True, CaseStudy = 'PR2019'):

    OccupancyMask = pd.DataFrame(data = InputData['DateTime']) # create dataframe for the occupancy mask
    OccupancyMask.loc[:,'Occupied']= False # initialise with always unoccupied

    InputTimeIndex = pd.Index(InputData['DateTime'])

    for CloseTimeIndex in N.where(FrontDoorData['State']== 0.0)[0]: # loop over all the times the front door closed
        if CloseTimeIndex+1 == len(FrontDoorData): # if looking at the final time the door closed, quit the loop.
            continue
        else:
            t0, t1 = FindTimesBetweenDoorChanges(FrontDoorData, CloseTimeIndex, InputTimeIndex) # t0 is the time the front door closed, t1 is the next time the front door opened
##            print(t0, t1)
##            print(CloseTimeIndex)
            if isinstance(Prox, pd.DataFrame): # if the internal doors are monitored by Hobos doing event monitoring, rather than eltek doing state monitoring
                DoorChanges = AnyDoorChangesHobo(Prox, FrontDoorData, CloseTimeIndex)
                if DoorChanges: # if any of the monitored doors changed state (door changes = true)
                   OccupancyMask.loc[(OccupancyMask['DateTime'] > t0) & (OccupancyMask['DateTime'] <= t1), 'Occupied'] = DoorChanges
##                   print('Hobo Door changes identified')
            if ((t1-t0).total_seconds() > 600):
                DataBetweenDoorClosings = SubsetDataByTime(InputData,t0, t1)
                if len(DataBetweenDoorClosings) > 2: 
                    if isinstance(Prox, list):
                        CleanedProxData = CleanNaNsinProxData(DataBetweenDoorClosings, Prox)
                        DoorChanges = AnyDoorChangesEltek(CleanedProxData, Prox)
                                            
                    if (DoorChanges == True):
                        OccupancyMask.loc[(OccupancyMask['DateTime'] > t0) & (OccupancyMask['DateTime'] <= t1), 'Occupied'] = DoorChanges
##                        print('Door changes identfied')
                if len(DataBetweenDoorClosings) > 4:
                    if not DoorChanges:
                        #print(N.gradient(DataBetweenDoorClosings[CO2Columns], (1/12)))
                        GradientFunctionData = FindDataForGradientAssessment(DataBetweenDoorClosings, CO2Columns, nAveragingPoints)
                        GradientOverThresh = AnyGradientOverThreshold(GradientFunctionData, CO2Columns, ThresholdGradient)
                        if (GradientOverThresh == True):
                            OccupancyMask.loc[(OccupancyMask['DateTime'] > t0) & (OccupancyMask['DateTime'] <= t1), 'Occupied'] = GradientOverThresh
##                            print('Gradient over threshold')
                        else: 
                            OccupancyMask.loc[(OccupancyMask['DateTime'] > t0) & (OccupancyMask['DateTime'] < t1), 'Occupied'] = False

    OccupancyMask.loc[:,'Occupied'] = (OccupancyMask.loc[:,'Occupied']) | ((SetFDStateChangesOccupied(FrontDoorData, OccupancyMask, InputTimeIndex)).loc[:,'Occupied']) # Also set the mask occupied whenever the front door state changes: someone had to open it.
    CO2OccupancyMask = MakeOccupancyMaskForCO2Cols(OccupancyMask, CO2Columns)
    if PlotResults:
        PlotCO2AndDoorSensorsOccupancy(InputData, CO2OccupancyMask, CO2Columns, Prox, FrontDoorData, CaseStudy)


    return(OccupancyMask)

def FindNearestTimeInColumn(TimeColumn, ReferenceTime):
    return min(TimeColumn, key = lambda x: abs(x-ReferenceTime))
               
def CompareAlgorithmReportedEndOfOccupancy(ReportedEndTimes, FrontDoorTimes, OccupancyMask, TimeOffset=5):

    AlgorithmReportedOccupancyEndTimeComparison = pd.DataFrame(data = ReportedEndTimes)
    AlgorithmReportedOccupancyEndTimeComparison['PreviouslyOccupied'] = False
    AlgorithmReportedOccupancyEndTimeComparison['SubsequentlyUnoccupied'] = False

    IndexZero= ReportedEndTimes.index[0]
    
    for Index in N.arange(IndexZero, len(ReportedEndTimes)+IndexZero):
        ReportedEndTime = ReportedEndTimes[Index]
        NearestFrontDoorTime = FindNearestTimeInColumn(FrontDoorTimes, ReportedEndTime)
##        NearestEltekTime = FindNearestEltekTime(NearestFrontDoorTime)
####        NearestEltekTime = FindNearestTimeInColumn(OccupancyMask['DateTime'], NearestFrontDoorTime)
        EltekTimeAfterDoor = FindEltekTime(NearestFrontDoorTime) + datetime.timedelta(minutes = 5)
        PreviousTimeStep = EltekTimeAfterDoor + datetime.timedelta(minutes = -TimeOffset)
        NextTimeStep = EltekTimeAfterDoor + datetime.timedelta(minutes = TimeOffset)
##        PreviousTimeStep = NearestEltekTime + datetime.timedelta(minutes = -TimeOffset)
##        NextTimeStep = NearestEltekTime + datetime.timedelta(minutes = TimeOffset)

        if (len(OccupancyMask[OccupancyMask['DateTime']==PreviousTimeStep])==0) | (len(OccupancyMask[OccupancyMask['DateTime']==NextTimeStep])==0):
            continue
        else:
            AlgorithmReportedOccupancyEndTimeComparison['PreviouslyOccupied'].loc[Index] = OccupancyMask.loc[OccupancyMask['DateTime']==PreviousTimeStep, 'Occupied'].values[0]
            AlgorithmReportedOccupancyEndTimeComparison['SubsequentlyUnoccupied'].loc[Index] = not OccupancyMask.loc[OccupancyMask['DateTime']==NextTimeStep, 'Occupied'].values[0]

    return AlgorithmReportedOccupancyEndTimeComparison


def CompareAlgorithmReportedStartOfOccupancy(ReportedStartTimes, FrontDoorTimes, OccupancyMask, TimeOffset = 5):

    AlgorithmReportedOccupancyStartTimeComparison = pd.DataFrame(data = ReportedStartTimes)
    AlgorithmReportedOccupancyStartTimeComparison['PreviouslyUnoccupied'] = False
    AlgorithmReportedOccupancyStartTimeComparison['SubsequentlyOccupied'] = False

    IndexZero= ReportedStartTimes.index[0]
    
    for Index in N.arange(IndexZero, len(ReportedStartTimes)+IndexZero):
        ReportedStartTime = ReportedStartTimes[Index]
        NearestFrontDoorTime = FindNearestTimeInColumn(FrontDoorTimes, ReportedStartTime)
        #NearestEltekTime = FindNearestTimeInColumn(OccupancyMask['DateTime'], NearestFrontDoorTime)
##        NearestEltekTime = FindNearestEltekTime(NearestFrontDoorTime)
        
        EltekTimeAfterDoor = FindEltekTime(NearestFrontDoorTime) + datetime.timedelta(minutes = 5)
        PreviousTimeStep = EltekTimeAfterDoor + datetime.timedelta(minutes = -TimeOffset)
        NextTimeStep = EltekTimeAfterDoor + datetime.timedelta(minutes = TimeOffset)
##        PreviousTimeStep = NearestEltekTime + datetime.timedelta(minutes = -TimeOffset)
##        NextTimeStep = NearestEltekTime + datetime.timedelta(minutes = TimeOffset)

        if (len(OccupancyMask[OccupancyMask['DateTime']==PreviousTimeStep])==0) | (len(OccupancyMask[OccupancyMask['DateTime']==NextTimeStep])==0):
            continue
        else:
            AlgorithmReportedOccupancyStartTimeComparison['PreviouslyUnoccupied'].loc[Index] = not OccupancyMask.loc[OccupancyMask['DateTime']==PreviousTimeStep, 'Occupied'].values[0]
            AlgorithmReportedOccupancyStartTimeComparison['SubsequentlyOccupied'].loc[Index] = OccupancyMask.loc[OccupancyMask['DateTime']==NextTimeStep, 'Occupied'].values[0]

    return AlgorithmReportedOccupancyStartTimeComparison

