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

file_dict = {"Portfolio-by-Location-by-Age.json": "Location", "Portfolio-by-Location-by-Debt-Size.json": "Location",
            "salaries-by-region.json": "School Name", "student-loan-by-state.json":"state/area",
             "salaries-by-college-type.json": "School Name", "degrees-that-pay-back.json": "Undergraduate Major",
            "salary_potential.json": "name", "tuition_cost.json":"name"}
# file_dict = {"tuition_cost.json":"name"}

# file_dict = {}
for filename in os.listdir('data'):
    if filename.endswith('.json'):
        collectionName = filename.split('.')[0] # filename minus ext will be used as collection name
        str = 'data/' + filename
        f = open(str, 'r',encoding='utf-8-sig')
        docs = json.loads(f.read())
        for doc in docs:
            id = doc.pop(file_dict[filename], None)
            id = id.replace("/", "-")
            if id:
                db.collection(collectionName).document(id).set(doc, merge=True)
            else:
                db.collection(collectionName).add(doc)
            # st.write("done" + id)

        st.write("Done! "+filename)

st.write("DONE!")