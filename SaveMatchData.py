import json
import os
from skillcorner.client import SkillcornerClient
client = SkillcornerClient(username='jes0153@auburn.edu', password='WarEagle1')
print("START")

'''
Takes a timestamp in the format of "01:39:17.60" for example and 
returns the time in seconds and millisecond decimals.
'''
def reformat_timestamp(timestamp):
    if (timestamp != None):
        # Split the timestamp into hours, minutes, and seconds
        parts = timestamp.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        # Convert the timestamp to milliseconds
        total_seconds = (hours * 3600 + minutes * 60 + seconds)
        # Decimal is milliseconds part
        return float(total_seconds)
    else:
        return 0

'''
Takes in the matchID number and saves a file with the name formatted "matchID"+"TrackingData".
If the file name being written already exists, it overwrites it.
'''
def downloadMatchData(matchID):
    fileName = f"{matchID}MatchData.json"
    # Delete the file if it exists
    if os.path.exists(fileName):
        os.remove(fileName)
        print(f"\nExisting file {fileName} deleted.")
    
    # Save the match tracking data
    client.save_match(filepath=fileName, match_id=str(matchID))
    print(f"\nMatch data for {matchID} has been saved.")

'''
Reads the .json file and creates an Array structure that we can read and edit in python.
If the file is too large or has an error, an exception is thrown and nothing happens.
'''
def readFile(filePath):
    try:
        # "r" means "reading". There are other options such as "w" for "writing". 
        # We only need to use "r" here, but later when shrinking the file, we will use w to overwrite.
        with open(filePath, "r") as file:
            # If the entire file fits into memory
            loadedFile = json.load(file)
            return loadedFile
    ############################################################
    # ChatGPT said to add these. These are error detection, but there are no errors because we are goated.      
    except MemoryError:
        print("File too large to load at once, consider processing in chunks.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    
def saveRelevantMatchData(fileJson, trackingDataJson):
    newJson = {}
    # Match Info
    newJson['match_id'] = fileJson['id']
    newJson['competition_edition'] = fileJson['competition_edition']['id']
    newJson['date'] = fileJson['date_time'].split('T')[0]
    newJson['home_team'] = fileJson['home_team']['acronym']
    newJson['home_team_id'] = fileJson['home_team']['id']
    newJson['away_team'] = fileJson['away_team']['acronym']
    newJson['away_team_id'] = fileJson['away_team']['id']
    newJson['home_team_score'] = fileJson['home_team_score']
    newJson['away_team_score'] = fileJson['away_team_score']
    lastTimestamp = trackingDataJson[len(trackingDataJson) - 1]['timestamp']
    newJson['match_length_in_seconds'] = reformat_timestamp(lastTimestamp)
    # Players Info
    newJson['players'] = [{} for _ in range(len(fileJson['players']))]
    for i in range(len(fileJson['players'])):
        newJson['players'][i]['role_full_name'] = fileJson['players'][i]['player_role']['name']
        newJson['players'][i]['role'] = fileJson['players'][i]['player_role']['acronym']
        # Uses an if/else statement to do some gymnastics in order to identify the team name
        if fileJson['players'][i]['team_id'] == fileJson['home_team']['id']:
            newJson['players'][i]['team_name'] = newJson['home_team']
        else:
            newJson['players'][i]['team_name'] = newJson['away_team']
        newJson['players'][i]['team_id'] = fileJson['players'][i]['team_id']
        newJson['players'][i]['track_id'] = fileJson['players'][i]['trackable_object']
        newJson['players'][i]['team_player_id'] = fileJson['players'][i]['team_player_id']
        newJson['players'][i]['start_time'] = fileJson['players'][i]['start_time']
        newJson['players'][i]['end_time'] = fileJson['players'][i]['end_time']
        # Uses an if/else statement to check if the time is None (aka null). 
        # First checks if the player never played, then if she never stopped, then if she started after t=0. Calculates time played in seconds.
        # Round(___, 2) makes sure there are no crazy decimal lengths
        if (fileJson['players'][i]['end_time'] == None and fileJson['players'][i]['start_time'] == None):
            newJson['players'][i]['time_played_in_seconds'] = round(newJson['match_length_in_seconds'] - reformat_timestamp(fileJson['players'][i]['start_time']), 2)
        elif (fileJson['players'][i]['end_time'] == None):
            newJson['players'][i]['time_played_in_seconds'] = round(newJson['match_length_in_seconds'] - reformat_timestamp(fileJson['players'][i]['start_time']), 2)
        else:
            newJson['players'][i]['time_played_in_seconds'] = round(reformat_timestamp(fileJson['players'][i]['end_time']) - reformat_timestamp(fileJson['players'][i]['start_time']), 2)
    return newJson

# A main function to do everything needed to create the file for a specific matchID
def main(matchID):
    # Downloads the match data without fixing it
    downloadMatchData(matchID)
    fileName = f"{matchID}MatchData.json"
    fileJson = readFile(fileName)
    trackingDataFileName = f"{matchID}TrackingData.json"
    trackingDataJson = readFile(trackingDataFileName)
    newJson = saveRelevantMatchData(fileJson, trackingDataJson)
    with open(fileName, "w") as file:
        json.dump(newJson, file, indent=4)  # indent=4 makes the JSON more readable


# Iteratively use the main() function with all of matches played by Orlando
matches = client.get_matches(params={'team': 2334, 'competition_edition': 800})
print("LIST OF ORLANDO MATCH IDs FOR THE competition_edition WITH id: 800")
matchesIDs = []
for i in range(len(matches)):
    matchesIDs.append(matches[i]['id'])
for i in range(len(matchesIDs)):   
    main(matchesIDs[i])

print("END")
