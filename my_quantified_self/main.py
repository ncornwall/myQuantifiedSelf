import logging
import os

import pandas as pd

from run_data_processor import RunDataProcessor
from run_data_analyzer import RunDataAnalyzer
from run_data_vizualizer import RunDataVisualizer
from activity_enums import ActivitySource

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logging.info("Let's get started!")

def set_pandas_display_options() -> None:
    display = pd.options.display
    display.max_columns = 1000
    display.max_rows = 1000
    display.max_colwidth = 199
    display.width = None
    # display.precision = 2  # set as needed

def main():
    setup_logging()
    set_pandas_display_options()
    df = None

    # Try to grab the data frame from file where it has been stored
    pickle_path = "data/all_activities.pkl"
    if os.path.exists(pickle_path):
        df = pd.read_pickle('data/all_activities.pkl')
        logging.info("Successfully fetched stored data from pickle file")
    else:
        logging.info("Data frame is not available from pickle file, run the data pipeline")
        # merge the data from APIs + data from apple health app
        # and remove duplicate run data
        processor = RunDataProcessor()
        processor.add_strava_data_to_activities()
        processor.add_nike_data_to_activities()
        # cleaner.add_apple_data_to_activities()
        # cleaner.remove_duplicates()

    #     df = cleaner.all_activities

    #     # store the resulting frame as the previous steps can be slow
    #     df.to_pickle('data/all_activities.pkl')

    # # generate some insights
    # analyzer = RunDataAnalyzer(df)
    # analyzer.get_summary_stats_by_type_and_source()
    # analyzer.get_running_stats()

    # # make some fun charts
    # visualizer = RunDataVisualizer(df)
    # # visualizer.visualize_bikes_by_year()
    # visualizer.visualize_runs_by_year_and_source()
    # visualizer.visualize_runs_by_year_and_source()
    # visualizer.visualize_min_per_km_by_year()
    # visualizer.visualize_runs_and_bikes_by_year()
    # visualizer.visualize_runs_by_month()
    # visualizer.visualize_runs_by_day_of_week()
    # visualizer.visualize_min_per_km_by_year()
    # visualizer.visualize_runs_by_year_month()
    # visualizer.visualize_min_per_km_by_year_month()

if __name__ == "__main__":
    main()
