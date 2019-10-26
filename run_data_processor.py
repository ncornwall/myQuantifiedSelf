from activity_enums import ActivitySource, ActivityType

import json
import itertools

from datetime import datetime
from dateutil.parser import parse
import pytz

from pandas.io.json import json_normalize
import pandas as pd

class RunDataProcessor:

    def __init__(self, requestor):
        self.requestor = requestor

        self.data_frame_columns = ['start_timestamp', 
                            'duration_in_min', 
                            'distance_in_km', 
                            'activity_type',
                            'source']

        self.all_activities = pd.DataFrame(columns=self.data_frame_columns)

    def convert_strava_activity_type(self, x):
        if x == "Run":
            return ActivityType.RUN
        elif x == "Ride":
            return ActivityType.BIKE
        else:
            return ActivityType.OTHER

    def add_strava_data_to_activities(self):
        strava_data = json.dumps(self.requestor.get_json_activities(ActivitySource.STRAVA))
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
        strava_df['activity_type'] = strava_df['type'].apply(lambda x: self.convert_strava_activity_type(x))
        strava_df['duration_in_min'] = strava_df['elapsed_time'].apply(lambda x: x / 60)
        strava_df['source'] = ActivitySource.STRAVA
        # strava_df = strava_df.drop(columns=['start_date_local', 'distance', 'type', 'elapsed_time'], axis=1)

        strava_df = strava_df.filter(self.data_frame_columns)
        self.all_activities = self.all_activities.append(strava_df, sort=True)

    def add_nike_data_to_activities(self):  
        nike_df = json_normalize(self.requestor.get_json_activities(ActivitySource.NIKE))
        summaries = json_normalize(self.requestor.get_json_activities(ActivitySource.NIKE), record_path="summaries", record_prefix="summaries.", meta="id")
        summaries = summaries[summaries['summaries.metric'] == "distance"]
        nike_df = pd.merge(nike_df, summaries, how='inner', on='id')

        nike_df['start_timestamp'] = nike_df['start_epoch_ms'].apply(lambda x: datetime.fromtimestamp(x / 1000, pytz.timezone('America/Vancouver')))
        nike_df['distance_in_km'] = nike_df['summaries.value']
        nike_df['activity_type'] = ActivityType.RUN
        nike_df['duration_in_min'] = nike_df['active_duration_ms'].apply(lambda x: x / 1000 / 60)
        nike_df['source'] = ActivitySource.NIKE

        nike_df = nike_df.filter(self.data_frame_columns)
        self.all_activities = self.all_activities.append(nike_df, sort=True, ignore_index=True)

    def load_apple_workouts(self):
        print("Getting csv data for apple data")
        workouts_filepath = 'data/apple_health_export_csv/Workout.csv'
        return pd.read_csv(workouts_filepath, sep=',')

    def remove_duplicates(self, activities):
        before_len = len(activities)
        for a, b in itertools.combinations(activities, 2):
            if a.isDuplicate(b):
                if a in activities:
                    activities.remove(a)
        print(f"Removed {before_len - len(activities)} duplicates")