import subprocess
import os
import sys
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'geopy', 'textblob'])
from html import entities
import streamlit as st
import pandas as pd
import spacy_streamlit
import spacy
from spacy import displacy
import requests
from textblob import TextBlob
from requests.structures import CaseInsensitiveDict
import random
from pydoc import locate
import streamlit.components.v1 as components
import base64
import traceback
import random
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

#API_URL = os.environ.get('API_URL', '')
API_URL = 'http://ef14-35-192-60-94.ngrok.io'

if 'isAuthenticated' not in st.session_state:
    st.session_state.isAuthenticated = False

if 'authToken' not in st.session_state:
    st.session_state.authToken = ''


user_container = st.empty()
pass_container = st.empty()
auth_container = st.empty()

user_container.empty()
pass_container.empty()
auth_container.empty()


if st.session_state.isAuthenticated is False:
    
    username = user_container.text_input('Email Address', '')
    password = pass_container.text_input('Password', type="password")


def page_second():
    
    #st.session_state.authToken = ''

    #int_val = st.number_input('Select a row for the article', min_value=0, max_value=49, step=1, key="int")

    # if st.button("Submit"):
    #     int_val = random.randrange(1, 500, 3)
    #     st.session_state["int"] = int_val

    def get_coordinates(location):
    # initialize Nominatim API 
        geolocator = Nominatim(user_agent="geoapiExercises")
        location_area = geolocator.geocode(location)
        return location_area.latitude, location_area.longitude

    def get_event_id(lat,long):
        max = 10000000
        event_id = None

        for i in range(0, len(df_catalog)):
            targ = (df_catalog.at[i, 'llcrnrlat'], df_catalog.at[i, 'llcrnrlon'])
            val = geodesic((lat,long), targ).miles
            #print(val)
            if (val < max and val < 100):
                max = val
                event_id = df_catalog.at[i, 'event_id']

        if (max == 10000000):
            print("Not Found")
        else:
            print("Shortest distance: ", max, "\nEvent ID: ", event_id)

        return max, event_id

  

    if st.session_state.isAuthenticated is True:

        user_container.empty()
        pass_container.empty()
        auth_container.empty()

        txt = st.text_input('Location')

        if st.button('Submit'):
            int_val = random.randrange(1, 500, 3)
            st.session_state["int"] = int_val
            if txt == '' or txt.isnumeric():
                print("Loc Func in If")
                st.write("Wrong Input")

            else:
                print("Loc Func in Else")
                lat,long = get_coordinates(txt)
                
                max,event_id = get_event_id(lat,long)
                
                if event_id:
                    st.write("Event ID: ", event_id)
                    #params = {"idx_id": str(event_id)[-2:]}
                    params = {"idx_id": random.randrange(10,50), "location": txt}
                    headers = {'Authorization' : st.session_state.authToken}
                    URL = API_URL + "/event"
                    print(URL)
                    r = requests.get(URL,params=params,headers=headers)
                    
                    try:
                        r_json = r.json()
                        if r_json.get('message') and not r_json.get('data'):
                            st.write(r_json.get('message'))
                        elif r_json:
                            image_b64 = r_json.get('data')
                            with open(os.path.join(images_dir, 'image.png'), "wb") as file:
                                file.write(base64.b64decode(image_b64))

                            st.image(os.path.join(images_dir, 'image.png'))
                        else:
                            st.write(r_json.get('message'))
                    except:
                        print(traceback.format_exc())
                        st.write(f'No records found for {txt}')
                else:
                    st.write("Location not found")

df_catalog = pd.read_csv('web_server/catlog_data.csv')
#df_catalog = pd.read_csv('./catlog_data.csv')
images_dir = './'



    # if st.session_state.isAuthenticated is True:
    #     user_container.empty()
    #     pass_container.empty()
    #     auth_container.empty()
    #     location_func()

if st.session_state.isAuthenticated is False:

    if auth_container.button('Authenticate'):

        if username == '' or password == '':
            # try to print an error message on frontend
            st.write("Please enter valid credentials")
        
        else:
            URL = API_URL + "/user/login"
            body = {
                "email": username,
                "password": password
            }
            login = requests.post(URL, data=json.dumps(body))
            print(login.text)
            try:
                login_json = login.json()
                if login_json:
                    access_token = login_json.get('access_token')
                    if access_token:
                        st.session_state.isAuthenticated = True
                        st.session_state.authToken = access_token
                        # txt = st.text_input('Location')
                        # st.button('Submit', on_click=location_func, args=(txt, ))
                        user_container.empty()
                        pass_container.empty()
                        auth_container.empty()
                        #txt = st.text_input('Location')
                        #st.button('Submit')

                        print("Loc Func Ex")
                            
                    else:
                        st.write("Invalid credentials")
            except:
                st.write("Error occured, please try again")


def process_summarization(server_url: str):
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    data = ''
    resp = requests.get(server_url, headers=headers, verify=False, timeout=8000)
    result = resp.json()
    summ = result["summary"][0]["summary_text"]
    return summ


def page_third():
    x=st.session_state.int
    st.session_state.int = x
    DATA_URL="web_server/eventnarratives.csv"
    data = st.cache(pd.read_csv)(DATA_URL)
    nlp_option = st.radio("Services", st.session_state["options"], key="radio")
    row = data["EPISODE_NARRATIVE"][x]
    docx = nlp(row)

    if nlp_option=="NER":
        spacy_streamlit.visualize_ner(docx,labels=nlp.get_pipe('ner').labels, show_table=False)

    if nlp_option=="Summarization":
        st.write("# Summarization")
        backend = f'https://gy7a332y3hu6ln3pj2ogfujxxq0lhroc.lambda-url.us-east-1.on.aws/summarizer/{x}'
        summarize = process_summarization(backend)
        st.write(summarize)


# df_catalog = pd.read_csv('./catlog_data.csv')
# images_dir = './'

# df_catalog = pd.read_csv('/Users/vachanabelgavi/Documents/BDS&IA/Big-Data-Systems-Team/BDSIA-A4/sevir_project-master/streamlit_server/web_server/catlog_data.csv')
# images_dir = '/Users/vachanabelgavi/Documents/BDS&IA/Big-Data-Systems-Team/BDSIA-A4/sevir_project-master/streamlit_server/web_server'


nlp = spacy.load('en_core_web_sm')

def main():

    pages = {
    "Weather Nowcast": page_second,
    "NLP": page_third
    }

    if "page" not in st.session_state:
        st.session_state.update({
            # Default page
            "page": "Weather Nowcast",

            # Default widget values
            "int": 0,
            "options": ["NER","Summarization"],
            "radio": "NER"
        })

    with st.sidebar:
        page = st.radio("Dashboard", tuple(pages.keys()))

    pages[page]()

    
if __name__ == "__main__":
    main()