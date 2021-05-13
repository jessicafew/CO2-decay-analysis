import pandas as pd
from PlotFunctions import *

def SubsetDataByTime(DataFrame, StartTime, EndTime):
    '''Function for subsetting monitoring data in DataFrame to between two datetimes. NB does not include edges.'''

    # Convert datetime variables to timestamps.
    StartTime = pd.DatetimeIndex([StartTime])[0]
    EndTime = pd.DatetimeIndex([EndTime])[0]

    SubsetData = DataFrame.loc[(DataFrame['DateTime'] > StartTime) & (DataFrame['DateTime'] < EndTime)]

    return SubsetData


def SubsetDataByAnyDecay(InputData, ProxSplitDecayPeriods):
    AnyDecayTimes = ProxSplitDecayPeriods.any(1)
    return AnyDecayTimes


def SubsetByInferredOccupancy(InputData, OccupancyPeriods):
    '''Return data frame with data only during occupied periods, unoccupied periods are filled with NaNs'''
    OccupiedData = pd.DataFrame(index = range(OccupancyPeriods.index[0], OccupancyPeriods.index[-1]), columns = InputData.columns)
    for ColumnName in InputData.columns:
        OccupiedData[ColumnName] = InputData[ColumnName][OccupancyPeriods]
    OccupiedData['DateTime'] = InputData['DateTime']
    OccupiedData = OccupiedData.loc[(OccupiedData['DateTime'] >= InputData['DateTime'].iloc[0]) & (OccupiedData['DateTime'] <= InputData['DateTime'].iloc[-1])]

    return OccupiedData


def SubsetByInferredUnoccupancy(InputData, OccupancyPeriods):
    '''Return data frame with data only during unoccupied periods, occupied periods are filled with NaNs'''
    UnoccupiedData = pd.DataFrame(index = range(OccupancyPeriods.index[0], OccupancyPeriods.index[-1]), columns = InputData.columns)
    for ColumnName in InputData.columns:
        UnoccupiedData[ColumnName] = InputData[ColumnName][~OccupancyPeriods]
    UnoccupiedData['DateTime'] = InputData['DateTime']
    UnoccupiedData = UnoccupiedData.loc[(UnoccupiedData['DateTime'] >= InputData['DateTime'].iloc[0]) & (UnoccupiedData['DateTime'] <= InputData['DateTime'].iloc[-1])]

    return UnoccupiedData
