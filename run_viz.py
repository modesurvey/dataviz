import pyrebase
import config
import json
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
import time
import numpy as np
from collections import defaultdict
import nordypy


def run():
    config = {
    "apiKey": "apiKey",
    "authDomain": "projectId.firebaseapp.com",
    "databaseURL": "https://surveybox-fe69c.firebaseio.com",
    "storageBucket": "projectId.appspot.com"}

    firebase = pyrebase.initialize_app(config)

    db = firebase.database()
    resp = db.get()
    data = []
    for f, v in dict(resp.val())['accounts'].items():
        data.append(v)

    # set up all the locations that had a modesurvey box
    accounts = {}
    for loc in data:
        name = loc['name']
        for k, v in loc['locations'].items():
            accounts[k] = name

    # get all the events and associate them with an account
    events = defaultdict(list)
    for k, v  in dict(resp.val()['streams']).items():
        location_id = v['location_id']
        for event_key, event in v['events'].items():
            events[accounts[location_id]].append(event)

    def convert(d):
        try:
            return datetime.datetime.fromtimestamp(int(d))
        except:
            'error'
    
    list_ordering = ["walk", "wheels", 'transit', 'car']  

    # aggregate to all responses per account 
    all_data = pd.DataFrame()
    for k, v in events.items():
        data = pd.DataFrame(v)

        data['timestamp'] = data['timestamp'].apply(convert)
        data['count'] = 1
        print(f'Before deduping: {data.shape}')
        data = data.drop_duplicates(['timestamp', 'type'])
        print(f'Total responses after deduping: {len(data)}')
        grouped_data = data.groupby(['type'])['count'].sum().reset_index()


        grouped_data["type"] = pd.Categorical(grouped_data["type"], categories=list_ordering, ordered=True)
        grouped_data["account"] = k 
        all_data = pd.concat([all_data, grouped_data])

    # plot everything 
    sns.set_style("whitegrid")
    # Create an array with the colors you want to use
    colors = ['#66b3ff','#99ff99','#ff9999','#808080']
    # Set your custom color palette
    customPalette = sns.set_palette(sns.color_palette(colors))

    g = sns.catplot(x="type", y="count", col="account",
                    data=grouped_data, saturation=.5,
                    kind="bar", aspect=1, palette=customPalette)
    (g.set_xticklabels(["walk", "wheels", "transit", "car"])
        .set_titles("{col_name}")
        .despine(left=True))
    sns.set(font_scale=1)
    plt.savefig('grouped_data.png')

    # Pie chart

    for u in all_data['account'].unique():
        mini = all_data[all_data['account'] == u]
        labels = mini['type']
        sizes = mini['count']
        
        #colors : car transit wheels walk
        colors = ['#808080','#ff9999','#66b3ff', '#99ff99']

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, colors = colors, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=.55)
        #draw circle
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title(u)
        ax1.axis('equal')  
        fig.text(.5, .01, 'Updated at: ' + str( datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")  ), 
                  ha='center', fontsize=10)

        plt.tight_layout()
        path = 'output/'
        path = path + '_'.join(u.lower().split(' ')) + '.png'
        print(u)
        plt.savefig(path)
        plt.show()
        plt.close()
        nordypy.s3_upload(bucket='modesurvey-dataviz', s3_filepath=path, 
                                                      local_filepath=path,
                                                      permission='public-read')

    

if __name__ == '__main__':
    run()