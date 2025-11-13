import json
import os
from skillcorner.client import SkillcornerClient
client = SkillcornerClient(username='jes0153@auburn.edu', password='WarEagle1')

# Define the folder containing all match and tracking data files
data_folder = "/Users/treyhibbard/Downloads/DATAPROJECT"
#print(os.getcwd())  # Prints the current working directory
print(os.getcwd())

# Define the roles of midfielders
midfielder_roles = ["LM", "RM", "CM"]

print("START PROCESSING")
filesList = os.listdir(data_folder)

# Loop through all files in the folder
for file_name in filesList:
    if "MatchData.json" in file_name:  # Check if it's a match data file
        match_id = file_name.split("MatchData.json")[0]  # Extract match ID (e.g., 1875301)
        match_file_path = os.path.join(data_folder, file_name)

        # Open and process the match data file
        with open(match_file_path, "r") as match_file:
            match_data = json.load(match_file)

        # Extract midfielder track IDs
        midfielderIDs = [
            player.get("trackable_object") or player.get("track_id")
            for player in match_data.get("players", [])
            if player.get("player_role", {}).get("acronym") in midfielder_roles or player.get("role") in midfielder_roles
        ]

        print(f"Match ID: {match_id}, Midfielder Track IDs: {midfielderIDs}")
 # Process the corresponding tracking data
        tracking_file_name = f"{match_id}TrackingData.json"  # Construct tracking data filename
        tracking_file_path = os.path.join(data_folder, tracking_file_name)

        if os.path.exists(tracking_file_path):  # Check if tracking data file exists
            with open(tracking_file_path, "r") as tracking_file:
                tracking_data = json.load(tracking_file)

            # Filter tracking data for midfielders
            filtered_tracking_data = []
            for frame in tracking_data:
                filtered_frame = {
                    "data": [
                        player
                        for player in frame["data"]
                        if player["track_id"] in midfielderIDs
                    ],
                    "possession": frame.get("possession"),
                    "frame": frame.get("frame"),
                    "timestamp": frame["timestamp"],
                    "period": frame.get("period"),
                }
                if filtered_frame["data"]:  # Only include frames with midfielder data
                    filtered_tracking_data.append(filtered_frame)

            # Save the filtered tracking data to a new JSON file
            output_file = os.path.join(data_folder, f"{match_id}MidfielderTrackingData.json")
            with open(output_file, "w") as output_json:
                json.dump(filtered_tracking_data, output_json, indent=4)

            print(f"Filtered tracking data saved to {output_file}")
        else:
            print(f"Tracking data file not found for match ID {match_id}")