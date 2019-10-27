from json_run_data_fetcher import JsonRunDataFetcher
from run_data_cleaner import RunDataCleaner
from run_data_analyzer import RunDataAnalyzer
from run_data_vizualizer import RunDataVisualizer

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
    df = None
    try:
        # Try to grab the data frame from file where it has been stored
        df = pd.read_pickle('data/all_activities.pkl')
        print("Fetching from pickle")

    except FileNotFoundError:

        # Data frame is not available, run the data pipeline

        # fetcher to get data from strava and nike APIs
        fetcher = JsonRunDataFetcher()

        # merge the data from APIs + data from apple health app
        # and remove duplicate run data
        cleaner = RunDataCleaner(fetcher)
        cleaner.add_strava_data_to_activities()
        cleaner.add_nike_data_to_activities()
        cleaner.add_apple_data_to_activities()
        cleaner.remove_duplicates()

        df = cleaner.all_activities

        # store the resulting frame as the previous steps can be slow
        df.to_pickle('data/all_activities.pkl')

    # generate some insights
    analyzer = RunDataAnalyzer(df)
    analyzer.get_summary_stats_by_type_and_source()
    analyzer.get_running_stats()

    # make some fun charts
    visualizer = RunDataVisualizer(df)
    # visualizer.visualize_bikes_by_year()
    # visualizer.visualize_runs_by_year_and_source()
    visualizer.visualize_runs_by_year_and_source()
    # visualizer.visualize_min_per_km_by_year()
    # visualizer.visualize_runs_and_bikes_by_year()
    # visualizer.visualize_runs_by_month()

if __name__ == "__main__":
    main()
