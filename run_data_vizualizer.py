from activity_enums import ActivitySource, ActivityType
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

class RunDataVisualizer:
    """
    Does some interesting matlab plots with the data
    """

    def __init__(self, activities):
        """
            activities is a data frame with columns:
            ['start_timestamp', 'duration_in_min', 'distance_in_km','activity_type','source']
        """

        self.activities = activities

        # TODO: move this to data cleaning stage
        self.activities['y'] = self.activities['start_timestamp'].apply(lambda x: '{}'.format(x.year))
        self.activities['y_m'] = self.activities['start_timestamp'].apply(lambda x: '{}-{}'.format(x.year, x.month))
        self.activities['y_m_d'] = self.activities['start_timestamp'].apply(lambda x: '{}-{}-{}'.format(x.year, x.month, x.day))
        
        self.activities['weekday'] = pd.Categorical(self.activities['start_timestamp'].apply(lambda x: f'{x.day_name()}'),
            categories= ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday'], ordered=True)

        self.activities['min_per_km_pace'] = self.activities['duration_in_min'] / self.activities['distance_in_km']

        self.runs = self.activities[self.activities['activity_type'] == ActivityType.RUN.value]

        # filter out runs < 1 km
        self.runs = self.runs[self.runs['distance_in_km'] > 3]

        self.bikes = self.activities[self.activities['activity_type'] == ActivityType.BIKE.value]

        self.runs_and_bikes = self.activities[(self.activities['activity_type'] == ActivityType.RUN.value) | (
            self.activities['activity_type'] == ActivityType.BIKE.value)]

    def visualize_runs_by_year_month(self):
        grouped = self.runs.groupby(['y_m'])['distance_in_km'].sum()
        grouped.plot(kind="bar")
        plt.show(block=True)

    def visualize_runs_by_year_and_source(self):
        grouped = self.runs.groupby(['y', 'source'])[
            'distance_in_km'].sum().unstack('source').fillna(0)
        grouped.plot(kind="bar", stacked=True)
        plt.show(block=True)

    def visualize_bikes_by_year(self):
        grouped = self.bikes.groupby(['y'])['distance_in_km'].sum()
        grouped.plot(kind="bar")
        plt.show()

    def visualize_runs_by_month(self):
        grouped = self.runs.groupby(['m', 'source'], sort=False)[
            'distance_in_km'].sum()
        grouped.plot(kind="bar", stacked=True)
        plt.show(block=True)

    def visualize_runs_and_bikes_by_year(self):
        grouped = self.runs_and_bikes.groupby(['y', 'activity_type'])[
            'distance_in_km'].sum().unstack('activity_type').fillna(0)
        grouped.plot(kind="line", stacked=True)
        plt.show(block=True)

    def visualize_min_per_km_by_year(self):
        grouped = self.runs.groupby(['y'])['min_per_km_pace'].mean()
        grouped.plot(kind="line")
        plt.show(block=True)

    def visualize_min_per_km_by_year_month(self):
        grouped = self.runs.groupby(['y_m'])['min_per_km_pace'].mean()
                # plt.xticks(index, dow_labels, rotation=45)
        grouped.plot(kind="line")
        plt.show(block=True)

    def visualize_runs_by_day_of_week(self):

        data = self.runs.groupby(['weekday'])['distance_in_km'].mean()

        # fig, ax = plt.subplots(figsize=[10, 6])
        ax = data.plot(kind='bar', x='weekday')

        n_groups = len(self.activities)
        index = np.arange(n_groups)
        opacity = 0.75

        # ax.yaxis.grid(True)

        plt.suptitle('Average km by Day of the Week', fontsize=16)
        dow_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # plt.xticks(index, dow_labels, rotation=45)
        plt.xlabel('Day of Week', fontsize=12, color='red')
        plt.show(block=True)