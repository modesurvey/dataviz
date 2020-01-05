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

    # Create an array with the colors you want to use
    colors = ["#2b56ff", "#0c780c", "#db0a07", "#0a0606"]
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

if __name__ == '__main__':
    run()