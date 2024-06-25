# TODO; Add minimum, fix logic, change chart, design, llm 붙여서 개선하려면 어떻게 해야하는지? 무엇이 문제인지 도출, pill with question

import streamlit as st
import pandas as pd
import numpy as np


def calc_vector(inflow, retention):
    vector = [inflow]
    
    for idx in range(len(retention)):
        if idx==0:
            vector.append(retention[idx])
        else:
            vector.append(retention[idx] / retention[idx-1])
    return vector

def project_mau(month, initial_population, vector):
    curr_mau = initial_population
    mau_list = [curr_mau]
    mau_by_month = {}
    mau_by_age = {}

    
    for m in range(month):
        next_mau = [m * v for m, v in zip(curr_mau, vector)]
        mau_list.append(next_mau)
        
        curr_mau = next_mau

    mau_list = np.array(mau_list)
    mau_by_month["month"] =[m for m in range(month+1)]
    mau_by_month["mau"] = mau_list.sum(axis=1)


    mau_by_age["month"] = [m for m in range(month+1)]
    for age, row in enumerate(np.transpose(mau_list)):
        mau_by_age[f"age_{age}"] = row
    
    st.write(mau_by_month)
    st.write(mau_by_age)

    return mau_by_month, mau_by_age

with st.container(border=True): 
    st.write("MAU Projection")

with st.container(border=True): 
    col1, col2 = st.columns(2)

    user_age = int(col1.number_input("1. User Age", step=1, key="user_age"))

    month = int(col1.number_input("2. Month", step=1, key="month"))

    initial_population = [col1.number_input("2. Initial Population", step=1, key=f"initial_population_0")]
    for age in range(0, user_age):    
        initial_population.append(col1.number_input("", step=1, label_visibility ="collapsed", 
                                                    key=f"initial_population_{age+1}"))

    inflow = col1.number_input("3. Inflow", step=0.01, key=f"inflow")
    retention = [col1.number_input("4. Retention", step=0.01, min_value=0.0, max_value=1.0, key=f"retention_0")]
    for m in range(1, user_age):    
        retention.append(col1.number_input("", step=0.01, min_value=0.0, max_value=1.0, label_visibility ="collapsed", 
                                           key=f"retention_{m}"))

    col2.write(f"""MAU over {month} months""")
    toggle_on = col2.toggle("Show by user age")

    vector = calc_vector(inflow, retention)
    mau_by_month, mau_by_age = project_mau(month, initial_population, vector)

    mau_by_month = pd.DataFrame(mau_by_month)
    mau_by_age = pd.DataFrame(mau_by_age)

    st.write(mau_by_month)
    st.write(mau_by_age)

    if toggle_on: 
        # by user age
        col2.line_chart(mau_by_age, x="month", y=[v for v in mau_by_age.columns.values if v!= "month"])
    else:
        # by total
        col2.line_chart(mau_by_month, x="month", y="mau")



