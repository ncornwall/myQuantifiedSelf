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
from pandas.io.json import json_normalize

requestor = JsonRunDataRequestor()

def set_pandas_display_options() -> None:
    display = pd.options.display

    display.max_columns = 1000
    display.max_rows = 1000
    display.max_colwidth = 199
    display.width = None
    # display.precision = 2  # set as needed

def merge_strava_nike_apple_data():

    merged_activity = []

    strava_data = requestor.get_json_activities(ActivityType.STRAVA)

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

def add_strava_data_to_data_frame(all_activities):
    strava_data = json.dumps(requestor.get_json_activities(ActivityType.STRAVA))
    strava_df = pd.read_json(strava_data)
    strava_df = strava_df[['distance', 
        'elapsed_time', 
        'start_date_local', 
        'location_city', 
        'average_speed', 
        'max_speed', 
        'type']]

    strava_df['start_time'] = strava_df['start_date_local'].apply(lambda x: parse(x, tzinfos={"America/Vancouver"}))
    strava_df['distance_in_km'] = strava_df['distance'].apply(lambda x: x / 1000)
    strava_df['activity_type'] = strava_df['type']
    strava_df['duration'] = strava_df['elapsed_time']
    strava_df['source'] = ActivityType.STRAVA
    strava_df = strava_df.drop(columns=['start_date_local', 'distance', 'type', 'elapsed_time'], axis=1)

    all_activities = all_activities.append(strava_df, sort=True)

def add_nike_data_to_data_frame(all_activities):  
    nike_df = json_normalize(requestor.get_json_activities(ActivityType.NIKE))
    summaries = json_normalize(requestor.get_json_activities(ActivityType.NIKE), record_path="summaries", record_prefix="summaries.", meta="id")
    summaries = summaries[summaries['summaries.metric'] == "distance"]
    nike_df = pd.merge(nike_df, summaries, how='inner', on='id')

    # nike_df = pd.read_json(nike_data, typ='frame', dtype={"id": np.float64,
    #                                                     "articleId": np.float64, 
    #                                                     "start_epoch_ms": np.float64, 
    #                                                     "end_epoch_ms": np.float64,
    #                                                     "last_modified": np.float64,
    #                                                     "timestamp": np.float64})
    nike_df['start_time'] = nike_df['start_epoch_ms'].apply(lambda x: datetime.fromtimestamp(x / 1000, pytz.timezone('America/Vancouver')))
    nike_df['distance_in_km'] = nike_df['summaries.value']
    # nike_df['duration'] = nike_df['active_duration_ms']
    # nike_df['activity_type'] = nike_df['type']
    nike_df['source'] = ActivityType.NIKE

    all_activities = all_activities.append(nike_df, sort=True, ignore_index=True)
    # df['duration'] = df['elapsed_time']
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
    set_pandas_display_options()

    # activities = merge_strava_nike_apple_data()
    # remove_duplicates(activities)
    # calc_total_distance_run(activities)

    all_activities = pd.DataFrame(columns=['start_time', 
                                        'duration', 
                                        'distance_in_km', 
                                        'activity_type'])

    add_strava_data_to_data_frame(all_activities)
    add_nike_data_to_data_frame(all_activities)



if __name__ == "__main__":
    main()
