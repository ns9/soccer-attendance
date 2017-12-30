#!/usr/bin/env python

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_num_players(service,timeMin,timeMax,string_filter = '',debug_print=True):

    eventsResult = service.events().list(
        calendarId='primary', timeMin=timeMin, timeMax=timeMax, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    attendance = dict()
    if not events:
	if(debug_print):
		print('No games found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if (string_filter in event['summary']):
		if(debug_print):
			print('\n',start, event['summary'])
			print('	Players:')
		
		total_num_players = 0
		for attendee in event['attendees']:
			if ('accepted' in attendee['responseStatus']):
				total_num_players = total_num_players + 1
				if not attendee['email'] in attendance:
					attendance[attendee['email']] = 1
				else:	
					attendance[attendee['email']] += 1
				if(debug_print):
					print('	',attendee['email'],attendee['responseStatus'])
		if(debug_print):
			print('	Total Number of Players: ',total_num_players)

    return attendance



def main():
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    start_of_season = datetime.datetime(2017,9,8,00).isoformat() + 'Z'

    attendance = get_num_players(service,start_of_season,now,'Quincy',debug_print=True)

    num_games = 6;
    ref_fee = 15;
    season_fee = 650;
    total_season_cost = season_fee + ref_fee*num_games
    total_season_players = sum(attendance.values())
    per_player_cost = dict() 
   
    for player,games_played in attendance.items():
	per_player_cost[player] = games_played*total_season_cost/total_season_players
   
    print('\n\n*********SUMMARY*********\n\n') 
    print('Number of games this season:',num_games)
    print('Total season cost: $',total_season_cost)
    for player in per_player_cost:
	print('\n',player)
	print(' Games played:',attendance[player]) 
	print(' Season fee $',per_player_cost[player]) 

if __name__ == '__main__':
    main()

