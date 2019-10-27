from activity_enums import ActivitySource, ActivityType

import json
import itertools

from datetime import datetime
from dateutil.parser import parse
import pytz

from pandas.io.json import json_normalize
import pandas as pd

class RunDataCleaner:
    """
    Merges all data sources together and pulls out common fields
    Removes duplicate run data based on similarity
    """

    # A run whose distance is < 1 km different and start time < 10 min apart is a duplicate run
    KM_SIMILARITY_THRESHOLD = 1
    SECONDS_SIMILARITY_THRESHOLD = 600

    def __init__(self, requestor):
        self.requestor = requestor

        self.data_frame_columns = ['start_timestamp', 
                            'duration_in_min', 
                            'distance_in_km', 
                            'activity_type',
                            'source']

        self.all_activities = pd.DataFrame(columns=self.data_frame_columns)

    def convert_apple_activity_type(self, x):
        """
        Maps apple activity types to more useful enum representation
        """

        if x == 'HKWorkoutActivityTypeCycling':
            return ActivityType.BIKE
        elif x == 'HKWorkoutActivityTypeElliptical':
            return ActivityType.ELLIPTICAL
        elif x == 'HKWorkoutActivityTypePilates':
            return ActivityType.PILATES
        elif x == 'HKWorkoutActivityTypeRowing':
            return ActivityType.ROWING
        elif x == 'HKWorkoutActivityTypeRunning':
            return ActivityType.RUN
        elif x == 'HKWorkoutActivityTypeSwimming':
            return ActivityType.RUN
        elif x == 'HKWorkoutActivityTypeWalking':
            return ActivityType.WALKING
        elif x == 'HKWorkoutActivityTypeYoga':
            return ActivityType.YOGA
        return ActivityType.OTHER

    def convert_strava_activity_type(self, x):
        """
        Maps strava activity types to more useful enum representation
        """

        if x == "Run":
            return ActivityType.RUN
        elif x == "Ride":
            return ActivityType.BIKE
        else:
            return ActivityType.OTHER

    def add_strava_data_to_activities(self):
        strava_data = json.dumps(self.requestor.get_json_activities(ActivitySource.STRAVA))
        
        # load strava data straight up from json, not doing any json normalization
        strava_df = pd.read_json(strava_data)
        strava_df = strava_df[['distance', 
            'elapsed_time', 
            'start_date_local', 
            'location_city', 
            'average_speed', 
            'max_speed', 
            'type']]

        # set up 5 key metrics
        # note we're using the enum value
        strava_df['activity_type'] = strava_df['type'].apply(lambda x: self.convert_strava_activity_type(x).value)
        strava_df['source'] = ActivitySource.STRAVA.value
        strava_df['start_timestamp'] = strava_df['start_date_local'].apply(lambda x: parse(x, tzinfos={"America/Vancouver"}))
        # strava distances are in meters
        strava_df['distance_in_km'] = strava_df['distance'].apply(lambda x: x / 1000)
        strava_df['duration_in_min'] = strava_df['elapsed_time'].apply(lambda x: x / 60)

        #  filter out extraneous columns
        strava_df = strava_df.filter(self.data_frame_columns)

        #  add to activities
        self.all_activities = self.all_activities.append(strava_df, sort=True)

    def add_nike_data_to_activities(self):  

        # load Nike data, normalize the nested JSON
        nike_df = json_normalize(self.requestor.get_json_activities(ActivitySource.NIKE))

        # merge in normalized summaries, joining by id
        summaries = json_normalize(self.requestor.get_json_activities(ActivitySource.NIKE), record_path="summaries", record_prefix="summaries.", meta="id")
        summaries = summaries[summaries['summaries.metric'] == "distance"]
        nike_df = pd.merge(nike_df, summaries, how='inner', on='id')

        # set 5 key metrics
        # note we're using the enum value
        nike_df['source'] = ActivitySource.NIKE.value
        nike_df['activity_type'] = ActivityType.RUN.value
        nike_df['start_timestamp'] = nike_df['start_epoch_ms'].apply(lambda x: datetime.fromtimestamp(x / 1000, pytz.timezone('America/Vancouver')))
        nike_df['distance_in_km'] = nike_df['summaries.value']
        nike_df['duration_in_min'] = nike_df['active_duration_ms'].apply(lambda x: x / 1000 / 60)

        #  filter out extraneous columns
        nike_df = nike_df.filter(self.data_frame_columns)

        #  add to activities
        self.all_activities = self.all_activities.append(nike_df, sort=True, ignore_index=True)

    def add_apple_data_to_activities(self):

        # apple data is loaded from csv rather than from json
        apple_data = self.load_apple_workouts()

        #  filter out nike and strava data that has synced to apple, we are getting that from json source
        apple_data = apple_data[(apple_data.sourceName != "Nike Run Club") & (apple_data.sourceName != "Strava")]

        # set up 5 key metrics
        # note we're using enum values
        apple_data['source'] = ActivitySource.APPLE.value
        apple_data['activity_type'] = apple_data['workoutActivityType'].apply(lambda x: self.convert_apple_activity_type(x).value)
        apple_data['distance_in_km'] = apple_data['totalDistance']
        apple_data['duration_in_min'] = apple_data['duration']
        apple_data['start_timestamp'] = apple_data['startDate'].apply(lambda x: parse(x, tzinfos={"America/Vancouver"}))

        #  filter out extraneous columns
        apple_data = apple_data.filter(self.data_frame_columns)
        self.all_activities = self.all_activities.append(apple_data, sort=True, ignore_index=True)

    def load_apple_workouts(self):
        print("Getting csv data for apple data")
        workouts_filepath = 'data/apple_health_export_csv/Workout.csv'
        return pd.read_csv(workouts_filepath, sep=',')

    def isDuplicate(self, a, b):
        """
        check for duplicates based on close runs are in distance and time
        removing timezones for the timestamp comparison
        """

        isDuplicate = (
            abs(a['distance_in_km'] - b['distance_in_km']) 
                < RunDataCleaner.KM_SIMILARITY_THRESHOLD and 
            abs((a['start_timestamp'].tz_convert(None) - b['start_timestamp'].tz_convert(None)).total_seconds()) 
                < RunDataCleaner.SECONDS_SIMILARITY_THRESHOLD)
        if isDuplicate:
            print("A: {} : {} : {}\nB: {} : {} : {}\n".format(
                a['source'],
                a['start_timestamp'],
                a['distance_in_km'],
                b['source'],
                b['start_timestamp'],
                b['distance_in_km']))
        return isDuplicate

    def remove_duplicates(self):
        print("Removing duplicates...")
        all_activities = self.all_activities
        all_activities['duplicate'] = False
        before_len = len(all_activities)

        # generating all these combinations is slow, hence this will be saved to pickle after being run
        for a, b in itertools.combinations(all_activities.index, 2):
            if self.isDuplicate(all_activities.loc[a,:], all_activities.loc[b,:]):
                all_activities.at[a, 'duplicate'] = True
        all_activities = all_activities[all_activities['duplicate']!= True]
        print(f"Removed {before_len - len(all_activities)} duplicates")
