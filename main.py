from run_data_api import RunDataApiRequestor
import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# environment settings: 
pd.set_option('display.max_column',None)
pd.set_option('display.max_rows',None)
pd.set_option('display.max_seq_items',None)
pd.set_option('display.max_colwidth', 500)
pd.set_option('expand_frame_repr', True)

def main():
    requestor = RunDataApiRequestor()
    activities = requestor.get_and_save_activites()

    df = pd.read_json(activities)

    df = df[df.type == "Run"]

    df['start_date'] = pd.to_datetime(df['start_date'], infer_datetime_format=True)
    df['date_no_timestamp'] = df['start_date'].apply(lambda x: x.date())
    df['y_m_d'] = df['start_date'].apply(lambda x: '{}-{}-{}'.format(x.year, x.month, x.day))

    df['distance_in_km'] = df['distance'].apply(lambda x: x / 1000)

    print('Total strava running distance:')
    print(df["distance_in_km"].sum())

    # data_to_plot = df.groupby("date_no_timestamp")["distance_in_km"].sum()

    df.groupby(["y_m_d"])["distance_in_km"].agg('sum').plot(kind="bar")
    # df.groupby(["start_date"])["distance_in_km"].agg('sum').plot(kind="bar")

    # fig, ax = plt.subplots(figsize=(10, 6))
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y'))
    # ax.bar(data_to_plot.index, data_to_plot[0], width=25, align='center')
    plt.show()

if __name__ == "__main__":
    main()
