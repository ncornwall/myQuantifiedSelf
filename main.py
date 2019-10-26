from json_run_data_fetcher import JsonRunDataFetcher
from run_data_cleaner import RunDataCleaner
from activity_enums import ActivitySource, ActivityType

import pandas as pd

class RunDataAnalyzer:
    def __init__(self, activities):
        self.activities = activities
    
    def get_summary_stats_by_type_and_source(self):
        all_activities = self.activities
        aggs = all_activities.groupby(['source', 'activity_type'])['distance_in_km'].sum()
        sum = all_activities['distance_in_km'].sum()
        print(f'All activities:\n {aggs} \n {sum}')

    def get_running_stats(self):
        all_activities = self.activities
        sum = all_activities[all_activities['activity_type'] == ActivityType.RUN.value]['distance_in_km'].sum()
        print(f'Total running distance: {sum}')

def set_pandas_display_options() -> None:
    display = pd.options.display
    display.max_columns = 1000
    display.max_rows = 1000
    display.max_colwidth = 199
    display.width = None
    # display.precision = 2  # set as needed

def main():
    set_pandas_display_options()
    df = None
    try:
        df = pd.read_pickle('data/all_activities.pkl')
        print("Fetching from pickle")
    except FileNotFoundError:
        fetcher = JsonRunDataFetcher()

        cleaner = RunDataCleaner(fetcher)
        cleaner.add_strava_data_to_activities()
        cleaner.add_nike_data_to_activities()
        cleaner.add_apple_data_to_activities()
        cleaner.remove_duplicates()

        df = cleaner.all_activities
        df.to_pickle('data/all_activities.pkl')

    analyzer = RunDataAnalyzer(df)
    analyzer.get_summary_stats_by_type_and_source()
    analyzer.get_running_stats()

if __name__ == "__main__":
    main()
