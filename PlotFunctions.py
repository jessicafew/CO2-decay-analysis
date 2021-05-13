import numpy as N
import pandas as pd
import os
import matplotlib.pyplot as pyplot
import matplotlib.dates
import datetime
import LegendListGeneral
from pylab import date2num
    


def PlotHistVR_BarConfig(ResultsFrame, ConfigData, CaseStudy, CO2Columns):
    #ConfigData = ConfigData[ConfigData['AllTimeProportion']>0.035]# Don't plot configs which the flat spent less than 5% total time in.
    ConfigData = ConfigData.sort_values('AllTimeProportion', ascending = False)
    N_Rows = len(ConfigData)
    MaxVR = ResultsFrame['DecayConstHours'].max()

    TitleDict = {'WO: LivWLHLivWMBedW DO: All': 'WO: LivL-LivM-Bed; DO: All', 'WO: BedW DO: All':'WO: Bed; DO: All',
                 'WO: None  DO: All':'WO: None; DO: All', 'WO: LivWRHBedW DO: All':'WO: LivR-Bed; DO: All',
                 'WO: LivWLHBedW DO: All':'WO: LivL-Bed; DO: All','WO: All  DO: All':'WO: All; DO: All',
                 'WO: LivWLH DO: All':'WO: LivL; DO: All', 'WO: None  DO: LivDBathD':'WO: None; DO: Liv-Bath',
                 'WO: KitW DO: All': 'WO: Kit; DO: All', 'WO: LivWRH DO: All':'WO: LivR; DO: All',
                 'WO: None  DO: None':'WO: None; DO: None'}
    
    #MaxProportion = ConfigData[['OccupiedProportion', 'UnoccupiedProportion', 'ProportionDecays']].max().max()
    pyplot.figure()
    ydata, xdata, histbins = pyplot.hist(ResultsFrame['DecayConstHours'][ResultsFrame['Config']== ConfigData['Legend'].iloc[0]], bins = N.arange(0,MaxVR+0.1,0.1))
    MaxHistHeight = ydata.max()
    pyplot.close()

    
    pyplot.set_cmap('viridis')
    cmap = pyplot.cm.viridis
    CMapVals = [cmap(0),cmap(0.3),cmap(0.6), cmap(0.9)]
    fig= pyplot.figure(figsize=(7,0.5+N_Rows), dpi=100)
    for n in N.arange(1,N_Rows+1):

#	# barplots of proportions of time in different configs + proportions of decays
        y_pos = (1/(2*(N_Rows+0.5))) + (0/(20*(N_Rows+0.5))) + ((N_Rows-n)/(N_Rows+0.5))
        ax = fig.add_axes([0.14,y_pos,0.4, (0.75/(N_Rows+0.5))])
        ax.set_xlim([0,1])
        ax.grid(axis = 'x', zorder=-10)
        ax.set_xticks(N.arange(0,1,0.2))
        ax.set_xticklabels([])
        ax.set_yticks(N.arange(0,4,1))
        ax.set_yticklabels(['', 'Occupied', 'Unoccupied', 'Decays'])
        ax.set_ylim([0.5,3.6])
        ax.barh([1,2,3], [ConfigData.iloc[n-1]['OccupiedProportion'], ConfigData.iloc[n-1]['UnoccupiedProportion'], ConfigData.iloc[n-1]['ProportionDecays']], color= CMapVals)
        print(ConfigData.iloc[n-1]['Legend'])
        ax.text(0.7,1.2, (TitleDict[ConfigData.iloc[n-1]['Legend']]), transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left')
        if n == N_Rows:
            ax.set_xticklabels(N.arange(0,1.1, 0.2))
            ax.get_xaxis().set_ticks(N.arange(0,1.1, 0.2))
            ax.set_xlabel('Proportion')
 
        # histograms of decay rates in those configurations
        ax = fig.add_axes([0.59,y_pos,0.4, (0.75/(N_Rows+1))])
        ax.set_ylim([0,MaxHistHeight+1])
        ax.set_xlim([0,MaxVR+0.1])
        if (len(CO2Columns)==1):
            ax.hist(ResultsFrame['DecayConstHours'][ResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]],
                    bins = N.arange(0,MaxVR+0.1,0.1), color = CMapVals[2])


        else:
            i=0
            for Sensor in CO2Columns:
                SensorResultsFrame = ResultsFrame[ResultsFrame['CO2Sensor']== Sensor]
                ax.hist(SensorResultsFrame['DecayConstHours'][SensorResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]],
                    bins = N.arange(0,MaxVR+0.1,0.1), alpha = 0.5, color = CMapVals[i])
                i=i+1
            CO2RoomLegend = LegendListGeneral.FindLegendList(CO2Columns, CaseStudy)
            ax.legend(CO2RoomLegend)
        
        ax.grid(axis = 'x', zorder=-10)
        ax.set_xticks(N.arange(0,MaxVR+0.1,0.5))
        pyplot.locator_params(axis = 'y', nbins = 3)
        ax.set_yticks([0, MaxHistHeight])
        ax.set_xticklabels([])
        Mean = (ResultsFrame['DecayConstHours'][ResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]]).mean()
        Number = (ResultsFrame['Config']==ConfigData['Legend'].iloc[n-1]).sum()
        NOver05 = ((ResultsFrame['DecayConstHours'][ResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]])<0.5).sum()
        if Number>0:
            Percentage = (NOver05/Number)*100
            Median = (ResultsFrame['DecayConstHours'][ResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]]).median()
            BoxText = 'N = ' + str(Number) + '\nMedian= '+ ('%0.2f'%Median) + '\n% < 0.5 = ' + ('%0.1f'%Percentage)+'%'
        else:
            BoxText = 'N = ' + str(Number) + '\nMedian= N/A'+ '\n% < 0.5 = N/A'
#        ax.text(0.6,0.95, ('Mean= ' + ('%0.2f'%Mean) + '\nMedian= '+ ('%0.2f'%Median)), transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))
        ax.text(0.5,0.9, BoxText,
        transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))
#        ax.get_yaxis().set_visible(False)
        if n == N_Rows:
            ax.get_xaxis().set_visible(True)
            ax.get_xaxis().set_ticks(N.arange(0,MaxVR+0.1, 0.5))
            ax.set_xticklabels(N.arange(0,MaxVR+0.1, 0.5))
            ax.set_xlabel('Whole House Decay Rate (1/h)')

    pyplot.show()
     

def PlotHistVR_BarConfig_HistDist(ResultsFrame, ConfigData, EnvData, CaseStudy, CO2Columns):
    from matplotlib.lines import Line2D
    from scipy.stats import mannwhitneyu
#    ConfigData = ConfigData[ConfigData['AllTimeProportion']>0.035]# Don't plot configs which the flat spent less than 5% total time in.
    ConfigData = ConfigData[ConfigData['AllTimeProportion']>0.005]# Don't plot configs which the flat spent less than 5% total time in.
    ConfigData = ConfigData.sort_values('AllTimeProportion', ascending = False)
    N_Rows = len(ConfigData)
    if N_Rows>4:
        N_Rows=4
    MaxVR = ResultsFrame['DecayConstHours'].max()
    MaxTDiff = EnvData['TDiff'].max()
    MinTDiff = EnvData['TDiff'].min()
    MaxWindSp = EnvData['WindSpMidas'].max()
    MinWindSp = EnvData['WindSpMidas'].min()
    MaxWindDir = EnvData['WindDirMidas'].max()
    MinWindDir = EnvData['WindDirMidas'].min()
    

    TitleDict = {'WO: LivWLHLivWMBedW DO: All': 'WO: LivL-LivM-Bed; DO: All', 'WO: BedW DO: All':'WO: Bed; DO: All',
                 'WO: None  DO: All':'WO: None; DO: All', 'WO: LivWRHBedW DO: All':'WO: LivR-Bed; DO: All',
                 'WO: LivWLHBedW DO: All':'WO: LivL-Bed; DO: All','WO: All  DO: All':'WO: All; DO: All',
                 'WO: LivWLH DO: All':'WO: LivL; DO: All', 'WO: None  DO: LivDBathD':'WO: None; DO: Liv-Bath',
                 'WO: KitW DO: All': 'WO: Kit; DO: All', 'WO: LivWRH DO: All':'WO: LivR; DO: All',
                 'WO: None  DO: None':'WO: None; DO: None','WO: LivWLHLivWM DO: All':'WO: LivL-LivM; DO: All',
                 'WO: None  DO: LivDBedD':'WO: None; DO: Liv-Bed', 'WO: LivWLHLivWMBedW DO: LivDBedD':'WO: LivL-LivM-Bed; DO: Liv-Bed', 
                 'WO: All  DO: LivDBedD': 'WO: All; DO: Liv-Bed', 'WO: LivWLHLivWMBedW DO: BedDBathD': 'WO: LivL-LivM-Bed; DO: Bed-Bath',
                 'WO: BedW DO: LivDBedD': 'WO: Bed; DO: LivD-Bed', 'WO: LivWLH DO: LivDBedD': 'WO: LivL; DO:Liv-Bed',
                 'WO: LivWRH DO: LivDBedD':'WO:LivR; DO: Liv-Bed', 'WO: BedW DO: None':'WO: Bed; DO: None', 'WO: All  DO: None': 'WO: All; DO: None',
                 'WO: LivWLHLivWRH DO: All':'WO: LivL-LivR; DO: All', 'WO: LivWLHLivWRH DO: None':'WO: LivL-LivR; DO: None',
                 'WO: LivWRHBedW DO: None':'WO: LivR-Bed; DO: None'}
    
    #MaxProportion = ConfigData[['OccupiedProportion', 'UnoccupiedProportion', 'ProportionDecays']].max().max()
    pyplot.figure()
    ydata, xdata, histbins = pyplot.hist(ResultsFrame['DecayConstHours'][ResultsFrame['Config']== ConfigData['Legend'].iloc[0]], bins = N.arange(0,MaxVR+0.1,0.1))
    MaxHistHeight = ydata.max()
    pyplot.close()
    
    pyplot.set_cmap('viridis')
    cmap = pyplot.cm.viridis
    CMapVals = [cmap(0),cmap(0.3),cmap(0.6), cmap(0.9)]
    fig= pyplot.figure(figsize=(14,0.5+N_Rows*1.2), dpi=100)
    for n in N.arange(1,N_Rows+1):
        # Subset the environmental data according to the configuration
        EnvDataSubset = EnvData[EnvData['Config']== ConfigData.iloc[n-1]['Legend']]
        ResultsSubset = ResultsFrame[ResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]]
#	# barplots of proportions of time in different configs + proportions of decays
        y_pos = (1/(2*(N_Rows+0.5))) + (0/(20*(N_Rows+0.5))) + ((N_Rows-n)/(N_Rows+0.5))
        ax = fig.add_axes([0.07,y_pos,0.16, (0.75/(N_Rows+1))])
        ax.set_xlim([0,1])
        ax.grid(axis = 'x', zorder=-10)
        ax.set_xticks(N.arange(0,1,0.2))
        ax.set_xticklabels([])
        ax.set_yticks(N.arange(0,4,1))
        ax.set_yticklabels(['', 'Occupied', 'Unoccupied', 'Decays'])
        ax.set_ylim([0.5,3.6])
        ax.barh([1,2,3], [ConfigData.iloc[n-1]['OccupiedProportion'], ConfigData.iloc[n-1]['UnoccupiedProportion'], ConfigData.iloc[n-1]['ProportionDecays']], color= CMapVals)
        ax.text(2.3,1.2, (TitleDict[ConfigData.iloc[n-1]['Legend']]), transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', fontsize = 13)
        if n == N_Rows:
            ax.set_xticklabels(N.arange(0,1.1, 0.2))
            ax.get_xaxis().set_ticks(N.arange(0,1.1, 0.2))
            ax.set_xlabel('Proportion')
 
        # histograms of decay rates in those configurations
        x_pos2 = 0.07+0.186
        ax = fig.add_axes([x_pos2,y_pos,0.16, (0.75/(N_Rows+1))])
        ax.set_ylim([0,MaxHistHeight+1])
        ax.set_xlim([0,MaxVR+0.1])
        if (len(CO2Columns)==1):
            ax.hist(ResultsSubset['DecayConstHours'],
                    bins = N.arange(0,MaxVR+0.1,0.1), color = CMapVals[2])


            #ax.plot([0.5,0.5], [0,MaxHistHeight+1], color = '0.6', ls='--', zorder = -1)
        else:
            i=0
            for Sensor in CO2Columns:
                SensorResultsFrame = ResultsSubset[ResultsSubset['CO2Sensor']== Sensor]
##                print(SensorResultsFrame)
##                Sensor_heights, SensorBins = N.histogram(SensorResultsFrame['DecayConstHours'][SensorResultsFrame['Config']==ConfigData['Legend'].iloc[n-1]], bins = N.arange(0,MaxVR+0.1,0.1))
##                BarWidth = (SensorBins[1]-SensorBins[0])/(len(CO2Columns)+1)
##                ax.bar(SensorBins[:-1]+BarWidth*i, Sensor_heights, width = BarWidth)
##                i=i+1
                ax.hist(SensorResultsFrame['DecayConstHours'][SensorResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]],
                    bins = N.arange(0,MaxVR+0.1,0.1), alpha = 0.5, color = CMapVals[i])
                i=i+1
            CO2RoomLegend = LegendListGeneral.FindLegendList(CO2Columns, CaseStudy)
            ax.legend(CO2RoomLegend)
        
        ax.grid(axis = 'x', zorder=-10)
        ax.set_xticks(N.arange(0,MaxVR+0.1,0.5))
        pyplot.locator_params(axis = 'y', nbins = 3)
        ax.set_yticks([0, MaxHistHeight])
        Mean = ResultsSubset['DecayConstHours'].mean()
        Number = len(ResultsSubset['Config'])
        NOver05 = ((ResultsSubset['DecayConstHours'])<0.5).sum()
        if Number>0:
            Percentage = (NOver05/Number)*100
            Median = (ResultsFrame['DecayConstHours'][ResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]]).median()
            BoxText = 'N = ' + str(Number) + '\nMedian= '+ ('%0.2f'%Median) + '\n% < 0.5 = ' + ('%0.1f'%Percentage)+'%'
        else:
            BoxText = 'N = ' + str(Number) + '\nMedian= N/A'+ '\n% < 0.5 = N/A'
#        ax.text(0.6,0.95, ('Mean= ' + ('%0.2f'%Mean) + '\nMedian= '+ ('%0.2f'%Median)), transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))
        ax.text(0.4,0.9, BoxText,
            transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))
#        ax.get_yaxis().set_visible(False)
        ax.set_xticklabels([])
        if n == N_Rows:
            ax.get_xaxis().set_visible(True)
            ax.get_xaxis().set_ticks(N.arange(0,MaxVR+0.1, 0.5))
            ax.set_xticklabels(N.arange(0,MaxVR+0.1, 0.5))
            ax.set_xlabel('Whole House Decay Rate (ach)')


        x_pos3 = 0.07+0.186*2
        ax = fig.add_axes([x_pos3,y_pos,0.15, (0.75/(N_Rows+1))])
        ax.set_xlim([int(MinTDiff)-1, int(MaxTDiff)+1])
        ax.hist(EnvDataSubset['TDiff'].dropna(), bins = N.arange(int(MinTDiff), int(MaxTDiff), 1),
                color = CMapVals[0], alpha = 0.6, normed= True)
        ax.hist(ResultsFrame['TDiff'][ResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]],
                bins = N.arange(int(MinTDiff), int(MaxTDiff), 1), color = CMapVals[2], alpha = 0.7, normed = True)
        ax.grid(axis = 'x', zorder=-10)
        ax.get_xaxis().set_ticks(N.arange(int(MinTDiff), int(MaxTDiff)+1, 4))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_yticks([])
        print(ConfigData['Legend'].iloc[n-1] + 'results: ' +str((ResultsFrame['TDiff'][ResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]]).median()) + ' occupied: ' + str(EnvDataSubset['TDiff'].dropna().median()))

        if len(ResultsSubset) > 15:
            stat, p = mannwhitneyu(EnvDataSubset['TDiff'].dropna(), ResultsSubset['TDiff'].dropna(), alternative = 'two-sided')
            ax.text(0.7,0.9, 'P= ' + ('%0.2f'%p),
                transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))
##            else:
##                ax.legend(title = 'P not calculated', framealpha = 0.5, loc = 'upper right')


        if n == N_Rows:
            ax.get_xaxis().set_visible(True)
            ax.get_xaxis().set_ticks(N.arange(int(MinTDiff), int(MaxTDiff)+1, 4))
            ax.set_xticklabels(N.arange(int(MinTDiff), int(MaxTDiff)+1, 4))
            ax.set_xlabel('Temperature Difference (ºC)')



        x_pos4 = 0.07+0.186*3
        ax = fig.add_axes([x_pos4,y_pos,0.15, (0.75/(N_Rows+1))])
        ax.set_xlim([int(MinWindSp), int(MaxWindSp)+1])
        ax.hist(EnvDataSubset['WindSpMidas'].dropna(), bins = N.arange(int(MinWindSp), int(MaxWindSp), 2),
                color = CMapVals[0], alpha = 0.6, normed= True)
        ax.hist(ResultsFrame['WindSpMidas'][ResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]].dropna(),
                bins = N.arange(int(MinWindSp), int(MaxWindSp), 2), color = CMapVals[2], alpha = 0.7, normed = True)
        ax.grid(axis = 'x', zorder=-10)
        ax.get_xaxis().set_ticks(N.arange(int(MinWindSp), int(MaxWindSp)+1, 6))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_yticks([])
        

        if n==1:
            if len(ResultsSubset) > 15:
                stat, p = mannwhitneyu(EnvDataSubset['WindSpMidas'].dropna(), ResultsSubset['WindSpMidas'].dropna(), alternative = 'two-sided')
                #ax.legend(['Occupied', 'Decay'], title = 'P= ' + ('%0.2f'%p), framealpha = 0.5, loc = 'upper right')
                ax.legend(['Occupied conditions', 'Measurement conditions'], loc='upper center', bbox_to_anchor=(1, 1.5), ncol=2)
                ax.text(0.7,0.9, 'P= ' + ('%0.2f'%p),
                    transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))


            else:
                #ax.legend(['Occupied', 'Decay'], framealpha = 0.5, loc = 'upper right')
                ax.legend(['Occupied conditions', 'Measurement conditions'], loc='upper center', bbox_to_anchor=(1, 1.5), ncol=2)
                ax.text(0.7,0.9, 'P= ' + ('%0.2f'%p),
                    transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))


            
        else:
            if len(ResultsSubset) > 15:
                stat, p = mannwhitneyu(EnvDataSubset['WindSpMidas'].dropna(), ResultsSubset['WindSpMidas'].dropna(), alternative = 'two-sided')
                ax.text(0.7,0.9, 'P= ' + ('%0.2f'%p),
                    transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))

        if n == N_Rows:
            ax.get_xaxis().set_visible(True)
            ax.get_xaxis().set_ticks(N.arange(int(MinWindSp), int(MaxWindSp)+1, 6))
            ax.set_xticklabels(N.arange(int(MinWindSp), int(MaxWindSp)+1, 6))
            ax.set_xlabel('Wind Speed (Knots)')

        x_pos5 = 0.07+0.186*4
        ax = fig.add_axes([x_pos5,y_pos,0.15, (0.75/(N_Rows+1))])
        ax.set_xlim(0,360)
        ax.hist(EnvDataSubset['WindDirMidas'].dropna(), bins = N.arange(0,360,20),
                color = CMapVals[0], alpha = 0.6, normed= True)
        ax.hist(ResultsFrame['WindDirMidas'][ResultsFrame['Config']== ConfigData['Legend'].iloc[n-1]].dropna(),
                bins = N.arange(0,360,20), color = CMapVals[2], alpha = 0.7, normed = True)
        ax.grid(axis = 'x', zorder=-10)
        ax.get_xaxis().set_ticks(N.arange(0, 360, 90))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_yticks([])
        
        if len(ResultsSubset) > 15:
            stat, p = mannwhitneyu(N.sin(EnvDataSubset['WindDirMidas'].dropna()), N.sin(ResultsSubset['WindDirMidas'].dropna()), alternative = 'two-sided')
            ax.text(0.7,0.9, 'P= ' + ('%0.2f'%p),
                transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))

        
        if n == N_Rows:
            ax.get_xaxis().set_visible(True)
            ax.get_xaxis().set_ticks(N.arange(0, 360, 90))
            ax.set_xticklabels(N.arange(0, 360, 90))
            ax.set_xlabel('Wind Direction')
    pyplot.show()


def PlotIdentifyDecayCurvesDifferentSmoothing(InputData, CO2Columns, RawDecayPeriods1, DecayStartPositions1,
                            DecayEndPositions1, nAveragingPoints1, RawDecayPeriods2, DecayStartPositions2,
                            DecayEndPositions2, nAveragingPoints2, CaseStudy, AllData = None, OccupiedData = None):

    pyplot.rcParams.update({'font.size': 16})
    pyplot.figure(figsize=(8,4.0))
    if isinstance(AllData, pd.DataFrame):
        if CaseStudy == 'Loughborough':
            AllCO2Columns = ['CO2D','CO2E', 'CO2A', 'CO2C']
        elif CaseStudy == '2D':
            AllCO2Columns = ['CO2A','CO2B', 'CO2C']
        elif CaseStudy == '2A':
            AllCO2Columns = ['CO2A','CO2B', 'CO2C', 'CO2D']
        else:
            AllCO2Columns = CO2Columns
        pyplot.plot(AllData['DateTime'], AllData[AllCO2Columns], color = 'gainsboro', ls='-')
        pyplot.plot(AllData['DateTime'], AllData[CO2Columns], color = 'grey', ls='-')


    AveragedCO2Data1 =  AllData[CO2Columns].rolling(window=nAveragingPoints1,center=True).mean()
    AveragedCO2Data2 =  AllData[CO2Columns].rolling(window=nAveragingPoints2,center=True).mean()

    pyplot.set_cmap('viridis')
    cmap = pyplot.cm.viridis
    CMapVals = [0.1,0.4,0.7]
    pyplot.plot(InputData['DateTime'], AveragedCO2Data1[RawDecayPeriods1], color = cmap(0))
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns][DecayStartPositions1], color = cmap(0), marker = 'v', ls = 'None')
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns][DecayEndPositions1], color = cmap(0), marker = 'v', ls = 'None')

    pyplot.plot(InputData['DateTime'], AveragedCO2Data2[RawDecayPeriods2], color = cmap(0.5))
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns][DecayStartPositions2], color = cmap(0.5), marker = '^', ls = 'None')
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns][DecayEndPositions2], color = cmap(0.5), marker = '^', ls = 'None')

    from matplotlib.lines import Line2D # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html
    custom_lines = [Line2D([0], [0], color='gainsboro', lw=2),
                Line2D([0], [0], color='grey', lw=2),
                Line2D([0], [0], color=cmap(0), lw=2),
                Line2D([0], [0], color=cmap(0.5), lw=2),
                Line2D([0], [0], marker='v', color='k')]

    pyplot.legend(custom_lines, (['All CO$_2$ sensors', 'Mean $\Delta$CO$_2$', '3 point smoothing decays', '5 point smoothing decays', 'Decay start and end points']))

    
    pyplot.grid(axis='y')
    pyplot.ylabel('$\Delta$CO$_2$ (ppm)')
    pyplot.xlabel('Time')
    #pyplot.legend(LegendList)
    ax = pyplot.gca()
    xfmt = matplotlib.dates.DateFormatter('%H:%M')#'%m-%d') #%H')
    ax.xaxis.set_major_formatter(xfmt)
    pyplot.tight_layout() # top stop overlap of text as much as possible
    pyplot.show()


    
def PlotIdentifyDecayCurves(InputData, CO2Columns, RawDecayPeriods, DecayStartPositions,
                            DecayEndPositions, nAveragingPoints, CaseStudy, AllData = None, OccupiedData = None):
    '''Plot the CO2 data with the identified decay curves in black.'''
    
    AveragedCO2Data =  InputData[CO2Columns].rolling(window=nAveragingPoints,center=True).mean()
    pyplot.rcParams.update({'font.size': 16})

    pyplot.set_cmap('viridis')
    cmap = pyplot.cm.viridis
    pyplot.figure(figsize=(8,4.0))
    if isinstance(AllData, pd.DataFrame):
        if CaseStudy == 'Loughborough':
            AllCO2Columns = ['CO2D','CO2E', 'CO2A', 'CO2C']
        elif CaseStudy == '2D':
            AllCO2Columns = ['CO2A','CO2B', 'CO2C']
        elif CaseStudy == '2A':
            AllCO2Columns = ['CO2A','CO2B', 'CO2C', 'CO2D']
        else:
            AllCO2Columns = CO2Columns
        pyplot.plot(AllData['DateTime'], AllData[AllCO2Columns], color = 'gray', ls='-')
        #pyplot.plot(AllData['DateTime'], AllData['CO2C'], color = 'c', ls='-')
        #pyplot.plot(AllData['DateTime'], AllData[CO2Columns].rolling(window=nAveragingPoints,center=True).mean(), color = 'darkgrey', ls='--')
    if isinstance(OccupiedData, pd.DataFrame):
        pyplot.plot(OccupiedData['DateTime'], OccupiedData[AllCO2Columns], color = 'gainsboro', ls='-')
        #pyplot.plot(OccupiedData['DateTime'], OccupiedData[CO2Columns].rolling(window=nAveragingPoints,center=True).mean(), color = 'lightgrey', ls='--')
    pyplot.plot(InputData['DateTime'], AveragedCO2Data, color = 'black', ls=':')
    # uncomment next line to show homogeneous periods with black dots.
    #pyplot.plot(InputData['DateTime'], AveragedCO2Data, color = 'black', marker= '.', ls='None')

    pyplot.plot(InputData['DateTime'], InputData[CO2Columns][RawDecayPeriods], 'k')
    #pyplot.plot(InputData['DateTime'], AveragedCO2Data[RawDecayPeriods], 'k')
    # uncomment next line for dotted line at 0∆CO2. 
    #pyplot.plot([InputData['DateTime'][~InputData['DateTime'].isnull()].iloc[0], InputData['DateTime'][~InputData['DateTime'].isnull()].iloc[-1]], [0,0], ls = ':', color = '0.8')
    # Run the following two lines put markers on the plot at the start and end points of the decay curve
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns][DecayStartPositions], color =cmap(0.6), marker = '^', ls = 'None', markersize = 10)
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns][DecayEndPositions], color = cmap(0.6), marker = 'v', ls = 'None', markersize=10)
    #pyplot.title('Decay regions with CO2 data smoothed by' + str(nAveragingPoints) + 'points')
    pyplot.grid(axis='y')
    from matplotlib.lines import Line2D # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html
    custom_lines = [Line2D([0], [0], color='gray', lw=2),
                Line2D([0], [0], color='k', lw=2),
                Line2D([0], [0], marker = '^', color=cmap(0.6), ls= 'None'),
                Line2D([0], [0], marker = 'v', color=cmap(0.6), ls= 'None')]

    
    pyplot.legend(custom_lines, (['All CO$_2$ sensors', 'Identified decay periods', 'Decay start point', 'Decay end point']))

#    LegendList = LegendListGeneral.FindLegendList(CO2Columns, CaseStudy) + ['Identified Decay Periods']
    pyplot.ylabel('$\Delta$CO$_2$ (ppm)')
    pyplot.xlabel('Time')
    #pyplot.legend(LegendList)
    ax = pyplot.gca()
    xfmt = matplotlib.dates.DateFormatter('%H:%M')#'%m-%d') #%H')
    ax.xaxis.set_major_formatter(xfmt)
    pyplot.tight_layout() # top stop overlap of text as much as possible
    #fig.subplots_adjust(top=0.88) 
    pyplot.show()


def PlotIdentifyDecayCurvesAndDoorData(InputData, Prox, FDData, CO2Columns, RawDecayPeriods, DecayStartPositions,
                            DecayEndPositions, nAveragingPoints, CaseStudy, AllData = None, OccupiedData = None):
    '''Plot the CO2 data with the identified decay curves in black.'''
##
 
    AveragedCO2Data =  InputData[CO2Columns].rolling(window=nAveragingPoints,center=True).mean()
    pyplot.rcParams.update({'font.size': 14})
    
    pyplot.set_cmap('viridis')
    cmap = pyplot.cm.viridis
    pyplot.figure(figsize=(8,4.0))
    fig = pyplot.figure(figsize = (9,5.5))
    ax1 = pyplot.subplot2grid((3,1), (0,0), rowspan = 2)

    if isinstance(AllData, pd.DataFrame): # set some columns to plot in distinct colours
        if CaseStudy == 'Loughborough':
            AllCO2Columns = ['CO2D','CO2E', 'CO2A', 'CO2C']
        elif CaseStudy == '2D':
            AllCO2Columns = ['CO2A','CO2B', 'CO2C']
        elif CaseStudy == '2A':
            AllCO2Columns = ['CO2A','CO2B', 'CO2C', 'CO2D']
        elif CaseStudy == '2C':
            AllCO2Columns = ['CO2A','CO2B']
        
        else:
            AllCO2Columns = CO2Columns
        ax1.plot(AllData['DateTime'], AllData[AllCO2Columns], color = 'gray', ls='-')
        #pyplot.plot(AllData['DateTime'], AllData['CO2C'], color = 'c', ls='-')
        #pyplot.plot(AllData['DateTime'], AllData[CO2Columns].rolling(window=nAveragingPoints,center=True).mean(), color = 'darkgrey', ls='--')
    if isinstance(OccupiedData, pd.DataFrame):
        ax1.plot(OccupiedData['DateTime'], OccupiedData[AllCO2Columns], color = 'gainsboro', ls='-')
        #pyplot.plot(OccupiedData['DateTime'], OccupiedData[CO2Columns].rolling(window=nAveragingPoints,center=True).mean(), color = 'lightgrey', ls='--')
    #ax1.plot(InputData['DateTime'], AveragedCO2Data, color = 'black', ls=':')
    # uncomment next line to show homogeneous periods with black dots.
    #pyplot.plot(InputData['DateTime'], AveragedCO2Data, color = 'black', marker= 'x', ls='None')

    ax1.plot(InputData['DateTime'], InputData[CO2Columns][RawDecayPeriods], 'k')
    #pyplot.plot(InputData['DateTime'], AveragedCO2Data[RawDecayPeriods], 'k')
    # uncomment next line for dotted line at 0∆CO2. 
    #pyplot.plot([InputData['DateTime'][~InputData['DateTime'].isnull()].iloc[0], InputData['DateTime'][~InputData['DateTime'].isnull()].iloc[-1]], [0,0], ls = ':', color = '0.8')
    # Run the following two lines put markers on the plot at the start and end points of the decay curve
    ax1.plot(InputData['DateTime'], InputData[CO2Columns][DecayStartPositions], color =cmap(0.6), marker = '^', ls = 'None', markersize = 6)
    ax1.plot(InputData['DateTime'], InputData[CO2Columns][DecayEndPositions], color = cmap(0.6), marker = 'v', ls = 'None', markersize=6)
    
    #pyplot.title('Decay regions with CO2 data smoothed by' + str(nAveragingPoints) + 'points')
    ax1.grid(axis='y')
    from matplotlib.lines import Line2D # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html
    custom_lines = [Line2D([0], [0], color='gainsboro', lw=2),
                        Line2D([0], [0], color='gray', lw=2),
                        Line2D([0], [0], color='k', lw=2),
                        Line2D([0], [0], marker = '^', color=cmap(0.6), ls= 'None'),
                        Line2D([0], [0], marker = 'v', color=cmap(0.6), ls= 'None')]

    ax1.legend(custom_lines, (['Occupied','Unoccupied', 'Decay periods', 'Decay start', 'Decay end']), loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=3)

#    LegendList = LegendListGeneral.FindLegendList(CO2Columns, CaseStudy) + ['Identified Decay Periods']
    ax1.set(ylabel='$\Delta$CO$_2$ (ppm)')
    ax1.set(xlabel='.')

    
    ax2 = fig.add_subplot(3,1,3, sharex = ax1)
    Tick_vals = [0,1]
    # Label the y axis with open and closed text at 1 and 0
    new_ticks = ["Open" if y == 1 else "Closed" for y in Tick_vals]
    pyplot.yticks(Tick_vals, new_ticks)
    
    Offset = 0
    CMapVals = [0.05,0.2, 0.35, 0.5, 0.65, 0.8, 0.95]
    for i in range(1, len(Prox.columns)):
        Sensori = Prox.columns[i]
        SensoriData = Prox[~N.isnan(Prox[Sensori])]
        ax2.step(SensoriData['DateTime'], SensoriData[Sensori] + Offset, where='post', color = cmap(CMapVals[i%7]))
        Offset = Offset + 0.025

    ax2.step(FDData['DateTime'], (((1+Offset+0.025)*FDData['State'])-0.025), where = 'post', color = 'k')        
    ax2.legend(Prox.columns.tolist()[1:]+['FrontD'], loc='upper center', bbox_to_anchor=(0.5, 1.6), ncol=5)
    xfmt = matplotlib.dates.DateFormatter('%H:%M')#('%m-%d %H:%M') #%m-%d %H
    xfmt1 = matplotlib.dates.DateFormatter('')#('%m-%d %H:%M') #%m-%d %H
    ax1.xaxis.set_major_formatter(xfmt1)
    ax2.xaxis.set_major_formatter(xfmt)
    ax2.set(xlabel='Time')


    #pyplot.title(' ')
    pyplot.tight_layout() # top stop overlap of text as much as possible
    #fig.subplots_adjust(top=0.88) 
    pyplot.show()



def PlotDecayCurveFit(ExtendedDecayData, DecayTime, i, CO2DiffVals, LnCO2DiffVals, DeltaTime, LinModelLnCO2DiffT0, LinModelDecayConst, LinModelLnCO2DiffVals, LinModelDW, ExpModelCO2DiffT0, ExpModelDecayConst, ExpModelCO2DiffVals, ExpModelDW, DecayStartTime, UncertaintyDecayVals, UncertaintyLnDecayVals, ExternalCO2, CO2Columns, CaseStudy, ProxData = []):
    '''Plot the data, fitted decay, proximity state of doors and windows, residuals and lag plot for a decay curve'''
        
    # Set up data to plot, additional is for plotting an period of time before and after the decay so that the context of the decay can be seen 
    AdditionalCO2Data = ExtendedDecayData[CO2Columns]
    AdditionalTime = ExtendedDecayData['DateTime']
    AdditionalDeltaTime = AdditionalTime - DecayTime.iloc[0]
    AdditionalDeltaTime = AdditionalDeltaTime / N.timedelta64(1, 'h') # formatted as hours

    
    LinModelCO2DiffVals = N.exp(LinModelLnCO2DiffT0)*(N.exp(-LinModelDecayConst*DeltaTime))
    LinModelFittedCurve = LinModelCO2DiffVals + ExternalCO2
    ExpModelLnCO2DiffVals = -ExpModelDecayConst*DeltaTime+(N.log(ExpModelCO2DiffT0))
    # Extended curve over a longer period to see how the shape develops
    AdditionalLinModelFittedCurve = N.exp(LinModelLnCO2DiffT0)*(N.exp(-LinModelDecayConst*AdditionalDeltaTime)) + ExternalCO2

    # Initialise the plot
    fig = pyplot.figure(figsize=(12,8))
    pyplot.rcParams.update({'font.size': 16})
    RoomName = LegendListGeneral.FindLegendList([i], CaseStudy)[0]

    #######
    # Plot the linearized data and fit in the top right of the plot
    ax = fig.add_subplot(3,2,2)
    ErrorBarsN = (int(len(DeltaTime)/10)+1) # Plot 10 error bars on the graph, otherwise the whole thing is error bars
    pyplot.errorbar(DeltaTime, LnCO2DiffVals, yerr = UncertaintyLnDecayVals, color = 'k', ls='-', errorevery = 1)
    pyplot.plot(DeltaTime, LinModelLnCO2DiffVals, 'b-', zorder = 100)
    pyplot.legend(['Model', 'Measurement'])
    pyplot.ylabel('Ln($\Delta$CO$_2$)')
    pyplot.xlabel('Time since start of decay (Hours)')

    #######
    # Plot the residuals of the exponential plot in the middle right
    ax = fig.add_subplot(3,2,4)
    LinModResiduals = LnCO2DiffVals - LinModelLnCO2DiffVals
    ExpModResiduals = LnCO2DiffVals - ExpModelLnCO2DiffVals
    pyplot.plot(DeltaTime, N.zeros((1, len(DeltaTime)))[0], color = '0.8', ls = '-')
    pyplot.plot(DeltaTime, LinModResiduals, 'bo')
    LinModelRMSE = LinModResiduals.std()
    ax.text(0.65,0.9, 'RMSE = ' + ('%0.2f'%LinModelRMSE),
        transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))
    pyplot.ylabel('Residuals')
    pyplot.xlabel('Time since start of decay (Hours)')

    #######
    # Plot the ith  against i-1th residuals, lag plot
    ax = fig.add_subplot(3,2,6)
    LinModLaggedResiduals = N.roll(LinModResiduals, 1)
    ExpModLaggedResiduals = N.roll(ExpModResiduals, 1)
    pyplot.plot(LinModLaggedResiduals[1:], LinModResiduals[1:], 'bo')
    pyplot.xlabel('(i-1)$^{th}$ Residual')
    pyplot.ylabel('i$^{th}$ Residual')
    ax.text(0.7,0.9, 'DW = ' + ('%0.2f'%LinModelDW),
        transform = ax.transAxes, verticalalignment='top', horizontalalignment = 'left', bbox=dict(alpha=0.5, fc='white', ec='k'))

    ####### 
    ax1 = pyplot.subplot2grid((3,2), (0,0), rowspan = 2) # make the plot double height in the top left side
    #pyplot.plot(AdditionalDeltaTime, AdditionalCO2Data[CO2Columns], color = '0.9', ls = '--')
    #pyplot.plot(AdditionalDeltaTime, AdditionalCO2Data[i], color = '0.6', ls = '-')
    ax1.set_xlim([AdditionalDeltaTime.iloc[0], AdditionalDeltaTime.iloc[-1]])

    #pyplot.plot(AdditionalDeltaTime, AdditionalFittedCurve, color = '0.8', ls = '-') # This is to plot the extension of the fit for another hour
    if i == 'CO2BR':
        ExtraColsToPlot = ['CO2A','CO2C','CO2D','CO2E']
    elif CaseStudy == '2D':
        ExtraColsToPlot = ['CO2A','CO2B','CO2C']
    else:
        ExtraColsToPlot = i
    pyplot.plot(AdditionalDeltaTime, ExtendedDecayData[ExtraColsToPlot], ls='-', color = 'lightgrey')

    pyplot.errorbar(DeltaTime, (CO2DiffVals + ExternalCO2), yerr = UncertaintyDecayVals, color = 'k', ls = '-',
                    errorevery = 1, zorder=50)
    
    pyplot.plot(DeltaTime, LinModelFittedCurve, 'b-', zorder = 100)
    # Plot the external CO2 level
    from matplotlib.lines import Line2D # instructions here https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html
    custom_lines = [Line2D([0], [0], color='b', lw=2),
                    Line2D([0], [0], color='k', lw=2),
                    Line2D([0], [0], color='lightgrey', lw=2)]

    ax1.legend(custom_lines, (['Model', 'Mean sensors', 'Individual sensor']), loc='upper right', title = 'VR = ' + ('%0.2f'%LinModelDecayConst) + ' ach')

    
    pyplot.grid(axis='y')
    pyplot.ylabel('$\Delta$CO$_2$ (ppm)')
    pyplot.xlabel('Time since start of decay (Hours)')


    ########
    ax = fig.add_subplot(3,2,5, sharex = ax1)
    # Set the limits in case there is no change in door state & change the y marks from 1, 0 to open and closed
    pyplot.ylim(-0.1,1.35)
    Tick_vals = [0,1]
    # Label the y axis with open and closed text at 1 and 0
    new_ticks = ["Open" if y == 1 else "Closed" for y in Tick_vals]
    pyplot.yticks(Tick_vals, new_ticks)
    pyplot.xlabel('Time since start of decay (Hours)')
    # Relevant proximity sensors for each room
    if isinstance(ProxData, list): # This code is for if the window/door data were collected using state monitoring equipment and are stored as part of the data frame with the CO2 data.
        RoomSensors, OtherSensors = FindProxSensorForDecayFit(i)
        Offset = 0
        for RoomSensor in RoomSensors:
            pyplot.plot(AdditionalDeltaTime, ExtendedDecayData[RoomSensor] + Offset, ls = '-')
            Offset = Offset + 0.05
        for OtherSensor in OtherSensors:
            pyplot.plot(AdditionalDeltaTime, ExtendedDecayData[OtherSensor] + Offset, color = '0.6', ls = '-')
            Offset = Offset + 0.05
        ProxLegend = LegendListGeneral.FindProximityList(RoomSensors)
        pyplot.legend(ProxLegend, loc = 'best')
    elif isinstance(ProxData, pd.DataFrame): # This code is for if the window / door opening data were collected using event logging equipment and are stored in their own data frame.
        if i == 'CO2BR':
            SensoriData = ProxData[~N.isnan(ProxData['BRState'])]
            ax.step(SensoriData['DeltaTime'], SensoriData['BRState'], where='post', color = 'k')
            ax.legend(['Back room door'], loc = 'upper right')
        else:
            Offset = 0
            for i in range(1, len(ProxData.columns)):
                Sensori = ProxData.columns[i]
                SensoriData = ProxData[~N.isnan(ProxData[Sensori])]
                ax.step(SensoriData['DeltaTime'], SensoriData[Sensori] + Offset, where='post') #, color = 'k')
                Offset = Offset + 0.025
            ax.legend(ProxData.columns.tolist()[1:-1])
    ax.set_xlim([AdditionalDeltaTime[~N.isnan(AdditionalDeltaTime)].iloc[0], AdditionalDeltaTime[~N.isnan(AdditionalDeltaTime)].iloc[-1]])
        

    ###### plot the final graph 
    pyplot.tight_layout() # top stop overlap of text as much as possible
    #fig.subplots_adjust(top=0.88) # more space at the top for the title
    pyplot.show()

####### End of function
    

def PlotOccupiedPeriodsWithMask(InputData, CO2Columns, OccupiedSubset, UnoccupiedSubset, CaseStudy):
    '''Plot the CO2 data with the possible occupied periods in black.'''
    # Plot the CO2 data
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns])

    # Generate a mask of the same dimensions as InputData[CO2Columns] for where house might be occupied
    # Since occupancy periods is trying to say something about the whole house, not individual rooms.

    pyplot.figure(figsize=(8,5.5), dpi=100) # for half an A4 page
    pyplot.set_cmap('viridis')
    cmap = pyplot.cm.viridis
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns], '0.8')
#    pyplot.plot(UnoccupiedSubset['DateTime'], UnoccupiedSubset[CO2Columns])
#    pyplot.plot([InputData['DateTime'][~InputData['DateTime'].isnull()].iloc[0], InputData['DateTime'][~InputData['DateTime'].isnull()].iloc[-1]], [0,0], ls = '-', color = '0.6')
    pyplot.plot([InputData['DateTime'][~InputData['DateTime'].isnull()].iloc[0], InputData['DateTime'][~InputData['DateTime'].isnull()].iloc[-1]], [50,50], ls = '--', color = '0.6')

    CMapVals = [0.1,0.4,0.7,0.95]
    for i in range(0,len(CO2Columns)):
        pyplot.plot(UnoccupiedSubset['DateTime'], UnoccupiedSubset[[CO2Columns[i]]], ls='-', color = cmap(CMapVals[i]))
    pyplot.plot(UnoccupiedSubset['DateTime'], UnoccupiedSubset['MeanCO2'], 'k')
 
    LegendList = LegendListGeneral.FindLegendList(CO2Columns, CaseStudy)
    LegendList = [Room + ', Unoccupied' for Room in LegendList]

    from matplotlib.lines import Line2D # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html
    custom_lines = [Line2D([0], [0], color=cmap(CMapVals[0]), lw=2),
                Line2D([0], [0], color=cmap(CMapVals[1]), lw=2),
                Line2D([0], [0], color=cmap(CMapVals[2]), lw=2),
                Line2D([0], [0], color=cmap(CMapVals[3]), lw=2),
                Line2D([0], [0], color='k', lw=2),
                Line2D([0], [0], color='0.8', lw=2)]

    pyplot.legend(custom_lines, (LegendList + ['Whole House Mean, Unoccupied', 'Occupied Data']))
    pyplot.grid(axis='y')

    ax = pyplot.gca()
    xfmt = matplotlib.dates.DateFormatter('%m-%d')#'%H:%M')#('%H')#('%m-%d') #%H')
    ax.xaxis.set_major_formatter(xfmt)
    pyplot.ylabel('$\Delta$CO$_2$ (ppm$_{(v)}$)')
    pyplot.xlabel('Month-Date')
    daylocator = matplotlib.dates.DayLocator(interval=1)
    ax.xaxis.set_major_locator(daylocator)

    pyplot.show()    
    

def PlotOccupiedPeriods(InputData, CO2Columns, OccupancyPeriods, OccupancyStartPositions, OccupancyEndPositions):
    '''Plot the CO2 data with the possible occupied periods in black.'''
    # Plot the CO2 data
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns])

    # Generate a mask of the same dimensions as InputData[CO2Columns] for where house might be occupied
    # Since occupancy periods is trying to say something about the whole house, not individual rooms.
    OccupancyMask = pd.DataFrame(index = range(OccupancyPeriods.index[0], OccupancyPeriods.index[-1]), columns = CO2Columns)
    for CO2Sensor in CO2Columns:
        OccupancyMask[CO2Sensor] = OccupancyPeriods

    pyplot.plot(InputData['DateTime'], InputData[CO2Columns][OccupancyMask], 'k-')
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns][OccupancyStartPositions], ls = None, marker = 'None', color = 'r')
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns][OccupancyEndPositions], ls = None, marker = 'None', color = 'b')
    LegendList = LegendListGeneral.FindLegendList(CO2Columns)
    LegendList.append('Inferred Occupied Periods')
    pyplot.legend(LegendList)
    pyplot.plot(InputData['DateTime'], InputData[CO2Columns].rolling(window=7, center =True).mean(), zorder = -1, color='0.6')
    pyplot.show()


def PlotCO2AndDoorSensorsAllTime(InputData, CO2Columns, Prox, FrontDoorData, CaseStudy):
    fig = pyplot.figure(figsize = (8,5.5))
    pyplot.set_cmap('viridis')
    cmap = pyplot.cm.viridis

    ax1 = pyplot.subplot2grid((3,1), (0,0), rowspan = 2)
    # Add more colours in here if you have more than 7 sensors 
    CMapVals = [0.05,0.2, 0.35, 0.5, 0.65, 0.8, 0.95]
    for i in range(0, len(CO2Columns)):
        CO2Sensor = CO2Columns[i]
        ax1.plot(InputData['DateTime'], InputData[CO2Sensor], color = cmap(CMapVals[i]))
    LegendList = LegendListGeneral.FindLegendList(CO2Columns, CaseStudy)
    ax1.legend(LegendList, loc=1)
    # The following line plots the front door opening and closing on the CO2 graph, which can make it easier to see what's happening.
    #ax1.stem(FrontDoorData['DateTime'], N.full(len(FrontDoorData), InputData[CO2Columns].max().max()), markerfmt = 'none', color= '0.6')
    MinCO2 = InputData[CO2Columns].min().min()
    MaxCO2 = InputData[CO2Columns].max().max()
##    if MinCO2>300:
##        ax1.step(FrontDoorData['DateTime'], ((MaxCO2-MinCO2)*FrontDoorData['State'])+MinCO2, where = 'post', color = '0.6')
##    else:
##        ax1.step(FrontDoorData['DateTime'], ((MaxCO2)*FrontDoorData['State']), where = 'post', color = '0.6')


    ax1.set(ylabel='CO$_2$ Concentration Difference (ppm)')
    
    ax2 = fig.add_subplot(3,1,3, sharex = ax1)
    Tick_vals = [0,1]
    # Label the y axis with open and closed text at 1 and 0
    new_ticks = ["Open" if y == 1 else "Closed" for y in Tick_vals]
    pyplot.yticks(Tick_vals, new_ticks)
    ProxCMap = [CMapVals[3], 1, CMapVals[6], CMapVals[4], CMapVals[1], CMapVals[0]]
    Offset = 0
    if isinstance(Prox, list):
        for i in range(0, len(Prox)):
            Sensori = Prox[i]
            ax2.plot(InputData['DateTime'], InputData[Sensori]+Offset, color = cmap(ProxCMap[i]))
            Offset = Offset + 0.025
        ProxLegendList = LegendListGeneral.FindLegendList(Prox, CaseStudy)
        ax2.legend(ProxLegendList, loc= 1)

    elif isinstance(Prox, pd.DataFrame):
        for i in range(1, len(Prox.columns)):
            Sensori = Prox.columns[i]
            SensoriData = Prox[~N.isnan(Prox[Sensori])]
            ax2.step(SensoriData['DateTime'], SensoriData[Sensori] + Offset, where='post', color = '0.7')
            Offset = Offset + 0.025
        ax2.step(FrontDoorData['DateTime'], (((1+Offset+0.025)*FrontDoorData['State'])-0.025), where = 'post', color = 'k')        
        from matplotlib.lines import Line2D # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html

        custom_lines = [Line2D([0], [0], color='k', lw=2),
                Line2D([0], [0], color='0.7', lw=2)]

        ax2.legend(custom_lines, (['Front door', 'Internal windows & doors']), loc='upper center',  bbox_to_anchor=(0.5, 1.2), ncol=2)
    
##        BDOnly = Prox[~N.isnan(Prox['BDState'])]
##        BROnly = Prox[~N.isnan(Prox['BRState'])]
##        ax2.step(BDOnly['DateTime'], BDOnly['BDState'], where='post', color = 'k')
##        ax2.step(BROnly['DateTime'], BROnly['BRState']+0.05, where='post', color = 'b')
        #ax2.legend(Prox.columns.tolist()[1:])
    xfmt = matplotlib.dates.DateFormatter('%H:%M')#('%m-%d %H:%M') #%m-%d %H
    ax1.xaxis.set_major_formatter(xfmt)
    ax2.xaxis.set_major_formatter(xfmt)
    ax2.set(xlabel='Time')
    
    pyplot.tight_layout()
    pyplot.show()



def PlotKnownOccupancyStartEndTimes(KnownStartTimes, KnownEndTimes, InputData, OccupancyMask, CO2Columns, ProxColumns, FrontDoorData):
    
    pyplot.rcParams.update({'font.size': 14})
    pyplot.set_cmap('viridis')
    fig = pyplot.figure(figsize = (9,5.5))

    cmap = pyplot.cm.viridis
    CMapVals = [0.05,0.2, 0.35, 0.5, 0.8, 0.5, 0.95]
    
    ax1 = pyplot.subplot2grid((3,1), (0,0), rowspan = 2)
    ax1.plot(InputData['DateTime'], InputData[CO2Columns][OccupancyMask], color = 'black')
    ax1.plot(InputData['DateTime'], InputData[CO2Columns], color = '0.6')
    ax1.plot(InputData['DateTime'], InputData[CO2Columns][OccupancyMask], color = 'black')

##    LegendList = LegendListGeneral.FindLegendList(CO2Columns)
    ax1.legend(['Occupied'])
    MinCO2 = InputData[CO2Columns].min().min()
    MaxCO2 = InputData[CO2Columns].max().max()
    #FDIndex = FrontDoorData.index[0]
    #KnownEndIndex = KnownEndTimes.index[0]
    #KnownStartIndex = KnownStartTimes.index[0]

    
##    if len(FrontDoorData)>0:
##        FDIndex = FrontDoorData.index[0]
##        for i in N.arange(FDIndex, FDIndex+len(FrontDoorData)):
##            pyplot.plot([FrontDoorData.loc[i, 'DateTime'], FrontDoorData.loc[i, 'DateTime']], [MinCO2, MaxCO2], color = '0.6')
    if len(KnownEndTimes)>0:
        KnownEndIndex = KnownEndTimes.index[0]
        for i in N.arange(KnownEndIndex, KnownEndIndex+len(KnownEndTimes)):
            pyplot.plot([KnownEndTimes.loc[i, 'DateTime'], KnownEndTimes.loc[i, 'DateTime']], [MinCO2, MaxCO2], color = cmap(0.1), ls = '--')
    if len(KnownStartTimes)>0:
        KnownStartIndex = KnownStartTimes.index[0]
        for i in N.arange(KnownStartIndex, KnownStartIndex+len(KnownStartTimes)):
            pyplot.plot([KnownStartTimes.loc[i, 'DateTime'], KnownStartTimes.loc[i, 'DateTime']], [MinCO2, MaxCO2], color = cmap(0.4), ls = ':')
    ax1.set(ylabel = 'CO$_2$ Concentration (ppm)')


    from matplotlib.lines import Line2D # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html
    custom_lines = [Line2D([0], [0], color='k', lw=2),
                Line2D([0], [0], color='0.6', lw=2),
                Line2D([0], [0],ls=':', color=cmap(0.4), lw=2)]#,
                #Line2D([0], [0],ls = '--', color=cmap(0.1), lw=2)]

    ax1.legend(custom_lines, (['OSA occupied', 'OSA unoccupied', 'Reported start of occupancy']), loc='upper center',  bbox_to_anchor=(0.45, 1.2), ncol=3) #, 'Reported end of occupancy'
    #ax2.legend(Prox.columns.tolist()[1:]+['FrontD'], loc='upper center', bbox_to_anchor=(0.5, 1.6), ncol=5)
    
    ax2 = fig.add_subplot(3,1,3, sharex = ax1)
    Tick_vals = [0,1]
    # Label the y axis with open and closed text at 1 and 0
    new_ticks = ["Open" if y == 1 else "Closed" for y in Tick_vals]
    pyplot.yticks(Tick_vals, new_ticks)
    ProxCMap = [CMapVals[3], 1, CMapVals[6], CMapVals[4], CMapVals[1], CMapVals[0]]
    Offset = 0
    if isinstance(ProxColumns, list):
        for i in range(0, len(ProxColumns)):
            Sensori = ProxColumns[i]
            ax2.plot(InputData['DateTime'], InputData[Sensori]+Offset, color= '0.7') #color = cmap(ProxCMap[i]), alpha=0.6)
            Offset = Offset + 0.03
    ax2.step(FrontDoorData['DateTime'], (((1+Offset+0.025)*FrontDoorData['State'])-0.025), where = 'post', color = 'k')        
    custom_lines = [Line2D([0], [0], color='k', lw=2),
                Line2D([0], [0], color='0.7', lw=2)]

    ax2.legend(custom_lines, (['Front door', 'Internal doors']), loc='upper center',  bbox_to_anchor=(0.5, 1.5), ncol=2)
    ### *** HERE ***
    #ax2.step(FDData['DateTime'], (((1+Offset+0.025)*FDData['State'])-0.025), where = 'post', color = 'k')        
    #ax2.legend(Prox.columns.tolist()[1:]+['FrontD'], loc='upper center', bbox_to_anchor=(0.5, 1.6), ncol=5)

        #ProxLegendList = LegendListGeneral.FindLegendList(Prox, CaseStudy)
        #ax2.legend(ProxLegendList, loc= 1)

    xfmt = matplotlib.dates.DateFormatter('%H:%M')#('%m-%d %H:%M') #%m-%d %H
    ax1.xaxis.set_major_formatter(xfmt)
    ax2.xaxis.set_major_formatter(xfmt)
    hourlocator = matplotlib.dates.HourLocator(interval=4)
    ax2.xaxis.set_major_locator(hourlocator)

    ax2.set(xlabel='Time')
    

    pyplot.tight_layout(pad=2.0)
    pyplot.suptitle(' ')
    pyplot.show()



    
def PlotCO2AndDoorSensorsOccupancy(InputData, OccupancyMask, CO2Columns, Prox, FrontDoorStateChange, CaseStudy):
    pyplot.rcParams.update({'font.size': 16})
    pyplot.set_cmap('viridis')
    fig = pyplot.figure()
    ax1 = pyplot.subplot2grid((3,1), (0,0), rowspan = 2)
#    ax1.plot(InputData['DateTime'], InputData[CO2Columns][OccupancyMask], color = 'black')
    ax1.plot(InputData['DateTime'], InputData[CO2Columns])
    ax1.plot(InputData['DateTime'], InputData[CO2Columns][OccupancyMask], color = 'black')
    LegendList = LegendListGeneral.FindLegendList(CO2Columns, CaseStudy)
    ax1.legend(LegendList+['Occupied'])
    ax1.set(ylabel = 'CO$_2$ Concentration (ppm)')
    # plot the FD door opening data
    MinCO2 = InputData[CO2Columns].min().min()
    MaxCO2 = InputData[CO2Columns].max().max()
    FDIndex = FrontDoorStateChange.index[0]
    if MinCO2>300:
        ax1.step(FrontDoorStateChange['DateTime'], ((MaxCO2-MinCO2)*FrontDoorStateChange['State'])+MinCO2, where = 'post', color = '0.6')
    else:
        ax1.step(FrontDoorStateChange['DateTime'], ((MaxCO2)*FrontDoorStateChange['State']), where = 'post', color = '0.6')

    #for i in N.arange(FDIndex, FDIndex+len(FrontDoorStateChange)):
#        pyplot.plot([FrontDoorStateChange.loc[i, 'DateTime'], FrontDoorStateChange.loc[i, 'DateTime']], [MinCO2, MaxCO2], color = '0.6')
    
    ax2 = fig.add_subplot(3,1,3, sharex = ax1)
    Tick_vals = [0,1]
    # Label the y axis with open and closed text at 1 and 0
    new_ticks = ["Open" if y == 1 else "Closed" for y in Tick_vals]
    pyplot.yticks(Tick_vals, new_ticks)
    ax2.set(xlabel = 'Date')
    if isinstance(Prox, list):
        ax2.plot(InputData['DateTime'], InputData[Prox])
    elif isinstance(Prox, pd.DataFrame):
        Offset = 0
        for i in range(1, len(Prox.columns)):
            Sensori = Prox.columns[i]
            SensoriData = Prox[~N.isnan(Prox[Sensori])]
            ax2.step(SensoriData['DateTime'], SensoriData[Sensori] + Offset, where='post') #, color = 'k')
            Offset = Offset + 0.05
        ax2.legend(Prox.columns.tolist()[1:])

    pyplot.tight_layout()
    pyplot.show()


    

def PlotKnownOccupancyStartEndTimesDecays(KnownStartTimes, KnownEndTimes, InputData, OccupancyMask, ProxSplitDecayPeriods, CO2Columns, ProxColumns, FrontDoorData):
    pyplot.rcParams.update({'font.size': 16})
    pyplot.set_cmap('viridis')
    fig = pyplot.figure()
    ax1 = pyplot.subplot2grid((3,1), (0,0), rowspan = 2)
    ax1.plot(InputData['DateTime'], InputData[CO2Columns][OccupancyMask], color = 'black')
    ax1.plot(InputData['DateTime'], InputData[CO2Columns], color = '0.6')
    ax1.plot(InputData['DateTime'], InputData[CO2Columns][OccupancyMask], color = 'black')
    ax1.plot(InputData['DateTime'], InputData[CO2Columns][ProxSplitDecayPeriods]) # uncomment this line to make the decay periods show in colour
##    LegendList = LegendListGeneral.FindLegendList(CO2Columns)
    #ax1.legend(['Occupied'])
    MinCO2 = InputData[CO2Columns].min().min()
    MaxCO2 = InputData[CO2Columns].max().max()
    #FDIndex = FrontDoorData.index[0]
    #KnownEndIndex = KnownEndTimes.index[0]
    #KnownStartIndex = KnownStartTimes.index[0]
    if len(FrontDoorData)>0:
        FDIndex = FrontDoorData.index[0]
        for i in N.arange(FDIndex, FDIndex+len(FrontDoorData)):
            pyplot.plot([FrontDoorData.loc[i, 'DateTime'], FrontDoorData.loc[i, 'DateTime']], [MinCO2, MaxCO2], color = '0.6')
    if len(KnownEndTimes)>0:
        KnownEndIndex = KnownEndTimes.index[0]
        for i in N.arange(KnownEndIndex, KnownEndIndex+len(KnownEndTimes)):
            pyplot.plot([KnownEndTimes.loc[i, 'DateTime'], KnownEndTimes.loc[i, 'DateTime']], [MinCO2, MaxCO2], color = 'r', ls = '--')
    if len(KnownStartTimes)>0:
        KnownStartIndex = KnownStartTimes.index[0]
        for i in N.arange(KnownStartIndex, KnownStartIndex+len(KnownStartTimes)):
            pyplot.plot([KnownStartTimes.loc[i, 'DateTime'], KnownStartTimes.loc[i, 'DateTime']], [MinCO2, MaxCO2], color = 'b', ls = '--')
    ax1.set(ylabel = 'CO$_2$ Concentration (ppm)')
    xfmt = matplotlib.dates.DateFormatter('%H')#('%m-%d %H:%M') #%m-%d %H
    ax1.xaxis.set_major_formatter(xfmt)
    
    ax2 = fig.add_subplot(3,1,3, sharex = ax1)
    Tick_vals = [0,1]
    # Label the y axis with open and closed text at 1 and 0
    new_ticks = ["Open" if y == 1 else "Closed" for y in Tick_vals]
    pyplot.yticks(Tick_vals, new_ticks)
    ax2.plot(InputData['DateTime'], InputData[ProxColumns])
    ax2.set(xlabel = 'Time')
    ax2.xaxis.set_major_formatter(xfmt)
    
    pyplot.tight_layout()
    pyplot.show()
##


def PlotDecayCurveOnly(ExtendedDecayData, DecayTime, i, CO2DiffVals, LnCO2DiffVals, DeltaTime, LinModelLnCO2DiffT0, LinModelDecayConst, LinModelLnCO2DiffVals, LinModelDW, ExpModelCO2DiffT0, ExpModelDecayConst, ExpModelCO2DiffVals, ExpModelDW, DecayStartTime, UncertaintyDecayVals, UncertaintyLnDecayVals, ExternalCO2, CO2Columns, CaseStudy, ProxData = []):
    '''Plot the data, fitted decay, proximity state of doors and windows, residuals and lag plot for a decay curve'''
        
    # Set up data to plot, additional is for plotting an period of time before and after the decay so that the context of the decay can be seen 
    #print(ExtendedDecayData)
    AdditionalCO2Data = ExtendedDecayData[CO2Columns]
    AdditionalTime = ExtendedDecayData['DateTime']
    AdditionalDeltaTime = AdditionalTime - DecayTime.iloc[0]
    AdditionalDeltaTime = AdditionalDeltaTime / N.timedelta64(1, 'h') # formatted as hours

    # Reconstruct the ln vals from the measured and fitted data
    #DataLnCO2DiffVals = N.log(CO2DiffVals)
    #FitLnCO2DiffVals = -1*DecayConst*DeltaTime + LnCO2DiffT0
    # Construct the curve fitted by polyfit during the time of the decay
    
    LinModelCO2DiffVals = N.exp(LinModelLnCO2DiffT0)*(N.exp(-LinModelDecayConst*DeltaTime))
    LinModelFittedCurve = LinModelCO2DiffVals + ExternalCO2
    ExpModelLnCO2DiffVals = -ExpModelDecayConst*DeltaTime+(N.log(ExpModelCO2DiffT0))
    # Extended curve over a longer period to see how the shape develops
    AdditionalLinModelFittedCurve = N.exp(LinModelLnCO2DiffT0)*(N.exp(-LinModelDecayConst*AdditionalDeltaTime)) + ExternalCO2

    # Initialise the plot
    fig = pyplot.figure(figsize=(13,8))
    pyplot.rcParams.update({'font.size': 16})
    #######
    # Plot the data in black and fitted curve over the time of the decay in red,
    # and the data from the hour before and after the decay in grey respectively
    ax1 = pyplot.subplot2grid((3,2), (0,0), rowspan = 2) # make the plot double height in the top left side
    pyplot.plot(AdditionalDeltaTime, AdditionalCO2Data[CO2Columns], color = '0.9', ls = '--')
    pyplot.plot(AdditionalDeltaTime, AdditionalCO2Data[i], color = '0.6', ls = '-')
    ax1.set_xlim([AdditionalDeltaTime.iloc[0], AdditionalDeltaTime.iloc[-1]])
    
    #pyplot.plot(AdditionalDeltaTime, AdditionalFittedCurve, color = '0.8', ls = '-') # This is to plot the extension of the fit for another hour
    ErrorBarsN = (int(len(DeltaTime)/10)+1)
    pyplot.errorbar(DeltaTime, (CO2DiffVals + ExternalCO2), yerr = 0, color = 'k', ls = '-',
                    errorevery = ErrorBarsN)
    #pyplot.plot(DeltaTime, LinModelFittedCurve, 'r-', zorder = 100)
    pyplot.plot(DeltaTime, (ExpModelCO2DiffVals+ExternalCO2), 'b-', zorder = 100)
    # Plot the external CO2 level
    pyplot.plot(AdditionalDeltaTime, N.full((1,len(AdditionalDeltaTime)), ExternalCO2)[0], color = '0.8', ls = '-')
    pyplot.ylabel('CO$_2$ (ppm$_{(v)}$)')
    pyplot.xlabel('Time (Hours)')

    pyplot.show()
