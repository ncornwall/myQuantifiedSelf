from activity_enums import ActivitySource, ActivityType

class RunDataAnalyzer:
    """
    The analysis stage of the data pipeline
    Does some interesting calculations on the data
    """

    def __init__(self, activities):
        """
            activities is a data frame with columns:
            ['start_timestamp', 'duration_in_min', 'distance_in_km','activity_type','source']
        """
        self.activities = activities

    def get_summary_stats_by_type_and_source(self):
        all_activities = self.activities
        aggs = all_activities.groupby(['source', 'activity_type'])[
            'distance_in_km'].sum()
        sum = all_activities['distance_in_km'].sum()
        print(f'All activities:\n {aggs} \n {sum}')

    def get_running_stats(self):
        all_activities = self.activities
        sum = all_activities[all_activities['activity_type']
                             == ActivityType.RUN.value]['distance_in_km'].sum()
        print(f'Total running distance: {sum}')
    