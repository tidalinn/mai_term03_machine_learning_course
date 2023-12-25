import numpy as np
import pandas as pd

from datetime import datetime
import requests
import pickle
import joblib

from tensorflow.keras.models import load_model
from tensorflow.keras.layers import TextVectorization

from geopy.distance import geodesic
from geopy.geocoders import Nominatim


# import models
multilabel = pickle.load(open('model/multilabel.pkl', 'rb'))


# preprocess predictions
def transform_label(label, vocab):
    return vocab.inverse_transform(np.array([label]))

def transform_probs_to_labels(probs, threshold=0.5):
    return (probs > threshold).astype(int)

def preprocess_prediction(pred, vocab):
    if sum(pred) == 0:
        pred = 'No results'
    else:
        pred = transform_label(pred, vocab)
        pred = ', '.join(*pred)
    
    return pred


# get predictions
def get_predictions(value, model_type):  
    if model_type == 'dl':
        # load
        model = load_model('model/model.h5')
        vectorizer_file = pickle.load(open('model/vectorizer.pkl', 'rb'))

        # convert vectorizer
        vectorizer = TextVectorization.from_config(vectorizer_file['config'])
        vectorizer.adapt([value])
        vectorizer.set_weights(vectorizer_file['weights'])

        # make predictions
        prediction = model.predict(vectorizer([value]))
        # convert predictions
        prediction = transform_probs_to_labels(prediction)[0]
    
    else:
        # load 
        model = joblib.load('model/model.h5')

        prediction = model.predict([value])[0]
    
    # preprocess output
    prediction = preprocess_prediction(prediction, multilabel)

    return prediction


# other funcs
def check_daytime(hour):
    if 4 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 16:
        return 'day'
    elif 16 <= hour < 24:
        return 'evening'
    else:
        return 'night'


def check_hour():
    hour = int(
        datetime.now().strftime("%H:%M:%S").split(':')[0]
    )

    daytime = check_daytime(hour)

    return hour, daytime


def convert_place_to_lat_lon(place):
    url = f'https://nominatim.openstreetmap.org/search.php?q={place}&format=jsonv2'
    
    try:
        result = requests.get(url=url)
        result_json = result.json()[0]
        
        return result_json['lat'], result_json['lon']
        
    except:
        return None
    

def calculate_distance(user, row) -> float:
    vendor = (row['vendor_lat'], row['vendor_lon'])
    
    return round(geodesic(user, vendor).km, 2)


# create rating
def create_rating(df, user_lat_lon, hour, pred, top=5):

    daytime = check_daytime(int(hour))
    # user_lat_lon = (1.35, 103.5)
    user_lat_lon = convert_place_to_lat_lon(user_lat_lon)
    
    # calculate distance between user and vendor
    rating_result = df[df['time_of_day'] == daytime].copy()
    
    rating_result['distance'] = rating_result.apply(
        lambda x: calculate_distance(user_lat_lon, x),
        axis=1
    )
    
    rating_result = rating_result.sort_values(by='distance')
    
    
    # create rating    
    rating = pd.DataFrame()

    for p in pred.split(', '):
        rating = pd.concat([rating, rating_result[rating_result['primary_cuisine'] == p][:top]])

    rating_top = rating.sort_values(by='count', ascending=False)[:top]
    
    rating_top['vendor_lat_lon'] = rating.apply(lambda x: (x['vendor_lat'], x['vendor_lon']), axis=1)
    
    cuisines = list(rating_top['primary_cuisine'].unique())
    locations = list(rating_top['vendor_lat_lon'].unique())

    cuisines = ', '.join(cuisines)
    locations = ', '.join([str(l) for l in locations])

    if cuisines == '' or locations == '':
        cuisines = 'No results'
        locations = 'No results'
    
    return cuisines, locations