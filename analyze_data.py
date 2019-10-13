from run_data_api import RunDataRequestor, ActivityType
import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# environment settings: 
# pd.set_option('display.max_column',None)
# pd.set_option('display.max_rows',None)
# pd.set_option('display.max_seq_items',None)
# pd.set_option('display.max_colwidth', 500)
# pd.set_option('expand_frame_repr', True)

def get_nike_total_distance():
    requestor = RunDataRequestor()
    nike_activities = requestor.get_json_activities(ActivityType.NIKE)
    total_running_distance = 0
    total_runs = 0
    for page in nike_activities:
        try:
            for activity in page['activities']:
                total_runs += 1
                summaries = activity['summaries']
                for summary in summaries:
                    if summary['metric'] == "distance":
                        total_running_distance += summary['value']
                        break
        except TypeError:
            continue

    print(f'total nike runs {total_runs}')
    print(f'total nike distance {total_running_distance} km')

def compare(row):
    prev_distance = row.distance_in_km.shift(1)
    this_distance = row["distance_in_km"]
    this_date = row['y_m_d']
    prev_date = row['y_m_d'].shift()
    if prev_date == this_date and abs(this_distance - prev_distance) <= 1:
        row["duplicate"] == True
    return row

def do_data_science():
    requestor = RunDataRequestor()
    activities = requestor.get_json_activities(ActivityType.STRAVA)

    df = pd.read_json(activities)

    df = df[df.type == "Run"]

    df['start_date'] = pd.to_datetime(df['start_date'], infer_datetime_format=True)
    df['date_no_timestamp'] = df['start_date'].apply(lambda x: x.date())
    df['y_m_d'] = df['start_date'].apply(lambda x: '{}-{}-{}'.format(x.year, x.month, x.day))

    df['distance_in_km'] = df['distance'].apply(lambda x: x / 1000)

    print('Total strava running distance:')
    print(df["distance_in_km"].sum())

    tag_duplicates_in_numpy(df)

    # data_to_plot = df.groupby("date_no_timestamp")["distance_in_km"].sum()
    # grouped = df.groupby(["y_m_d"])["distance_in_km"].agg('sum').plot(kind="bar")

    df = df.sort_values(by=['y_m_d', 'distance_in_km'])

    # df.groupby(["start_date"])["distance_in_km"].agg('sum').plot(kind="bar")
    # fig, ax = plt.subplots(figsize=(10, 6))
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y'))
    # ax.bar(data_to_plot.index, data_to_plot[0], width=25, align='center')
    # plt.show()

def tag_duplicates_in_numpy(df):
    numps = df.head(1).to_numpy(copy=False)
    print(numps)
    # for i, val in enumerate(numps):
    #     print(numps[i])
        # if i != 0:
            # prev_distance = numps[i-1]["distance_in_km"]
            # this_distance = numps[i]["distance_in_km"]
            # this_date = numps[i-1]['y_m_d']
            # prev_date = numps[i]['y_m_d']
            # if prev_date == this_date and abs(this_distance - prev_distance) <= 1:
            #     print("Found a duplicate!")
            #     numps[i]["duplicate"] = True
            #     numps[i-1]["duplicate"] = True

# compare stuff
    # print(df.head(4))
    # other_df = df.apply(compare, axis=1)

    # for i, row in df.iterrows():
    #     if i != 0:
    #         # prev_distance = df.iloc[i-1]["distance_in_km"]
    #         this_distance = df.iloc[:, i]["distance_in_km"]
    #         # prev_date = df.iloc[i-1]['y_m_d']
    #         this_date = df.iloc[:,i]['y_m_d']
            # if prev_date == this_date and abs(this_distance - prev_distance) <= 1:
            #     df.iloc[i]["duplicate"] = True
            #     df.iloc[i-1]["duplicate"] = True

get_nike_total_distance()