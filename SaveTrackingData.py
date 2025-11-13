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
    if timestamp:
        # Split the timestamp into hours, minutes, and seconds
        parts = timestamp.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        
        # Convert the timestamp to milliseconds
        total_seconds = (hours * 3600 + minutes * 60 + seconds)
        
        # Decimal is milliseconds part
        return float(total_seconds)
    return None


'''
Takes in the matchID number and saves a file with the name formatted "matchID"+"TrackingData".
If the file name being written already exists, it overwrites it.
'''
def downloadMatchTrackingData(matchID):
    fileName = f"{matchID}TrackingData.json"
    # Delete the file if it exists
    if os.path.exists(fileName):
        os.remove(fileName)
        print(f"\nExisting file {fileName} deleted.")
    
    # Save the match tracking data
    client.save_match_tracking_data(filepath=fileName, match_id=str(matchID))
    print(f"\nTracking data for {matchID} has been saved.")

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


'''
Get ride of all points when the time is not divisible by .5,
then get rid of unnecessary information.
'''
def shrinkFile(fileArray):
    # Only take every half second of data
    for i in range(len(fileArray) - 1):
        # Sets indicies with timestamps that are empty to None
        if (fileArray[i]['timestamp'] == None):
            fileArray[i] = None
        # Sets indicies with timestamps not divisible by .5 to None
        else:
            divisibleCheck = (reformat_timestamp(fileArray[i]['timestamp']) % .5 == 0)
            if (divisibleCheck == False):
                fileArray[i] = None
    # Deletes all indicies with value 'None'
    filteredData = [item for item in fileArray if item is not None]
    ########################################
    # Remove unnecessary information
    for i in range(len(filteredData)):
        for j in range(len(filteredData[i]['data'])):
            del filteredData[i]['data'][j]['trackable_object']
            del filteredData[i]['data'][j]['is_visible']
        filteredData[i]['possession'] = filteredData[i]['possession']['group']
        del filteredData[i]['image_corners_projection']
    return filteredData




'''
Does everything in one step
Downloads ALL match tracking data and then shrinks it.
'''
def downloadTrackingDataShrink(matchID):
    # Downloads ALL match tracking data
    downloadMatchTrackingData(matchID)
    # Initialize the file name and read the file into python
    fileName = f"{matchID}TrackingData.json"
    fileArray = readFile(fileName)
    # Filter the data by every .5 seconds and remove unnecessary information
    filteredData = shrinkFile(fileArray)
    # Overwrite the existing file with tbe shrunk file
    with open(fileName, "w") as file:
        json.dump(filteredData, file, indent=4)  # indent=4 makes the JSON more readable

'''
Using everything together to download all of the tracking data for every Orlando game...
'''
matches = client.get_matches(params={'team': 2334, 'competition_edition': 800})
print("LIST OF ORLANDO MATCH IDs FOR THE competition_edition WITH id: 800")
matchesIDs = []
for i in range(len(matches)):
    matchesIDs.append(matches[i]['id'])
print(matchesIDs, end='\n\n')

for i in range(len(matchesIDs)):   
    downloadTrackingDataShrink(matchesIDs[i])

print("\nEND")