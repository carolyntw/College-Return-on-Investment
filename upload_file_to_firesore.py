# *-* coding:utf8 *_*
# @Time: 3/20/22 14:28
# @Author: Yan
# @File: upload_file_to_firesore.py
# @Software: PyCharm

import streamlit as st
from google.cloud import firestore
import json
from google.oauth2 import service_account
import os

# Authenticate to Firestore with the JSON account key.
# db = firestore.Client.from_service_account_json("firestore-key.json")

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="college-return-on-investment")

file_dict = {"degrees-that-pay-back.json": "Undergraduate Major", "salaries-by-college-type.json": "School Name",
            "salary_potential.json": "name", "tuition_cost.json":"name"}

for filename in os.listdir('data'):
    if filename.endswith('.json'):
        collectionName = filename.split('.')[0] # filename minus ext will be used as collection name
        f = open('data/' + filename, 'r')
        docs = json.loads(f.read())
        for doc in docs:
            id = doc.pop(file_dict[filename], None)
            id = id.replace("/", "-")
            st.write(id)
            if id:
                db.collection(collectionName).document(id).set(doc, merge=True)
            else:
                db.collection(collectionName).add(doc)
            # st.write("done" + id)

        st.write("done"+filename)

st.write("done")