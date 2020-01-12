import pyrebase
import config
import json
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
import time
import numpy as np


def run():
    config = {
    "apiKey": "apiKey",
    "authDomain": "projectId.firebaseapp.com",
    "databaseURL": "https://surveybox-fe69c.firebaseio.com",
    "storageBucket": "projectId.appspot.com"}

    firebase = pyrebase.initialize_app(config)

    unit_translation = {'38ed9c286f24': "Cafe Allegro", 
                        '98798yuah8': "Bulldog Espresso", 
                        "a03e9e286f24": "Magus Books"}

    db = firebase.database()
    resp = db.get()
    data = []
    for f, v in dict(resp.val())['events'].items():
        data.append(v)
    data = pd.DataFrame(data)

    def convert(d):
        try:
            return datetime.datetime.fromtimestamp(int(d))
        except:
            'error'

    data['timestamp'] = data['timestamp'].apply(convert)
    data['count'] = 1
    grouped_data = data.groupby(['unit', 'type'])['count'].sum().reset_index()

    list_ordering = ["walk", "wheels", 'transit', 'car']  

    grouped_data["type"] = pd.Categorical(grouped_data["type"], categories=list_ordering, ordered=True)
    grouped_data["unit"] = grouped_data['unit'].apply(lambda k: unit_translation[k])

    sns.set_style("whitegrid")
    # Create an array with the colors you want to use
    colors = ['#66b3ff','#99ff99','#ff9999','#808080']
    # Set your custom color palette
    customPalette = sns.set_palette(sns.color_palette(colors))

    g = sns.catplot(x="type", y="count", col="unit",
                    data=grouped_data, saturation=.5,
                    kind="bar", aspect=1, palette=customPalette)
    (g.set_xticklabels(["walk", "wheels", "transit", "car"])
        .set_titles("{col_name}")
        .despine(left=True))
    sns.set(font_scale=1)
    plt.savefig('grouped_data.png')

    # Pie chart

    for u in grouped_data['unit'].unique():
        mini = grouped_data[grouped_data['unit'] == u]
        labels = mini['type']
        sizes = mini['count']
        
        #colors
        colors = ['#808080','#ff9999','#99ff99','#66b3ff']

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, colors = colors, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=.55)
        #draw circle
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title(u)
        ax1.axis('equal')  
        plt.tight_layout()
        plt.savefig(f'{u}_circle.png')
        plt.show()

if __name__ == '__main__':
    run()