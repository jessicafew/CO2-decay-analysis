def FindLegendList(CO2Columns, CaseStudy):
    '''Given the list of CO2 sensor names, generate a list of which sensor is in which
    room.'''
    LegendList = list()
    if CaseStudy == 'Priory':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('Kitchen')
            elif CO2Sensor == 'CO2B':
                LegendList.append('Living Room')
            elif CO2Sensor == 'CO2C':
                LegendList.append('Hall')
            elif CO2Sensor == 'CO2D':
                LegendList.append('Bedroom 1 A')
            elif CO2Sensor == 'CO2E':
                LegendList.append('Bedroom 2')
            elif CO2Sensor == 'CO2F':
                LegendList.append('Bedroom 1 B')
            elif CO2Sensor == 'CO2G':
                LegendList.append('Bedroom 3')
            elif CO2Sensor == 'Prox1':
                LegendList.append('Bedroom 1')
            elif CO2Sensor == 'Prox2':
                LegendList.append('Bathroom')
            elif CO2Sensor == 'Prox3':
                LegendList.append('Bedroom 3')
            elif CO2Sensor == 'Prox4':
                LegendList.append('Bedroom 2')
            elif CO2Sensor == 'Prox5':
                LegendList.append('Living Room')
            elif CO2Sensor == 'Prox6':
                LegendList.append('Kitchen')
    elif CaseStudy == 'PR2019':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('Living Room B')
            elif CO2Sensor == 'CO2B':
                LegendList.append('Bedroom 3')
            elif CO2Sensor == 'CO2C':
                LegendList.append('Living Room A')
            elif CO2Sensor == 'CO2D':
                LegendList.append('Kitchen')
            elif CO2Sensor == 'CO2E':
                LegendList.append('Hall')
            elif CO2Sensor == 'CO2F':
                LegendList.append('Bedroom 1')
            elif CO2Sensor == 'CO2G':
                LegendList.append('Bedroom 2')
            elif CO2Sensor == 'CO2H':
                LegendList.append('Kitchen')
            elif CO2Sensor == 'CO2I':
                LegendList.append('IAQ CO2')
            elif CO2Sensor == 'CO2J':
                LegendList.append('Outdoor 1')
            elif CO2Sensor == 'CO2K':
                LegendList.append('Outdoor 2')

    elif CaseStudy == 'Loughborough':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('Back Room C') # wall, middle
            elif CO2Sensor == 'CO2B':
                LegendList.append('Front Room')
            elif CO2Sensor == 'CO2C':
                LegendList.append('Back Room D') # wall, floor
            elif CO2Sensor == 'CO2D':
                LegendList.append('Back Room A') # middle of room
            elif CO2Sensor == 'CO2E':
                LegendList.append('Back Room B') # wall ceiling
            elif CO2Sensor == 'CO2F':
                LegendList.append('Kitchen')
            elif CO2Sensor == 'CO2G':
                LegendList.append('Upstairs Hall')
            elif CO2Sensor == 'CO2BR':
                LegendList.append('Back Room Mean')
            elif CO2Sensor == 'CO2H':
                LegendList.append('Innova A')
            elif CO2Sensor == 'CO2I':
                LegendList.append('Upstairs BR A') # Bedroom middle
            elif CO2Sensor == 'CO2J':
                LegendList.append('Upstairs BR B') # Bedroom ceiling
            elif CO2Sensor == 'CO2K':
                LegendList.append('Upstairs BR C') # Bedroom wall middle
            elif CO2Sensor == 'CO2L':
                LegendList.append('Upstairs FR')
            elif CO2Sensor == 'CO2Inside':
                LegendList.append('Whole House Mean')
            elif CO2Sensor == 'CO2M':
                LegendList.append('Downstairs Hall')
            elif CO2Sensor == 'CO2N':
                LegendList.append('Upstairs Hall')
            elif CO2Sensor == 'VolWeightCO2':
                LegendList.append('Volume Weighted CO2')
            else:
                LegendList.append(CO2Sensor)

    elif CaseStudy == 'A':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('Bedroom')
            elif CO2Sensor == 'CO2B':
                LegendList.append('Living Room')
            elif CO2Sensor == 'CO2C':
                LegendList.append('Hall')
            elif CO2Sensor == 'CO2D':
                LegendList.append('Kitchen')

    elif CaseStudy == 'C':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('Hall')
            elif CO2Sensor == 'CO2B':
                LegendList.append('Living Room')
            elif CO2Sensor == 'CO2C':
                LegendList.append('Bedroom')
            elif CO2Sensor == 'CO2D':
                LegendList.append('Kitchen')

    elif CaseStudy == 'D':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('Bedroom 1')
            elif CO2Sensor == 'CO2B':
                LegendList.append('Living Room')
            elif CO2Sensor == 'CO2C':
                LegendList.append('Bedroom 2')
            elif CO2Sensor == 'CO2D':
                LegendList.append('Kitchen')

    elif CaseStudy == '2A':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('Hall')
            elif CO2Sensor == 'CO2B':
                LegendList.append('Living Room')
            elif CO2Sensor == 'CO2C':
                LegendList.append('Bedroom')
            elif CO2Sensor == 'CO2D':
                LegendList.append('Kitchen')
            elif CO2Sensor == 'MeanCO2':
                LegendList.append('Whole Flat')

    elif CaseStudy == '2B':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('Bedroom')
            elif CO2Sensor == 'CO2B':
                LegendList.append('Kitchen')
            elif CO2Sensor == 'MeanCO2':
                LegendList.append('Whole Flat')

    elif CaseStudy == '2C':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('Bedroom')
            elif CO2Sensor == 'CO2B':
                LegendList.append('Kitchen')
            elif CO2Sensor == 'MeanCO2':
                LegendList.append('Whole Flat')

    elif CaseStudy == '2D':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('Bedroom')
            elif CO2Sensor == 'CO2B':
                LegendList.append('Living Room')
            elif CO2Sensor == 'CO2C':
                LegendList.append('Kitchen')
            elif CO2Sensor == 'MeanCO2':
                LegendList.append('Whole Flat')
                
    elif CaseStudy == '2Ext':
        for CO2Sensor in CO2Columns:
            if CO2Sensor == 'CO2A':
                LegendList.append('External')
                
    # if the case study hasn't been included, just use the column headings in the legend.
    else:
        for CO2Sensor in CO2Columns:
            LegendList.append(CO2Sensor)
                
    return(LegendList)








