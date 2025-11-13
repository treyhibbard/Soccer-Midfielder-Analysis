import json
import math
import os
from skillcorner.client import SkillcornerClient

# Initialize the SkillCorner client
client = SkillcornerClient(username='jes0153@auburn.edu', password='WarEagle1')

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def analyze_ball_movement(matchID):
    """
    Analyzes ball movement and calculates distances from all players to the ball
    for processed tracking data files.
    """
    input_file = f"{matchID}TrackingData.json"
    output_file = f"{matchID}_BallAnalysis.json"
    
    # Read the processed tracking data
    try:
        with open(input_file, 'r') as f:
            tracking_data = json.load(f)
    except Exception as e:
        print(f"Error reading file {input_file}: {e}")
        return None
    
    analysis_results = {
        'match_id': matchID,
        'frames': []
    }
    
    # Analyze each frame
    for frame in tracking_data:
        ball_data = None
        player_distances = []
        
        # Find the ball in this frame
        for track in frame['data']:
            if track['track_id'] == 55:  # Ball ID
                ball_data = {
                    'position': {
                        'x': track['x'],
                        'y': track['y']
                    },
                    'timestamp': frame['timestamp'],
                    'frame': frame['frame'],
                    'period': frame['period']
                }
                break
        
        if ball_data:
            # Calculate distance from all players to the ball
            for track in frame['data']:
                if track['track_id'] != 55:  # Skip the ball itself
                    distance = calculate_distance(
                        ball_data['position']['x'],
                        ball_data['position']['y'],
                        track['x'],
                        track['y']
                    )
                    
                    player_distances.append({
                        'track_id': track['track_id'],
                        'distance': round(distance, 2),
                        'position': {
                            'x': track['x'],
                            'y': track['y']
                        }
                    })
            
            # Sort players by distance to ball
            player_distances.sort(key=lambda x: x['distance'])
            
            # Add frame analysis to results
            frame_analysis = {
                'timestamp': ball_data['timestamp'],
                'frame': ball_data['frame'],
                'period': ball_data['period'],
                'ball_position': ball_data['position'],
                'possession': frame.get('possession'),
                'closest_player': player_distances[0] if player_distances else None,
                'player_distances': player_distances
            }
            
            analysis_results['frames'].append(frame_analysis)
    
    # Save analysis results
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=4)
    
    print(f"Ball movement analysis for match {matchID} saved to {output_file}")
    return analysis_results

# Function to process multiple matches
def analyze_all_matches(match_ids):
    results = []
    for match_id in match_ids:
        print(f"\nAnalyzing match {match_id}")
        result = analyze_ball_movement(match_id)
        if result:
            results.append(result)
    return results

# Main execution
if __name__ == "__main__":
    print("START")
    
    # Get the match IDs
    matches = client.get_matches(params={'team': 2334, 'competition_edition': 800})
    match_ids = [match['id'] for match in matches]
    
    print("LIST OF ORLANDO MATCH IDs FOR THE competition_edition WITH id: 800")
    print(match_ids, end='\n\n')
    
    print("Starting ball movement analysis...")
    analysis_results = analyze_all_matches(match_ids)
    print("\nAnalysis complete!")
    
    print("\nEND")