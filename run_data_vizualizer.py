from activity_enums import ActivitySource, ActivityType
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
        self.activities['y'] = self.activities['start_timestamp'].apply(
            lambda x: '{}'.format(x.year))
        self.activities['y_m'] = self.activities['start_timestamp'].apply(
            lambda x: '{}-{}'.format(x.year, x.month))
        self.activities['y_m_d'] = self.activities['start_timestamp'].apply(
            lambda x: '{}-{}-{}'.format(x.year, x.month, x.day))

        # self.activities['min_per_km'] = self.activities.apply(
        #     lambda x: x['distance_in_km'] / x['distance_in_km'], axis=1)

    def visualize_runs_by_year_month(self):
        runs = self.activities[self.activities['activity_type']
                               == ActivityType.RUN.value]
        grouped = runs.groupby(['y_m'])['distance_in_km'].sum()
        grouped.plot(kind="bar")
        plt.show(block=True)

    def visualize_runs_by_year_and_source(self):
        runs = self.activities[self.activities['activity_type']
                               == ActivityType.RUN.value]
        grouped = runs.groupby(['y', 'source'])[
            'distance_in_km'].sum().unstack('source').fillna(0)
        grouped.plot(kind="bar", stacked=True)
        plt.show(block=True)

    def visualize_bikes_by_year(self):
        runs = self.activities[self.activities['activity_type']
                               == ActivityType.BIKE.value]
        grouped = runs.groupby(['y'])['distance_in_km'].sum()
        grouped.plot(kind="bar")
        plt.show()

    def visualize_runs_by_month(self):
        runs = self.activities[self.activities['activity_type']
                               == ActivityType.RUN.value]
        grouped = runs.groupby(['m', 'source'], sort=False)[
            'distance_in_km'].sum()
        grouped.plot(kind="bar", stacked=True)
        plt.show(block=True)

    def visualize_runs_and_bikes_by_year(self):
        runs_and_bikes = self.activities[(self.activities['activity_type'] == ActivityType.RUN.value) | (
            self.activities['activity_type'] == ActivityType.BIKE.value)]
        grouped = runs_and_bikes.groupby(['y', 'activity_type'])[
            'distance_in_km'].sum().unstack('activity_type').fillna(0)
        grouped.plot(kind="line", stacked=True)
        plt.show(block=True)

    def visualize_min_per_km_by_year(self):
        runs = self.activities[(
            self.activities['activity_type'] == ActivityType.RUN.value)]
        grouped = runs.groupby(['y'])['min_per_km']
        grouped.plot(kind="line")
        plt.show(block=True)
