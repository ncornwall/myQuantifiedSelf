from json_run_data_api import JsonRunDataRequestor
from run_data_processor import RunDataProcessor
from activity_enums import ActivitySource, ActivityType

import pandas as pd

def set_pandas_display_options() -> None:
    display = pd.options.display
    display.max_columns = 1000
    display.max_rows = 1000
    display.max_colwidth = 199
    display.width = None
    # display.precision = 2  # set as needed

def main():
    set_pandas_display_options()

    # activities = merge_strava_nike_apple_data()
    # remove_duplicates(activities)
    # calc_total_distance_run(activities)

    requestor = JsonRunDataRequestor()
    processor = RunDataProcessor(requestor)

    processor.add_strava_data_to_activities()
    processor.add_nike_data_to_activities()

    all_activities = processor.all_activities
    sum = all_activities[all_activities['activity_type'] == ActivityType.RUN].groupby(['activity_type'])['distance_in_km'].sum()
    print(f'Total running distance: {sum}')

if __name__ == "__main__":
    main()
