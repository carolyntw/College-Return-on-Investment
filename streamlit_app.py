# *-* coding:utf8 *_*
# @Time: 2/25/22 00:05
# @Author: Yan
# @File: streamlit_app.py
# @Software: PyCharm


from google.cloud import firestore
from google.oauth2 import service_account


import streamlit as st
import json
import pandas as pd

# Authenticate to Firestore with the JSON account key.
# db = firestore.Client.from_service_account_json("firestore-key.json")

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="college-return-on-investment")


navi = st.sidebar.radio("Navigation", ["Home", "Data Display", "Contact Us"])

if navi == "Home":
    # st.set_page_config(layout="centered", page_icon="🎓", page_title="Diploma Generator")
    # st.title("🎓 Diploma PDF Generator")
    st.header('🎓 College Returen on Investment')
    st.write("When it comes to pursuing a college degree, many prospective students don’t know exactly where to start."
             " There are a lot of factors such as passion, strength, personality, tuition fee, debt after graduation, "
             "etc,... to take into account when choosing a major and which college to go to. Many prospective students "
             "don’t have the privilege of having family members or someone they know that had such experiences to help "
             "guide them. These students often fall into the groups of first generation college students and "
             "underrepresented minorities. Additionally, American college graduates have an average of $30000 loan debt. "
             "Some graduates may end up being in more debt due to the college they pick and/or the major they choose. "
             "We want to build a website that provides prospective college students an understanding of the finance "
             "factor when it comes to getting a college degree, especially for helping first generation college students "
             "and underrepresented minorities who don’t have much resources around them.")

if navi == "Data Display":
    # Create a reference to the Google post.
    # Create dataframe of the university names, state codes
    df = pd.read_json('data/tuition_cost.json')
    df2 = pd.read_json('data/degrees-that-pay-back.json')

    form = st.form(key="state_info")
    with form:
        cols = st.columns(1)
        state_code = df['state_code'].unique()  
        state_code_choice = cols[0].selectbox('Select your state:', state_code)
        submitted = st.form_submit_button(label="Submit")

    form2 = st.form(key="school_info")
    with form2:
        cols = st.columns(1)
        university = df['name'].loc[df['state_code'] == state_code_choice].unique()  
        university_choice = cols[0].selectbox('Select your university:', university)  
        submitted = st.form_submit_button(label="Submit")

    form3 = st.form(key="Major_info")
    with form3:
        cols = st.columns(1)
        major = df2['Undergraduate Major'].unique()  
        major_choice = cols[0].selectbox('Select your major:', major) 
        submitted = st.form_submit_button(label="Submit")

    name_doc_ref = db.collection("tuition_cost").document(university_choice)
    name_doc = name_doc_ref.get()
    major_doc_ref = db.collection("degrees-that-pay-back").document(major_choice)
    major_doc = major_doc_ref.get()

    data = pd.DataFrame.from_dict(name_doc.to_dict(), orient='index', columns=[university_choice])
    # data2 = pd.DataFrame.from_dict(major_doc.to_dict(), orient='index', columns=[major])
    data2 = pd.DataFrame.from_dict(major_doc.to_dict(), orient='index', columns=['major'])
    st.dataframe(data)
    st.dataframe(data2)



if navi == "Contact Us":
    st.header('📝 Feedback')
    st.write("Our Email: jennyyan54@gmail.com")
    st.subheader("Send Us Your Feedback")
    form = st.form(key="feedback")
    with form:
        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")
        cols = st.columns(2)
        area = cols[0].text_input("Area Code")
        tel = cols[1].text_input("Tel.Number")
        email = st.text_input("Email")
        cont = st.columns(2)
        contact = cont[0].checkbox("May we contact you?")
        contact = cont[1].selectbox("Contact By", ('Tel.', 'Email'))
        feedback = st.text_area("Feedback")
        submitted = st.form_submit_button(label="Submit")
