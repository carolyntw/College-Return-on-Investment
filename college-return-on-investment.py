# *-* coding:utf8 *_*
# @Time: 2/25/22 00:05
# @Author: Yan
# @File: college-return-on-investment.py
# @Software: PyCharm

import streamlit as st
from google.cloud import firestore
import json
from google.oauth2 import service_account
import os
import json

# Authenticate to Firestore with the JSON account key.
# db = firestore.Client.from_service_account_json("firestore-key.json")

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="college-return-on-investment")

file_dict = {"degrees-that-pay-back.json":"Undergraduate Major", "salaries-by-college-type.json": "School Name",
            "salary_potential.json": "name", "tuition_cost.json":"name"}

for filename in os.listdir('data'):
    if filename.endswith('.json'):
        collectionName = filename.split('.')[0] # filename minus ext will be used as collection name
        f = open('data/' + filename, 'r')
        docs = json.loads(f.read())
        for doc in docs:
            id = doc.pop(file_dict(filename), None)
            if id:
                db.collection(collectionName).document(id).set(doc, merge=True)
            else:
                db.collection(collectionName).add(doc)



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
    doc_ref = db.collection("Tuition").document("Tuition")

    form = st.form(key="school_info")
    with form:
        cols = st.columns(3)
        state = cols[0].selectbox(
            'State',
            ('CA', 'NY', 'OH'))
        university = cols[1].selectbox(
            'University',
            ('USC', 'SJSU', 'UCLA','UCI'))
        major = cols[2].selectbox(
            'Major',
            ('Computer Science', 'Applied Data Science', 'Art'))
        submitted = st.form_submit_button(label="Submit")

    # Then get the data at that reference.
    doc = doc_ref.get()

    # Let's see what we got!
    st.write("The id is: ", doc.id)
    st.write("The contents are: ", doc.to_dict())

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


