# *-* coding:utf8 *_*
# @Time: 2/25/22 00:05
# @Author: Yan
# @File: streamlit_app.py
# @Software: PyCharm

import streamlit as st
from google.cloud import firestore
import json
from google.oauth2 import service_account



# Authenticate to Firestore with the JSON account key.
# db = firestore.Client.from_service_account_json("firestore-key.json")

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="college-return-on-investment")


navi = st.sidebar.radio("Navigation", ["Home", "Data Display", "Contact Us"])

if navi == "Home":
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
    doc_ref = db.collection("Tuition").document("Tuition")

    # Then get the data at that reference.
    doc = doc_ref.get()

    # Let's see what we got!
    st.write("The id is: ", doc.id)
    st.write("The contents are: ", doc.to_dict())




