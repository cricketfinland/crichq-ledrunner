#!/usr/bin/env python3
import crichq_ledrunner_config as cfg
import crichq_ledrunner_fixtures as unsafe
import requests
import sys
import ctypes
import datetime
import time
#import tkinter
import pygame
import signal
import os
#import lockfile
import importlib
#import logging

def new_fixtures(signum, frame):
    importlib.reload(unsafe)
    return

def team_abbreviation(team_name):
    team_name_parts = team_name.split(',')
    team_name = team_name_parts[1]
    team_name = team_name.strip()
    team_name = team_name.title()
    return(team_name)

def update_screen_small(line1=' ', line2=' ', line3=' ', line4=' '):
    text1 = font_small.render(line1, True, (255, 255, 255))
    text2 = font_small.render(line2, True, (255, 255, 255))
    text3 = font_small.render(line3, True, (255, 255, 255))
    text4 = font_small.render(line4, True, (255, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(text1, (0, 0))
    screen.blit(text2, (0, startRowVert1))
    screen.blit(text3, (0, startRowVert2))
    screen.blit(text4, (0, startRowVert3))
    pygame.display.flip()
    return

def update_screen(line1=' ', line2=' ', line3=' ', line4=' '):
    text1 = font.render(line1, True, (255, 255, 255))
    text2 = font.render(line2, True, (255, 255, 255))
    text3 = font.render(line3, True, (255, 255, 255))
    text4 = font.render(line4, True, (255, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(text1, (0, 0))
    screen.blit(text2, (0, startRowVert1))
    screen.blit(text3, (0, startRowVert2))
    screen.blit(text4, (0, startRowVert3))
    pygame.display.flip()
    return

#with daemon.DaemonContext(
#    signal_map={signal.SIGHUP: new_fixtures},
#    pidfile=lockfile.FileLock('/var/run/crichq-ledrunner.pid')
#):

signal.signal(signal.SIGHUP, new_fixtures)
base_url = 'https://www.crichq.com/'
#logging.basicConfig(filename='/var/log/crichq-ledrunner.log', level=logging.DEBUG)

#os.environ['SDL_VIDEODRIVER'] = "FBCON"
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,100"

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

font = pygame.font.SysFont("arial", unsafe.fontsize)
font_small = pygame.font.SysFont("arial", unsafe.fontsize_small)
startRowVert1 = unsafe.fontsize + 2
startRowVert2 = startRowVert1 * 2
startRowVert3 = startRowVert1 * 3
update_screen_small("Initialising")
clock.tick(60)

# This code may be useful for more intelligent led setups, but for a system
# relying on the led screen displaying the led screen resolution worth of 
# top-left corner it really has no use
#print(unsafe.display_width)
#print(unsafe.display_height)

# Polling CricHQ to find out whether a match is currently played at the cricket
# ground selected in the configuration file

s_crichq = requests.Session()

while 1:
    live_match_found = False
    if unsafe.fixtures != 0:
        fixture = str(unsafe.fixtures)
        fixture = str(fixture)
        fix = s_crichq.get(base_url + 'api/v2/public/fixtures/' + fixture + '?api_token=' + cfg.crichq_token)
        fix_dict = fix.json()
        if fix.status_code == 404:
            print('Invalid fixture id!')
            update_screen_small("Invalid fixture id!")
        #DEBUG CODE: print contents of fixture info
        #print (fix_dict)
        #DEBUG CODE: print fixture id

        print('Checking for fixture: ' + fixture)
        if fix.status_code != 404:
            if fix_dict['active_match'] is not None:                
                match_id_list = fix_dict['active_match']
                #DEBUG CODE: print live fixture found
                print('Active match found! Matchid: ' + str(match_id_list['id'])) 
                match_id = str(match_id_list['id'])
                match = s_crichq.get(base_url + 'api/v2/public/matches/' + match_id + '?api_token=' + cfg.crichq_token)
                match_dict = match.json()
                if match_dict['is_live'] is True and match_dict['match_status'] == 2:
                    live_match_found = True
                    print('Live match found, is_live is true and match_status 2.')
                else:
                    print('Waiting for live match, fixture:' + fixture + ', matchid:' + match_id)
                    line2 = 'Fixture id: %s' % (fixture)
                    line3 = 'Match id: %s' % (match_id)
                    update_screen_small("Waiting for match!", line2, line3, "Enable Live Updates in CricHQ settings!")
            else:
                print('Waiting for live match, fixture:' + fixture)
                line2 = 'Fixture: %s' % (fixture)
                update_screen_small("Waiting for match!", line2, "Start match and turn on", "Live Updates in CricHQ settings!")

    elif unsafe.fixtures == 0 and unsafe.crichq_match_id != 0:
        match_id = str(unsafe.crichq_match_id)
        live_match_found = True

    elif unsafe.crichq_match_id == 0 and unsafe.fixtures == 0 and unsafe.location != 0:
        #DEBUGGING CODE: API request
        print(base_url + 'api/v2/public/match_center/in_progress?search[q]=' + unsafe.location + '&api_token=' + cfg.crichq_token)
        
        #s_matches.headers.update({'X-USER-EMAIL'=cfg.crichq_user, 'X-USER-TOKEN'=cfg.crichq_token})
        matches = s_crichq.get(base_url + 'api/v2/public/match_center/in_progress?search[q]=' + unsafe.location + '&api_token=' + cfg.crichq_token)
        # DEBUG CODE: finding out the time it takes for the API to return info and writing the
        # time to a log file
        #elapsed = matches.elapsed.total_seconds()
        #print (elapsed)
        #logging.debug('Request turnaround time: ' + elapsed)
        
        #DEBUGGING CODE: what comes from the API
        #print(matches.json())
        
        matches_dict = matches.json()
        matches_list = matches_dict['items']
        for match in matches_list:
            match_ground = match['ground']
            if match_ground['id'] == unsafe.ground_id:
                match_id = match['id']
                #DEBUGGING CODE: is the match identified correctly?
                #print('Match found, id:', match_id)
                update_screen_small("Live match found!")
                live_match_found = True
                matches = 0

    else:
        update_screen_small("No match config!")

    # Start the live match following loop
    if live_match_found is True:
        live_match_ended = False
        innings_number = 0
        while live_match_ended is not True:
            check_fixture = str(unsafe.fixtures)
            if fixture != check_fixture:
                print('Fixture does not match check fixture, fixture:' + fixture + ', check:' + check_fixture)
                break
            #DEBUG CODE: announce finding a live match
            #print('Live match found!')
            
            update = s_crichq.get(base_url + 'api/v2/public/matches/' + match_id + '/live?api_token=' + cfg.crichq_token)
            
            #DEBUG CODE: print the turnaround time for the API query
            print(update.elapsed.total_seconds())
            update_dict = update.json()
            
            #DEBUG CODE: print the update dictionary
            #print(update_dict)
            innings_list = update_dict['innings']
            try:
                partnership = update_dict['currentPartnership']
            except KeyError:
                partnership_exists = False
                print('No partnership data') 
            else:
                partnership_exists = True 
            #DEBUG CODE: print the contents of the innings list object
            #print(innings_list)
            print('Inns: ', innings_number, ' of ', end='')
            #innings_number = 0
            try:
                innings = innings_list[innings_number]
            except IndexError:
                print('Waiting for new innings to start')
                time.sleep(10)
            else:
                if innings['endStatus'] != 0 and innings['endStatus'] != 1:
                    innings_number += 1 
                else:
                    #First screen
                    team_abbrev = team_abbreviation(innings['battingTeam'])
                    #DEBUG CODE: print the live stats
                    #print(innings['battingTeam'], '-', innings['bowlingTeam'])
                    print(team_abbrev, ', ', end='')
                    print('Score:', innings['runs'], '/', innings['wickets'], ' @ ', innings['overs'], '.', innings['overBalls'], ', ', end='')
                    if innings_number != 0:
                        print('To win:', update_dict['targetRuns'])
                    else:
                        print('RPO:', update_dict['currentRPO'])
                    #END DEBUG BLOCK
                    #team_abbrev = team_abbreviation(innings['battingTeam'])
                    line1 = '%s' % (team_abbrev)
                    line2 = 'Total: %s/%s' % (innings['runs'], innings['wickets'])
                    line3 = 'Overs: %s.%s' % (innings['overs'], innings['overBalls'])
                    if innings_number != 0:
                        line4 = 'To win: %s' % (update_dict['targetRuns'])
                    else:
                        line4 = 'RPO: %s' % (update_dict['currentRPO'])
                    update_screen(line1, line2, line3, line4)
                    time.sleep(7)
                    #Second screen
                    try:
                        currentFacingBatsmanIndex = update_dict['currentFacingBatsmanIndex']
                    except KeyError:
                        facingbatsman_exists = False
                    else:
                        facingbatsman_exists = True
                    
                    try:    
                        currentNonFacingBatsmanIndex = update_dict['currentNonFacingBatsmanIndex']
                    except KeyError:
                        nonfacingbatsman_exists = False
                    else: 
                        nonfacingbatsman_exists = True

                    scorecard_list = update_dict['scorecards']
                    scorecard = scorecard_list[innings_number]
                    scorecard_batting = scorecard['batting']
                    batting_list = scorecard_batting['players']
                    if facingbatsman_exists == True:
                        try:
                            facingbatsman_index = batting_list[currentFacingBatsmanIndex]
                        except TypeError:
                            facingbatsman_exists = False
                        else:
                            facingbatsman_exists = True
                            facingbatsman_name = facingbatsman_index['name']
                            facingbatsman_name.strip()
                            facingbatsman_name.title()
                            facingbatsman_words = facingbatsman_name.split(' ')
                            facingbatsman = ''
                            for word in facingbatsman_words:
                                try:
                                    facingbatsman = facingbatsman + word[0]
                                except IndexError:
                                    pass
                    
                    if nonfacingbatsman_exists == True:
                        try:
                            nonfacingbatsman_index = batting_list[currentNonFacingBatsmanIndex]
                        except TypeError:
                            nonfacingbatsman_exists = False
                        else:
                            nonfacingbatsman_exists = True
                            nonfacingbatsman_name = nonfacingbatsman_index['name']
                            nonfacingbatsman_name.strip()
                            nonfacingbatsman_name.title()
                            nonfacingbatsman_words = nonfacingbatsman_name.split(' ')
                            nonfacingbatsman = ''
                            for word in nonfacingbatsman_words:
                                try:
                                    nonfacingbatsman = nonfacingbatsman + word[0]
                                except IndexError:
                                    pass
                    #DEBUG CODE to stdout
                    if facingbatsman_exists == True:
                        print(facingbatsman, ':', facingbatsman_index['runs'], '(', facingbatsman_index['balls'], ') / ', end='') 
                    else:
                        print('No facing batsman /', end='')
                    if nonfacingbatsman_exists == True:
                        print(nonfacingbatsman, ':', nonfacingbatsman_index['runs'], '(', nonfacingbatsman_index['balls'], ') / ', end='')
                    else:
                        print('No non-facing batsman /', end='')

                    if partnership_exists == True:
                        try:
                            print('Partnership:', partnership['runs'], '(', partnership['balls'], ')')
                        except TypeError:
                            print('No p\'ship data.')
                    else:
                        print('No p\'ship data.')
                    #END DEBUG CODE
                    if facingbatsman_exists == True:
                        line1 = '%s: %s(%s)' % (facingbatsman, facingbatsman_index['runs'], facingbatsman_index['balls'])
                    else:
                        line1 = ' '
                    
                    if nonfacingbatsman_exists == True:
                        line2 = '%s: %s(%s)' % (nonfacingbatsman, nonfacingbatsman_index['runs'], nonfacingbatsman_index['balls'])
                    else:
                        line2 = ' '

                    if partnership_exists == True:
                        try:
                            line3 = 'Ptrship: %s(%s)' % (partnership['runs'], partnership['balls'])
                        except TypeError:
                            line3 = ' '
                    else:
                        line3 = ' '
                    update_screen(line1, line2, line3, line4)
                    time.sleep(8)
                
            update = s_crichq.get(base_url + 'api/v2/public/matches/' + match_id + '?api_token=' + cfg.crichq_token)
            update_dict = update.json()
            if update_dict['is_live'] is False and update_dict['match_status'] == 3:
                live_match_ended = True
                live_match_found = False
                print('Live match ended')
                break

    print('No live match found')
    time.sleep(5)