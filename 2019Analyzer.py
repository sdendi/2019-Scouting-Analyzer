# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 19:06:04 2019
                                    
@author: Saketh
"""

import tbaUtils
import pandas as pd
import numpy as np
from pprint import pprint
from tkinter import filedialog
def makeMatchList(event, year = 2018):
    '''
    Get match list from the Blue Alliance website depending on what event we're 
    going to. Format it and write it to a file. Have that read by the Scouting 
    Program and have formatted so that other scouting software can use it.
    '''
    RawMatches = tbaUtils.get_event_matches(event, year) 

    pprint(RawMatches[0:2])
    
    print()
    MatchList = []
    for Match in RawMatches:
        
        ShortMatch = []
        #Some of these matches are not quals, need to filter out non qm eventually
        MatchNum = Match['match_number']
        ShortMatch.append(MatchNum)
        
        for team in Match['alliances']['blue']['teams']:
        
            ShortMatch.append(int(team[3:]))
        
        for team in Match['alliances']['red']['teams']:
            
            ShortMatch.append(int(team[3:])) 
            
        comp_level = Match['comp_level']
        if comp_level == 'qm':
            MatchList.append(ShortMatch)
      
    print()
    MatchList.sort()
    pprint(MatchList)    

    with open('MatchList-' + event + '.csv', 'w') as File:
        for Match in MatchList : 
            Outstr = str(Match).replace('[', '').replace(']', '').replace(' ', '')+'\n'
            File.write(Outstr)

def readMatchList(testmode):    
    '''
    Read the Match List file created by makeMatchList.     
    
    '''
    if testmode : 
        FileName = r'C:\Users\Saketh\Documents\GitHub\2018-Scouting-Analyzer\Kansas City\MatchList-mokc2.csv'
    else :
        FileName = filedialog.askopenfilename(title = 'select MatchList file')
    with open(FileName, 'r') as Matchlist:
       data = Matchlist.readlines()
   
   
    result = []
    for line in data:
        line = line.replace('\n' , '')
        dataresult = line.split(',')
        for idx in range(len(dataresult)):
            dataresult[idx] = int(dataresult[idx])
        print(dataresult)
        result.append(dataresult)
        
    return result


def readScout(testmode):
    '''
    Read Scouting Data from a file, fix formatting to numeric where neccessary,
    clean the data, report any implausibile data.  
    '''
    if testmode :
        FileName = r'C:\Users\Saketh\Documents\matchScout.csv'
    else :
        FileName = filedialog.askopenfilename(title = 'select Data file')
    with open(FileName, 'r') as ScoutFile:
        ScoutData = pd.read_csv(ScoutFile, sep = '|') 
    Result = ScoutData.fillna(value = 0)
    return Result
    

def FindPartners(Matchlist, team = 1939):    
    '''
    Takes the Match List from the entire competition and finds the matches we're
    in and finds the teams that are with us.
    '''
    result = []
    for match in Matchlist:
        thisMatch = {}
        if team in match[1:]:
         #   print(match)
            if team in match[1:4]:
                thisMatch['alliance'] = 'blue'
                thisMatch['opposing'] = 'red'
                allies = match[1:4]
                thisMatch['opponents'] = match[4:7]
                allies.remove(team)
                thisMatch['allies'] = allies
            
                
            else:
                thisMatch['alliance'] = 'red'
                thisMatch['opposing'] = 'blue'
                allies = match[4:7]
                thisMatch['opponents'] = match[1:4]
                allies.remove(team)
                thisMatch['allies'] = allies
            thisMatch['match'] = match[0] 
            result.append(thisMatch)
            
    return result

            
def MatchReport(MatchList, PivotDf, Scoutdf, TeamNumber):
    ''' (dataframe)->dataframe
    (Scouting Data)->PivotTable with upcoming match partners
    Take the scouting data, trim down to only partners and opponents.
    Create a report by match showing partners and opponents.
    '''
    FileName = 'MatchReport.htm'
    with open(FileName, 'w') as File:
        File.write('<head>\n  <title>Pre-match scouting Report</title><br>\n')
        File.write('<link rel="icon" href="RoboticsAvatar2018.png" />') 
        File.write('<link rel="stylesheet" type="text/css" href="matchrep.css">')
        File.write('</head>\n')
        File.write('<body>\n')
        File.write('<h1><img src="8bit_logo.jpg", width=50, height=60>')
        File.write('Pre-match scouting Report</h1>\n')
        File.write('<div class="robot">\n')
        File.write('<h3>Our Robot' + '</h3>\n')
        SearchTeam(Scoutdf, PivotDf, TeamNumber, File)

        #print(MatchList[0]['allies'])
        LastScouted = max(Scoutdf['match'])
        
        # Prettying up the file output of the match list
        File.write('<h3>Forthcoming Matches</h3>\n')        
        
        File.write('<table border="1" class="dataframe">\n  <thead>\n    <tr style="text-align: right;">\n')
        File.write('      <th>Match</th>\n')
        File.write('      <th>Alliance</th>\n')
        File.write('      <th>Allies</th>\n')
        File.write('      <th>Opponents</th>\n')
        File.write('    </tr>\n  </thead>\n  <tbody>')

        
        for match in MatchList:
            if match['match'] > LastScouted:
                #File.write(str(match) + '\n')
                File.write('    <tr style="text-align: right;">\n')
                File.write('      <th><a href=#Match' + str(match['match']) + '>' + str(match['match']) + '</a></th>\n')
                File.write('      <th>' + match['alliance'] + '</th>\n')
                File.write('      <th>' + str(match['allies']) + '</th>\n')
                File.write('      <th>' + str(match['opponents']) + '</th>\n')
                File.write('    </tr>\n')                
                File.write('\n')
        File.write('</table>\n')
        File.write('</div>\n')
        #Printing reports for each forthcoming match
        for match in MatchList:
            if match['match'] > LastScouted:
                File.write('<div class="chapter">\n')
                File.write('<a name=Match' + str(match['match']) + '></a>\n')
                File.write('<h2>Match ' + str(match['match']) + '</h2>\n')
                                                               
                #print(len(PivotDf.columns))
                us = [TeamNumber]+match['allies']
                them = match['opponents']                 
                File.write('<h4>'+ match['alliance']+' Alliance</h4>\n')
                if any(i in them for i in PivotDf.index.values):
                    File.write(PivotDf.loc[us].to_html(float_format='{0:.2f}'.format))
                else:
                    File.write('Data not available\n')
                File.write('<h4>'+ match['opposing']+' Alliance</h4>\n')               
                if any(i in them for i in PivotDf.index.values):                    
                    File.write(PivotDf.loc[them].to_html(float_format='{0:.2f}'.format))
                else:
                    File.write('Data not available\n')
                
                File.write('\n<h3>Allies</h3>\n')
                for ally in match['allies']:
                    SearchTeam(Scoutdf, PivotDf, ally, File)
                    File.write('\n') 
                File.write('\n<h3>Opponents</h3>\n')
                for oppo in match['opponents']:
                    SearchTeam(Scoutdf, PivotDf, oppo, File)
                    File.write('\n')
                File.write('</div>\n')

                ''' with open ('MatchReport.csv', 'w') as File:
                    for match in MatchList:
                    Outstr = str(match)
                    File.write(Outstr)
                    '''
        File.write('</body>\n')    
        
def Day1Report(Scoutdf, PivotDf):
    '''(dataframe)->None
    Take Scouting data and analyze it by creating a report that will be presented
    at the Day 1 Scouting meeting
    '''
    outfile = '1st Day report.xlsx'
    with pd.ExcelWriter(outfile) as writer:
        Scoutdf = Scoutdf.sort_values(by = 'team')   
        tabname = 'Raw Data'
        Scoutdf.to_excel(writer, tabname, index=False)
        PivotDf = PivotDf.sort_values(by = 'team')
        tabname = 'Data Table'
        PivotDf.to_excel(writer, tabname, index=False)
    print('Day1Report written to file')
    

def SearchTeam(Scoutdf, PivotDf, TeamNumber, File = None):
    '''
    A Search function where we can find a team and their specific stats.
    '''
    print(Scoutdf)
    if File == None:
        print('Team:', TeamNumber)
        
        if TeamNumber not in PivotDf.team.values:
            print('Team', TeamNumber, 'is not yet scouted')
            return
            
        PivotDf.reset_index(inplace = True)
        PivotDf.set_index('team', inplace = True)
        print('Matches Played =', PivotDf.loc[TeamNumber]['totalmatches'])
        
        print('\nMatch Summary')
        print(PivotDf.loc[TeamNumber].to_dict())
        print('\nMatch Details')
        
        print(Scoutdf[Scoutdf.team == TeamNumber])
    else :
        File.write('<h4>Team: ' + str(TeamNumber) + '</h4>\n')

        PivotDf.reset_index(inplace = True)
                
        if TeamNumber not in PivotDf.team.values:
            File.write('\nTeam ' + str(TeamNumber) + ' is not yet scouted\n')
            PivotDf.set_index('team', inplace = True)
            return
            
        PivotDf.set_index('team', inplace = True)
        File.write('Matches Played =' + str(PivotDf.loc[TeamNumber]['totalmatches']) + '\n')
        
        File.write('\n<h5>Match Summary</h5>\n')
        temp = PivotDf.loc[TeamNumber].to_dict()
        if 'index' in temp:
            del temp['index']
        File.write(str(temp))
        File.write('\n<h5>Match Details</h5>\n')
        
        # Make pandas stop truncating the long text fields.
        pd.set_option('display.max_colwidth', -1)
        
        # Within each write, I'm specifying columns by number, taking off the
        # decimal places, and suppressing printing of the index number
        print(Scoutdf.columns)
        print(Scoutdf[Scoutdf.team == TeamNumber].to_html(columns = ['team']))
        
        # Comments        
        File.write(Scoutdf[Scoutdf.team == TeamNumber].to_html(columns=['match', 'team', 'Comments'], float_format='{0:.0f}'.format, index=False, justify='unset'))
        File.write('\n<br>\n')        
        '''
        # Calculated Fields
        File.write(Scoutdf[Scoutdf.team == TeamNumber].to_html(columns=[1, 2, 36, 37, 38], float_format='{0:.0f}'.format, index=False))
        File.write('\n<br>\n')  
        
            
        # Auton columns
        # Good stuff
        File.write(Scoutdf[Scoutdf.team == TeamNumber].to_html(columns=[1, 2, 4, 6, 10, 14], float_format='{0:.0f}'.format, index=False))
        File.write('\n<br>\n')
        # Failed Stuff
        File.write(Scoutdf[Scoutdf.team == TeamNumber].to_html(columns=[1, 2, 3, 5, 9, 13], float_format='{0:.0f}'.format, index=False))
        File.write('\n<br>\n')
        # Own Goals
        File.write(Scoutdf[Scoutdf.team == TeamNumber].to_html(columns=[1, 2, 7, 8, 11, 12], float_format='{0:.0f}'.format, index=False))
        File.write('\n<br>\n')
        
        # Teleop Columns
        # Cube Moving
        File.write(Scoutdf[Scoutdf.team == TeamNumber].to_html(columns=[1, 2, 14, 15, 16, 17, 18], float_format='{0:.0f}'.format, index=False))
        File.write('\n<br>\n')
        
        # Climbing and Parking
        File.write(Scoutdf[Scoutdf.team == TeamNumber].to_html(columns=[1, 2, 29, 30, 31, 32], float_format='{0:.0f}'.format, index=False))
        File.write('\n<br>\n')
        
        # Other Enumerated items
        File.write(Scoutdf[Scoutdf.team == TeamNumber].to_html(columns=[1, 2, 19, 33, 34], float_format='{0:.0f}'.format, index=False))
        File.write('\n<br>\n')
                 
                 
        # Bad Stuff
        File.write(Scoutdf[Scoutdf.team == TeamNumber].to_html(columns=[1, 2, 20, 21, 22, 23, 24, 25, 26, 27], float_format='{0:.0f}'.format, index=False))
        File.write('\n<br>\n')

        '''
        File.write(Scoutdf[Scoutdf.team == TeamNumber].to_html(float_format='{0:.0f}'.format, index=False))
        
        
                              
        
def TeamStats(TeamDf):
    '''
    Takes full dataframe, and creates per match calculated values. Creates a pivot
    dataframe with overall team statistics
    '''
    # Normalize column names
    # Database renamed match and team to matchNo and teamNo.  We put back.
    TeamDf.rename(columns = {'teamNo':'team', 'matchNo': 'match'}, inplace = True)
    
    # Calculate cube usage
    TeamDf['avgtelecargo'] = TeamDf['teleCargoCargo'] + TeamDf['TeleCargoHRocketCargo'] 
    TeamDf['avgtelecargo'] += TeamDf['TeleCargoMRocketCargo'] 
    TeamDf['avgtelecargo'] += TeamDf['TeleCargoLRocketCargo']
  
    TeamDf['avgsandcargo'] = TeamDf['SSCargoCargo'] + TeamDf['SSCargoSSHRocketCargo']
    TeamDf['avgsandcargo'] += TeamDf['SSCargoSSMRocketCargo']
    TeamDf['avgsandcargo'] += TeamDf['SSCargoSSLRocketCargo']
    
    TeamDf['avgtelehatch'] = TeamDf['teleCargoHatch'] + TeamDf['TeleHatchHRocketHatch']
    TeamDf['avgtelehatch'] += TeamDf['TeleHatchMRocketHatch']
    TeamDf['avgtelehatch'] += TeamDf['TeleHatchLRocketHatch']
    
    TeamDf['avgsandhatch'] = TeamDf['SSCargoHatch'] + TeamDf['SSCargoSSHRocketHatch']
    TeamDf['avgsandhatch'] += TeamDf['SSCargoSSMRocketHatch']
    TeamDf['avgsandhatch'] += TeamDf['SSCargoSSLRocketHatch']
    
    # Calculate climbs
    #TeamDf['totalclimbs'] = TeamDf['endClimbedCenter'] + TeamDf['endClimbedSide']
    #TeamDf['totalclimbs'] = TeamDf['endClimbedRamp'] + TeamDf['endDeployRamp']
    
    tempDf = TeamDf[['team', 'reachLvl1','reachLvl2','reachLvl3']]
    climbDf = pd.pivot_table(tempDf,values=['reachLvl1','reachLvl2','reachLvl3'],index=['team'],
                             columns=['reachLvl1', 'reachLvl2', 'reachLvl3'], aggfunc=len, fill_value=0)
    print(climbDf)
    climbDf.reset_index(inplace = True)
    
    #TeamDf['PostiveComments'] = TeamDf['postCommentsPro'] 
    
    TeamDf['totalmatches'] = 1
    
    AvgTeamPivot = pd.pivot_table(TeamDf, values = ['avgtelecargo', 'avgsandcargo', 'avgtelehatch', 'avgsandhatch'], index = 'team', aggfunc = np.average)
    MatchCount = pd.pivot_table(TeamDf, values = ['totalmatches', 'reachLvl1', 'reachLvl2', 'reachLvl3'], index = 'team', aggfunc = np.count_nonzero)
    #Comments = pd.pivot_table(TeamDf, values = ['PositiveComments'], index = 'team', aggfunc = lambda x: ' '.join(x))
    
    AvgTeamPivot.reset_index(inplace = True)
    MatchCount.reset_index(inplace = True)
    #Comments.reset_index(inplace = True)
                                                                               
    TeamPivot = pd.merge(AvgTeamPivot, MatchCount, on = 'team')
    
    TeamPivot = pd.merge(TeamPivot, climbDf, on = 'team')
    
    TeamPivot.rename(columns = {"Did not Try": 'noAttempt', "Attempt Level One Climb": 'attemptLvl1', 
                                "Climbed Level One": 'reachLvl1', "Attempt Level Two Climb": 'attemptLvl2',
                                "Climbed Level Two": 'reachLvl2', "Attempt Level Three Climb": 'attemptLvl3',
                                "Climbed Level Three": 'reachLvl3', "Deployed Ramps": 'deployedRamps', 
                                "Attempted Deploying Ramps": 'attemptDeployedRamps', "Used Another Robot": 'usedAnotherRobot',
                                "Lifted Another Robot": 'lift', "Attempted Lifting Another Robot": 'attemptLift'}, inplace = True)
    
    return TeamDf, TeamPivot


def PickList(TeamDf, PivotDf, lastMatch):
    '''
    List of teams organized by the order we should pick them. Then catagories 
    that rank robotics based on that catagory. Do not pick catagory.
    '''
    #print('inside')
    #print(TeamDf.head())
    earlyDf = TeamDf[TeamDf.match <= lastMatch]
    lateDf = TeamDf[TeamDf.match > lastMatch]
        

    earlytelepivot = pd.pivot_table(earlyDf, values = ['avgtelecargo'], index = 'team', aggfunc = np.average)
    latetelepivot = pd.pivot_table(lateDf, values = ['avgtelecargo'], index = 'team', aggfunc = np.average)
    
    earlytelepivot.reset_index(inplace = True)
    latetelepivot.reset_index(inplace = True)
    #print(earlytelepivot.head())
    #print(latetelepivot.head())
    print(PivotDf.head())
    deltaDf = pd.merge(earlytelepivot, latetelepivot, on = 'team', suffixes = ('_early', '_late'))
    
    
    deltaDf['change'] = deltaDf['avgtelecargo_late'] - deltaDf['avgtelecargo_early']
    deltaDf.sort_values('change')  
    
   # deltaDf['HatchChange'] = deltaDf['avgtelehatch_late'] - deltaDf['avgtelehatch_early']
   # deltaDf.sort_values('HatchChange')
    
    outfile = 'Picklist.xlsx'
    with pd.ExcelWriter(outfile) as writer:
        TeamDf = deltaDf.sort_values(by = 'team')   
        tabname = 'Raw Data'
        TeamDf.to_excel(writer, tabname, index=False)
        PivotDf = deltaDf.sort_values(by = ['team'])
        tabname = 'Pivot'
        PivotDf.to_excel(writer, tabname, index=False)
        tabname = 'Changes'
        deltaDf.to_excel(writer, tabname)

     
def enterTeam():
     Team = input('enter team number: ')
     if Team.isdigit():
        Team = int(Team)
        return Team
     else:
        print('input error')
        return

def Main(testmode):
    print('press 1 to acquire a Match List')
    print('press 2 to get a prematch Scouting Report')
    print('press 3 to get a single team report')
    print('press 4 to get the Day 1 Match Report')
    print('press 5 to get a picklist for Day 2')
    print('press 9 for functional math test')
    selection = input('enter number: ')
    
    if selection == '1':
        event = input('enter event code: ')
        makeMatchList(event)
        
    elif selection == '2':
        Team = enterTeam()       
        ReadData = readScout(testmode)
        MatchList = readMatchList(testmode)
        TeamDf, PivotDf = TeamStats(ReadData)
        Partners = FindPartners(MatchList, Team)
        #matchNum = FindPartners(MatchList, Team)
        MatchReport(Partners, PivotDf, TeamDf, Team)
        
    elif selection == '3':
        Team = int(enterTeam())       
        ReadData = readScout(testmode)
        print(ReadData)
        MatchList = readMatchList(testmode)
        TeamDf, PivotDf = TeamStats(ReadData)
        SearchTeam(TeamDf, PivotDf, Team)
    elif selection == '4':
        ReadData = readScout(testmode)
        TeamDf, PivotDf = TeamStats(ReadData)
        Day1Report(TeamDf, PivotDf)
    elif selection == '5':
        ReadData = readScout(testmode)
        TeamDf, PivotDf = TeamStats(ReadData)
        lastMatch = int(input('enter last match of Day 1'))
        print('boo')
        print(TeamDf.head())
        PickList(TeamDf, PivotDf, lastMatch)
    elif selection == '9':
        ReadData = readScout(testmode)
        print(ReadData)
        TeamDf, PivotDf = TeamStats(ReadData)
        
        print()
        print('TeamDF')
        print(TeamDf)
        print('\nTeam Pivot')
        print(PivotDf)
        
        
Main(True)
      
                
                      
                     







