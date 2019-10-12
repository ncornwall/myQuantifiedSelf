from run_data_api import RunDataRequestor, ActivityType

requestor = RunDataRequestor()

def get_strava_data_as_numpy():
    strava_data = requestor.get(ActivityType.STRAVA)
    # for activity in strava_data:

def main():
    print('yo')

if __name__ == "__main__":
    main()
