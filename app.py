import streamlit as st

from datetime import datetime, date, time
import requests
import pytz

import folium
from streamlit_folium import folium_static


BASE_URL = 'https://taxifare-nourhenekr-lgc6lf6tua-ew.a.run.app'

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def predict(pickup_datetime, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, passenger_count):
    url = BASE_URL + '/predict'

    data_to_predict = {
        'pickup_datetime': pickup_datetime,
        'pickup_longitude': pickup_longitude,
        'pickup_latitude': pickup_latitude,
        'dropoff_longitude': dropoff_longitude,
        'dropoff_latitude': dropoff_latitude,
        'passenger_count': passenger_count
    }

    try:
        response = requests.get(url, params=data_to_predict)

        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                st.error(f'Error parsing JSON response: {e}')
                return None
        else:
            st.error(f'Request failed with status code {response.status_code}')
            return None

    except requests.exceptions.RequestException as e:
        st.error(f'Request failed: {e}')
        return None


st.title('Welcome to Taxi Fare Predictor')
st.subheader('Created By NourheneKr')

st.header("Taxi Fare Predictor")

subcol1, subcol2 = st.columns(2)
with subcol1:
    date_input = st.date_input('Date du voyage')
with subcol2:
    time_input = st.time_input('Heure du voyage')
pickup_longitude = st.text_input('Départ longitude', '-73.950655')
pickup_latitude = st.text_input('Départ latitude', '40.783282')
dropoff_longitude = st.text_input('Arrivée longitude', '-73.984365')
dropoff_latitude = st.text_input('Arrivée latitude', '40.769802')

if pickup_longitude and pickup_latitude and dropoff_longitude and dropoff_latitude:
    pickup_coords = None
    dropoff_coords = None
    pickup_coords = (float(pickup_latitude), float(pickup_longitude))
    dropoff_coords = (float(dropoff_latitude), float(dropoff_longitude))
    if pickup_coords and dropoff_coords:
        m = folium.Map(location=pickup_coords, zoom_start=12)
        folium.Marker(pickup_coords, tooltip='Pickup Location', icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(dropoff_coords, tooltip='Dropoff Location', icon=folium.Icon(color='red')).add_to(m)
        folium.PolyLine([pickup_coords, dropoff_coords], color='blue', weight=2.5, opacity=1).add_to(m)
        folium_static(m)


passenger_count = st.number_input('Nombre de passagers', min_value=1, max_value=5)

fare = None
prediction_made = False

if st.button('Combien ça me coûte ?'):

    if pickup_longitude and pickup_latitude and dropoff_longitude and dropoff_latitude:
        if not is_float(pickup_longitude) or not is_float(pickup_latitude) or not is_float(dropoff_longitude)or not is_float(dropoff_latitude):
            st.warning('Invalid input. Please enter a valid float number.')

        else:
            pickup_datetime = datetime.combine(date_input, time_input)
            pickup_datetime_utc = pickup_datetime.astimezone(pytz.utc)
            pickup_datetime_utc_str = pickup_datetime_utc.strftime('%Y-%m-%d %H:%M:%S')

            prediction_result = predict(pickup_datetime_utc_str, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, passenger_count)
            if prediction_result and 'fare' in prediction_result:
                fare = round(prediction_result['fare'], 2)
                prediction_made = True
                st.markdown(f'<h1 style="font-size:48px;">$ {fare}</h1>', unsafe_allow_html=True)

    else:
        st.warning('Please fill in all input fields')
