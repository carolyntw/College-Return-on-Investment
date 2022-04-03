from google.cloud import firestore
from google.oauth2 import service_account

import streamlit as st
import json
import pandas as pd
import numpy
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import matplotlib.pyplot as plt

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

    state = df['state'].unique()
    state_choice = st.selectbox('Select your state:', state)
    university = df['name'].loc[df['state'] == state_choice].unique()
    university_choice = st.multiselect('Select your university:', university)

    # state_code1 = []
    # colleges = db.collection("tuition_cost").stream()
    # for college in colleges:
    #     st.write("!")
    #     state_c = college.to_dict()["state_code"]
    #     st.write(state_c)
    #     if state_c not in state_code1:
    #         state_code1.append(state_c)

    data_dict = {}
    # column = ["College", "In State Total", "Out Of State Total", "Debt", "Early Career Pay", "Debt-Income Ratio"]
    all_tuition = []
    all_ratio = []
    
    all_college = pd.DataFrame()
    for i in university_choice:
        name_doc_ref = db.collection("tuition_cost").document(i)
        name_doc = name_doc_ref.get()

        data_dict["College"] = [name_doc.id]
        in_tuition = name_doc.to_dict()["in_state_total"]
        data_dict["In State Total"] = [in_tuition]
        out_tuition = name_doc.to_dict()["out_of_state_total"]
        data_dict["Out Of State Total"] = [out_tuition]
        all_tuition.append(out_tuition)
        # data = pd.DataFrame.from_dict(datas, orient='index', columns=[i]).sort_index()
        # data = data.transpose()

        # get the debt
        debt = 0
        state = name_doc.to_dict()["state"]
        loan_by_state = db.collection("student_loan_by_state").document(state)
        loan = loan_by_state.get()
        if loan.exists:
            loan_2021 = loan.to_dict()["2021"]
            data_dict["Debt"] = [loan_2021]
            debt = loan_2021
        else:
            data_dict["Debt"] = ["No data for this college"]

        # get the tuition fee
        income = 0
        salary_potential = db.collection("salary_potential").document(i)
        salary = salary_potential.get()
        if salary.exists:
            early_pay_back = salary.to_dict()["early_career_pay"]
            data_dict["Early Career Pay"] = [early_pay_back]
            income = early_pay_back
        else:
            data_dict["Early Career Pay"] = ["No data for this college"]


        if income == 0:
            data_dict["Debt-Income Ratio"] = ["No enough data"]
            all_ratio.append(0)
        else:
            ration = debt / income
            data_dict["Debt-Income Ratio"] = [ration]
            all_ratio.append(ration)

        one_college = pd.DataFrame(data_dict)

        all_college = pd.concat([all_college, one_college], ignore_index=True)

        # salary_potential = db.collection("salary_potential").document(i)
        # salary = doc_ref.get()
        # if salary.exists:
        #
        # else:
        #     early_pay_back = salary_potential.to_dict()["early_career_pay"]


    # st.dataframe(all_college)
    import altair as alt
    # plot the data
    # all_college["Debt"]
    # st.write(all_college["Out Of State Total"][1])
    # c = alt.Chart(all_college).mark_circle().encode(
    #     x='Out Of State Total', y='Debt-Income Ratio', size='College', color='c',
    #     tooltip=['Out Of State Total', 'Debt-Income Ratio', 'College']

    numpy_tuition = numpy.array(all_tuition)
    numpy_ratio = numpy.array(all_ratio)
    # plt.figure(figsize=(1, 1))
    width = st.sidebar.slider("plot width", 0.1, 25., 3.)
    height = st.sidebar.slider("plot height", 0.1, 25., 1.)

    fig, ax = plt.subplots(figsize=(width, height))
    # fig, ax = plt.subplots(figsize=(1, 1))
    ax.scatter(numpy_tuition, numpy_ratio, marker='o')
    # ax.legend(loc='upper center', shadow=True, fontsize='x-large')

    st.pyplot(fig)


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

    major = df2['Undergraduate Major'].unique()
    major_choice = st.selectbox('Select your major:', major)

    major_doc_ref = db.collection("degrees-that-pay-back").document(major_choice)
    major_doc = major_doc_ref.get()

    data2 = pd.DataFrame.from_dict(major_doc.to_dict(), orient='index', columns=['major'])
    st.dataframe(data2)

if navi == "Loan":
    total_loan = a = st.number_input('The amount of loan: ')
    monthly_pay = st.number_input('Monthly payment: ')
    annual_interest = st.number_input('Estimated annual interest (%): ')
    monthly_interest = annual_interest/100/12

    monthly_balance = total_loan - monthly_pay
    interest = monthly_balance * monthly_interest

    i = 2
    while i < 1200:
        monthly_balance = monthly_balance + interest -monthly_pay
        interest = monthly_balance * monthly_interest
                
        if monthly_balance < monthly_pay and st.button('Calculate'):
            st.write('Time to pay off loan debt:', i + 1, 'month(s) or', '{:.2f}'.format((i+1)/12, 2), 'year(s).')
            st.write('The total balance paid: $', "{:.2f}".format(round(monthly_pay*i + monthly_balance + interest, 2)))
            break
        i +=1
    
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




