from os import major
from google.cloud import firestore
from google.oauth2 import service_account

import streamlit as st
import json
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from PIL import Image
import altair as alt

import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="college-return-on-investment")

navi = st.sidebar.radio("Navigation", ["Home", "College", "Loan Repayment Calculator", "Contact Us"])

if navi == "Home":
    # st.set_page_config(layout="centered", page_icon="🎓", page_title="Diploma Generator")
    # st.title("🎓 Diploma PDF Generator")
    with open('choice.txt', 'w') as f:
        f.write('None')
    st.header('Home Page')
    st.subheader("The motivation behind this webpage's idea:")
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
    image = Image.open('college-roi.jpeg')

if navi == "Colleges/Majors":
    # Create a reference to the Google post.
    # Create dataframe of the university names, state codes
    
    st.header('Colleges/Majors')
    st.write("Don't know which university to go to?")
    st.write("Don't know which major is financially prosperous?")
    st.write("We got you! Choose the category you wanna explore further.")

    choice = ''
    with open('choice.txt') as f:
        choice = f.readlines()

    left, right = st.columns(2)
    with left:
        university_button = st.button("Universities")
    with right:
        major_button = st.button("Majors")

    # university_button = st.button("Universities")
    # major_button = st.button("Majories")
    # st.write(university_button)
    # st.write(major_button)

    if university_button == False and major_button == False and choice[0] == 'university':
        university_button = True
        # major_button = False
    if university_button == False and major_button == False and choice[0] == 'major':
        major_button = True
        # university_button = False

    if university_button:
        with open('choice.txt', 'w') as f:
            f.write('university')
    if major_button:
        with open('choice.txt', 'w') as f:
            f.write('major')

    # st.write(university_button)
    # st.write(major_button)

    if university_button:

        # df = pd.read_json('data/tuition_cost.json')
        # df2 = pd.read_json('data/degrees-that-pay-back.json')

        # state = df['state'].unique()

        colleges = db.collection("tuition_cost")
        colleges_stream = colleges.stream()
        # state_code = []
        # for college in colleges_stream:
        #     state_c = college.to_dict()["state"]
        #     if state_c not in state_code:
        #         state_code.append(state_c)

        # state_choice = st.multiselect('Select your state:', state_code)
        # university_list = []
        # for i in state_choice:
        #     # university = df['name'].loc[df['state'] == i].unique()
        #     universities = colleges.where(u'state', u'==', i).stream()
        #     # st.write(universities)
        #     for university in universities:
        #         university_name = university.id
        #         # st.write(university_name)
        #         university_list.append(university_name)
        #     # for n in university:
        #     #     university_list.append(n)
        university_list = []
        for college in colleges_stream:
            university = college.id
            university_list.append(university)
            # if state_c not in state_code:
            #     state_code.append(state_c)
        # s_dict = pd.read_json('data/salary_potential.json')
        # t_dict = pd.read_json('data/tuition_cost.json')
        # merge = pd.merge(s_dict, t_dict, on="name")
        # final_university = merge['name']
        # salaries = db.collection("salary_potential").stream()
        # st.write(len(salaries))

        # final_university = []
        # for salary in salaries:
        #     if salary.id in university_list:
        #         university_list.append(salary.id)
        # print()
        university_choice = st.multiselect('Select your university:', university_list)
        # university_choice2 = st.select('Select your university:', university_list)
        # university_choice3 = st.select('Select your university:', university_list)

        data_dict = {}
        # column = ["College", "In State Total", "Out Of State Total", "Debt", "Early Career Pay", "Debt-Income Ratio"]
        all_tuition = []
        all_ratio = {}

        all_college = pd.DataFrame()
        for i in university_choice:
            name_doc_ref = db.collection("tuition_cost").document(i)
            name_doc = name_doc_ref.get()

            data_dict["College"] = [name_doc.id]
            in_tuition = name_doc.to_dict()["in_state_total"]
            data_dict["In State Tuition"] = [in_tuition]
            out_tuition = name_doc.to_dict()["out_of_state_total"]
            data_dict["Out Of State Tuition"] = [out_tuition]
            all_tuition.append(out_tuition)
            # data = pd.DataFrame.from_dict(datas, orient='index', columns=[i]).sort_index()
            # data = data.transpose()

            # get the debt
            debt = 0
            state = name_doc.to_dict()["state"]
            loan_by_state = db.collection("student-loan-by-state").document(state)
            loan = loan_by_state.get()
            if loan.exists:
                loan_2021 = int(loan.to_dict()["2021 Average"])
                data_dict["Debt"] = [loan_2021]
                debt = loan_2021
            else:
                data_dict["Debt"] = ["No data for this college"]

            # get the tuition fee
            income = 0
            salary_potential = db.collection("salary_potential").document(i)
            salary = salary_potential.get()
            if salary.exists:
                early_pay_back = int(salary.to_dict()["early_career_pay"])
                data_dict["Early Career Pay"] = [early_pay_back]
                income = early_pay_back
            else:
                data_dict["Early Career Pay"] = ["No data for this college"]

            if income == 0:
                data_dict["Debt-Income Ratio"] = ["No enough data"]
                all_ratio[i] = 0
            else:
                ratio1 = debt / income
                data_dict["Debt-Income Ratio"] = [ratio1]
                all_ratio[i] = ratio1

            one_college = pd.DataFrame(data_dict)

            all_college = pd.concat([all_college, one_college], ignore_index=True)

            # salary_potential = db.collection("salary_potential").document(i)
            # salary = doc_ref.get()
            # if salary.exists:
            #
            # else:
            #     early_pay_back = salary_potential.to_dict()["early_career_pay"]


        # st.dataframe(all_college)
        usa_debt = int(db.collection("student-loan-by-state").document("United States").get().to_dict()["2021 Average"])
        usa_income = int(db.collection("student-loan-by-state").document("United States").get().to_dict()["2021 Salary"])
        all_ratio["USA Average"] = usa_debt/usa_income
        # use bar_chart
        ratios = pd.DataFrame.from_dict(all_ratio, orient="index")
        st.bar_chart(ratios, height=380)

        # use altair_chart
        ratio_items = all_ratio.items()
        ratio_list = list(ratio_items)
        ratio_df = pd.DataFrame(ratio_list, columns=["College", "ratio"])
        c = alt.Chart(ratio_df).mark_bar().encode(x='College', y='ratio', color =alt.value('orange'))

        st.altair_chart(c, use_container_width=True)

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


        selection = aggrid_interactive_table(df=all_college)

    if major_button:
        # with open('choice.txt', 'w') as f:
        #     f.write('major')
        majors = db.collection("degrees-that-pay-back")
        majors_stream = majors.stream()
        majors_list = []
        for majors in majors_stream:
            major = majors.id
            majors_list.append(major)
        m_dict = pd.read_json('data/degrees-that-pay-back.json')
        del m_dict["Percent change from Starting to Mid-Career Salary"]
        del m_dict["Mid-Career Median Salary"]
        m_data = pd.DataFrame(m_dict)

        majors_choice = st.multiselect('Select your major (At most three):', m_dict)
        major_dict = {}
        all_major = pd.DataFrame()
        for i in majors_choice:
            major_doc_ref = db.collection('degrees-that-pay-back').document(i)
            major_doc = major_doc_ref.get()
            major_dict["Undergraduate Major"] = [major_doc.id]

            one_major = pd.DataFrame(major_dict)
            all_major = pd.concat([all_major, one_major], ignore_index=True)
        if len(all_major) > 0:
            final_m_data = all_major.merge(m_data, on="Undergraduate Major")

            plot = final_m_data.drop(columns=['Undergraduate Major'])
            plot = plot.replace('\$', '', regex=True).replace('\.', '', regex=True).replace('\,', '', regex=True)
            if len(final_m_data) == 1:

                x1_columnName = plot.columns.values.tolist()
                x1_rowValue = plot.loc[0, :].values.tolist()
                n = 5
                r = np.arange(n)
                width = 0.25
                fig = plt.figure(figsize=(24, 6))
                plt.rcParams['font.size'] = '14'
                plt.bar(r,x1_rowValue,color = 'mistyrose',width = width, edgecolor = 'black',label = all_major.at[0,'Undergraduate Major'])
                plt.xticks(r + width / 4, x1_columnName)
                plt.legend(prop={"size": 18})
                st.pyplot(fig)

            elif len(final_m_data) == 2:
                x1_columnName = plot.columns.values.tolist()
                x1_rowValue = plot.loc[0, :].values.tolist()
                x2_rowValue = plot.loc[1, :].values.tolist()

                n = 5
                r = np.arange(n)
                width = 0.25
                fig = plt.figure(figsize=(24, 6))
                plt.rcParams['font.size'] = '14'
                plt.bar(r,x1_rowValue,color = 'mistyrose',width = width, edgecolor = 'black',label = all_major.at[0,'Undergraduate Major'])
                plt.bar(r+0.25,x2_rowValue,color = 'coral',width = width,edgecolor = 'black',label = all_major.at[1,'Undergraduate Major'])
                plt.xticks(r + width / 3, x1_columnName)
                plt.legend(prop={"size": 18})
                st.pyplot(fig)

            elif len(final_m_data) == 3:
                x1_columnName = plot.columns.values.tolist()
                x1_rowValue = plot.loc[0, :].values.tolist()
                x2_rowValue = plot.loc[1, :].values.tolist()
                x3_rowValue = plot.loc[2, :].values.tolist()

                n = 5
                r = np.arange(n)
                width = 0.25
                fig = plt.figure(figsize=(24, 6))
                plt.rcParams['font.size'] = '14'
                plt.bar(r,x1_rowValue,color = 'mistyrose',width = width, edgecolor = 'black',label = all_major.at[0,'Undergraduate Major'])
                plt.bar(r+0.25,x2_rowValue,color = 'coral',width = width,edgecolor = 'black',label = all_major.at[1,'Undergraduate Major'])
                plt.bar(r+0.5,x3_rowValue,color = 'orangered',width = width,edgecolor = 'black',label = all_major.at[2,'Undergraduate Major'])
                plt.xticks(r + width, x1_columnName)
                plt.legend(prop={"size": 18})
                st.pyplot(fig)

if navi == "Loan Repayment Calculator":
    with open('choice.txt', 'w') as f:
        f.write('None')
    st.header('Loan Repayment Calculator')
    st.text("Finding out approximately how much time and money for loan debt repaynment can be challenging, but we are here to help!"
#    st.text("Input your information and we will help you "
#            "calculate how much time it would take for you to pay off your loan debt as well as the total money including interest you would pay over the time!")
    total_loan = st.number_input('The amount of loan taken: ')
    monthly_pay = st.number_input('Estimated monthly payment: ')
    annual_interest = st.number_input('Estimated annual interest (%): ')

    monthly_interest = annual_interest / 100 / 12

    monthly_balance = total_loan - monthly_pay
    interest = monthly_balance * monthly_interest
    if st.button('Calculate'):
        i = 2
        while i < 1200:
            monthly_balance = monthly_balance + interest - monthly_pay
            interest = monthly_balance * monthly_interest

            if monthly_balance < monthly_pay:
                st.write('It would take you approximately ', i + 1, 'month(s) or', '{:.2f}'.format((i + 1) / 12, 2),
                         'year(s) to pay off loan debt.')
                st.write('Total balance you would pay: $',
                         "{:.2f}".format(round(monthly_pay * i + monthly_balance + interest, 2)))
                break
            i += 1

if navi == "Contact Us":
    with open('choice.txt', 'w') as f:
        f.write('None')
    st.header('Contact Us')
    st.text("We appricate you for trying out our webpage and we would love to hear your thoughts on what you love and/or any improvements we can make!")
    st.text("Submit the form below and we will take a look at it as soon as possible!")
#    st.write("Our Email: jennyyan54@gmail.com")
#    st.subheader("Send Us Your Feedback")
    form = st.form(key="feedback", clear_on_submit=True)
    with form:
        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")
        cols = st.columns(2)
        area = cols[0].text_input("Area Code")
        tel = cols[1].text_input("Phone Number")
        email = st.text_input("Email Address")
        cont = st.columns(2)
        contact1 = cont[0].checkbox("May we contact you?")
        contact2 = cont[1].selectbox("Contact By", ('Phone', 'Email'))
        feedback = st.text_area("Feedback")
        submitted = st.form_submit_button(label="Submit")

        if submitted:
            st.success("Submit Successfully!")
            doc_ref = db.collection("Feedback").document(f"{fname} {lname}")
            doc_ref.set({
                "Area Code": area,
                "Tel.Number": tel,
                "Email": email,
                "May we contact you": contact1,
                "Contact By": contact2,
                "Feedback": feedback
            })