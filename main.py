from json_run_data_api import JsonRunDataRequestor, ActivitySource
from activity import Activity

from datetime import datetime
from dateutil.parser import parse
import itertools
import pytz
from functools import reduce
import pandas as pd
import numpy as np
import json
from pandas.io.json import json_normalize
from enum import Enum

def set_pandas_display_options() -> None:
    display = pd.options.display
    display.max_columns = 1000
    display.max_rows = 1000
    display.max_colwidth = 199
    display.width = None
    # display.precision = 2  # set as needed

class ActivityType(Enum):
    RUN = "run"
    BIKE = "bike"
    SWIM = "swim"
    OTHER = "other"

class RunDataProcessor:

    def __init__(self, requestor):
        self.requestor = requestor

        self.data_frame_columns = ['start_timestamp', 
                            'duration_in_min', 
                            'distance_in_km', 
                            'activity_type',
                            'source']

        self.all_activities = pd.DataFrame(columns=self.data_frame_columns)

    def merge_strava_nike_apple_data():

        merged_activity = []

        strava_data = self.requestor.get_json_activities(ActivitySource.STRAVA)

        for activity in strava_data:
            if activity['type'] == "Run":
                id = activity['id']
                start_time = parse(activity['start_date_local'], tzinfos={"America/Vancouver"})
                distance_in_km = activity['distance'] / 1000
                merged_activity.append(Activity(id, start_time, distance_in_km, ActivitySource.STRAVA, activity))

        nike_data = self.requestor.get_json_activities(ActivitySource.NIKE)

        for activity in nike_data:
            id = activity['id']
            start_time = datetime.fromtimestamp(activity['start_epoch_ms'] / 1000, pytz.timezone('America/Vancouver'))
            distance_in_km = None
            summaries = activity['summaries']
            for summary in summaries:
                if summary['metric'] == "distance":
                    distance_in_km = summary['value']
                    break
            merged_activity.append(Activity(id, start_time, distance_in_km, ActivitySource.NIKE, activity))

        apple_data = self.load_apple_workouts()
        filtered_apple_data = apple_data[(apple_data.workoutActivityType == "HKWorkoutActivityTypeRunning") & (apple_data.sourceName == "Natalia's Apple Watch")]
        filtered_apple_data.apply(lambda x:  merged_activity.append(Activity(None, 
                    parse(x.startDate, tzinfos={"America/Vancouver"}),
                    x.totalDistance, 
                    ActivitySource.APPLE, None)), axis=1)
        return merged_activity

    def convert_strava_activity_type(x):
        if x == "Run":
            return ActivityType.RUN
        elif x == "Ride":
            return ActivityType.BIKE
        else:
            return ActivityType.OTHER

    def add_strava_data_to_data_frame(all_activities):
        strava_data = json.dumps(requestor.get_json_activities(ActivitySource.STRAVA))
        strava_df = pd.read_json(strava_data)
        strava_df = strava_df[['distance', 
            'elapsed_time', 
            'start_date_local', 
            'location_city', 
            'average_speed', 
            'max_speed', 
            'type']]

        strava_df['start_timestamp'] = strava_df['start_date_local'].apply(lambda x: parse(x, tzinfos={"America/Vancouver"}))
        strava_df['distance_in_km'] = strava_df['distance'].apply(lambda x: x / 1000)
        strava_df['activity_type'] = strava_df['type'].apply(lambda x: convert_strava_activity_type(x))
        strava_df['duration_in_min'] = strava_df['elapsed_time'].apply(lambda x: x / 60)
        strava_df['source'] = ActivitySource.STRAVA
        # strava_df = strava_df.drop(columns=['start_date_local', 'distance', 'type', 'elapsed_time'], axis=1)
        strava_df = strava_df.filter(data_frame_columns)

        return all_activities.append(strava_df, sort=True)

    def add_nike_data_to_data_frame(all_activities):  
        nike_df = json_normalize(requestor.get_json_activities(ActivitySource.NIKE))
        summaries = json_normalize(requestor.get_json_activities(ActivitySource.NIKE), record_path="summaries", record_prefix="summaries.", meta="id")
        summaries = summaries[summaries['summaries.metric'] == "distance"]
        nike_df = pd.merge(nike_df, summaries, how='inner', on='id')

        nike_df['start_timestamp'] = nike_df['start_epoch_ms'].apply(lambda x: datetime.fromtimestamp(x / 1000, pytz.timezone('America/Vancouver')))
        nike_df['distance_in_km'] = nike_df['summaries.value']
        nike_df['activity_type'] = ActivityType.RUN
        nike_df['duration_in_min'] = nike_df['active_duration_ms'].apply(lambda x: x / 1000 / 60)
        nike_df['source'] = ActivitySource.NIKE
        nike_df = nike_df.filter(data_frame_columns)

        return all_activities.append(nike_df, sort=True, ignore_index=True)

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

def main():
    set_pandas_display_options()

    # activities = merge_strava_nike_apple_data()
    # remove_duplicates(activities)
    # calc_total_distance_run(activities)

    requestor = JsonRunDataRequestor()
    processor = RunDataProcessor(requestor)

    all_activities = add_strava_data_to_data_frame(all_activities)
    all_activities = add_nike_data_to_data_frame(all_activities)

    sum = all_activities[all_activities['activity_type'] == ActivityType.RUN]['distance_in_km'].sum()
    print(f'Total running distance: {sum}')




if __name__ == "__main__":
    main()
