from json_run_data_api import JsonRunDataRequestor, ActivityType
from datetime import datetime
from activity import Activity
from dateutil.parser import parse
import itertools
import pytz
from functools import reduce
import pandas as pd
import numpy as np
import json

requestor = JsonRunDataRequestor()

def merge_strava_nike_apple_data():
    strava_data = requestor.get_json_activities(ActivityType.STRAVA)

    merged_activity = pd.DataFrame({'start_time': pd.Timestamp, 'end_time': pd.Timestanp, 'duration': float, 'distance': float})

    for activity in strava_data:
        if activity['type'] == "Run":
            id = activity['id']
            start_time = parse(activity['start_date_local'], tzinfos={"America/Vancouver"})
            distance_in_km = activity['distance'] / 1000
            merged_activity.append(Activity(id, start_time, distance_in_km, ActivityType.STRAVA, activity))

    nike_data = requestor.get_json_activities(ActivityType.NIKE)

    for activity in nike_data:
        id = activity['id']
        start_time = datetime.fromtimestamp(activity['start_epoch_ms'] / 1000, pytz.timezone('America/Vancouver'))
        distance_in_km = None
        summaries = activity['summaries']
        for summary in summaries:
            if summary['metric'] == "distance":
                distance_in_km = summary['value']
                break
        merged_activity.append(Activity(id, start_time, distance_in_km, ActivityType.NIKE, activity))

    apple_data = load_apple_workouts()
    filtered_apple_data = apple_data[(apple_data.workoutActivityType == "HKWorkoutActivityTypeRunning") & (apple_data.sourceName == "Natalia's Apple Watch")]
    filtered_apple_data.apply(lambda x:  merged_activity.append(Activity(None, 
                parse(x.startDate, tzinfos={"America/Vancouver"}),
                x.totalDistance, 
                ActivityType.APPLE, None)), axis=1)
    return merged_activity

def merge_strava_nike_apple_data_more_pandas():  

    all_activities = pd.DataFrame(columns=['start_time', 
                                            'duration', 
                                            'distance_in_km', 
                                            'activity_type'])
    
    strava_data = json.dumps(requestor.get_json_activities(ActivityType.STRAVA))
    df = pd.read_json(strava_data)
    df = df[['distance', 
        'elapsed_time', 
        'start_date_local', 
        'location_city', 
        'average_speed', 
        'max_speed', 
        'type']]

    df['start_time'] = df['start_date_local'].apply(lambda x: parse(x, tzinfos={"America/Vancouver"}))
    df['distance_in_km'] = df['distance'].apply(lambda x: x / 1000)
    df['activity_type'] = df['type']
    df['duration'] = df['elapsed_time']
    df = df.drop(columns=['start_date_local', 'distance', 'type', 'elapsed_time'], axis=1)

    all_activities.append(df, sort=True)

    nike_data = json.dumps(requestor.get_json_activities(ActivityType.NIKE))
    df2 = pd.read_json(nike_data, typ='series', dtype={"articleId": np.float64})
    df2 = df2[['type', 
            'start_epoch_ms', 
            'active_duration_ms']]

    df2['start_time'] = df2['start_epoch_ms'].apply(lambda x: datetime.fromtimestamp(x / 1000, pytz.timezone('America/Vancouver')))
    df2['distance_in_km'] = df2['distance'].apply(lambda x: x / 1000)
    df2['activity_type'] = df2['type']
    # df['duration'] = df['elapsed_time']

    df


    # df['date_no_timestamp'] = df['start_date'].apply(lambda x: x.date())
    # df['y_m_d'] = df['start_date'].apply(lambda x: '{}-{}-{}'.format(x.year, x.month, x.day))

def load_apple_workouts():
    print("Getting csv data for apple data")
    workouts_filepath = 'data/apple_health_export_csv/Workout.csv'
    return pd.read_csv(workouts_filepath, sep=',')

def remove_duplicates(activities):
    before_len = len(activities)
    for a, b in itertools.combinations(activities, 2):
        if a.isDuplicate(b):
            if a in activities:
                activities.remove(a)
    print(f"Removed {before_len - len(activities)} duplicates")

def calc_total_distance_run(activities):
    sum = 0
    for a in activities:
        sum += a.distance
    # sum = reduce((lambda x, y: x.distance + y.distance), activities)
    print(f"Total distance run: {sum}")

def main():
    # activities = merge_strava_nike_apple_data()
    # remove_duplicates(activities)
    # calc_total_distance_run(activities)
    merge_strava_nike_apple_data_more_pandas()

if __name__ == "__main__":
    main()
