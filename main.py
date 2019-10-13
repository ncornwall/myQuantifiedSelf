from json_run_data_api import JsonRunDataRequestor, ActivityType
from datetime import datetime
from activity import Activity
from dateutil.parser import parse
import itertools
import pytz
from functools import reduce
import pandas as pd
import numpy as np

requestor = JsonRunDataRequestor()

def merge_strava_nike_apple_data():
    strava_data = requestor.get_json_activities(ActivityType.STRAVA)

    merged_activity = []

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

    for workout in apple_data:
        print('a')

    return merged_activity

def load_apple_workouts():
    workouts_filepath = 'data/apple_health_export_csv/Workout.csv'
    myFile = pd.read_csv(workouts_filepath, sep=',')
    return []

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
    activities = merge_strava_nike_apple_data()
    remove_duplicates(activities)
    calc_total_distance_run(activities)

if __name__ == "__main__":
    main()
