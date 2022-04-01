from google.cloud import firestore
from google.oauth2 import service_account

import streamlit as st
import json
import pandas as pd
import numpy
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="college-return-on-investment")

navi = st.sidebar.radio("Navigation", ["Home", "Data Display", "Loan", "Contact Us"])

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

    state_code = df['state_code'].unique()
    state_code_choice = st.selectbox('Select your state:', state_code)
    university = df['name'].loc[df['state_code'] == state_code_choice].unique()
    university_choice = st.multiselect('Select your university:', university)

    # state_code1 = []
    # colleges = db.collection("tuition_cost").stream()
    # for college in colleges:
    #     st.write("!")
    #     state_c = college.to_dict()["state_code"]
    #     st.write(state_c)
    #     if state_c not in state_code1:
    #         state_code1.append(state_c)

    # q = table.where(u'state_code', u'==', True)
    # for i in db.collection("tuition_cost").get().id:
    #     st.write(i)
    docs = db.collection("tuition_cost").stream()
    st.write("111")
    for doc in docs:
        st.write(doc.to_dict()["state_code"])
    # st.write(len(state_code1))
    st.write(len(state_code))

    df = pd.DataFrame()
    for i in university_choice:
        name_doc_ref = db.collection("tuition_cost").document(i)
        name_doc = name_doc_ref.get()
        data = pd.DataFrame.from_dict(name_doc.to_dict(), orient='index', columns=[i]).sort_index()
        data = data.transpose()
        df = pd.concat([df, data], ignore_index=True)

    st.dataframe(df)


    # function source: https://share.streamlit.io/streamlit/example-app-interactive-table/main
    def aggrid_interactive_table(df: pd.DataFrame):
        """Creates an st-aggrid interactive table based on a dataframe.

        Args:
            df (pd.DataFrame]): Source dataframe

        Returns:
            dict: The selected row
        """
        options = GridOptionsBuilder.from_dataframe(
            df, enableRowGroup=True, enableValue=True, enablePivot=True
        )

        options.configure_side_bar()

        options.configure_selection("single")
        selection = AgGrid(
            df,
            enable_enterprise_modules=True,
            gridOptions=options.build(),
            theme="light",
            update_mode=GridUpdateMode.MODEL_CHANGED,
            allow_unsafe_jscode=True,
        )

        return selection


    selection = aggrid_interactive_table(df=df)

    major = df2['Undergraduate Major'].unique()
    major_choice = st.selectbox('Select your major:', major)

    major_doc_ref = db.collection("degrees-that-pay-back").document(major_choice)
    major_doc = major_doc_ref.get()

    data2 = pd.DataFrame.from_dict(major_doc.to_dict(), orient='index', columns=['major'])
    st.dataframe(data2)

if navi == "Loan":
    st.write("loan")

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




