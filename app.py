# TODO; Add minimum, add logic, change chart, toggle, design, llm 붙여서 개선하려면 어떻게 해야하는지? 무엇이 문제인지 도출, pill with question
# explain calculation bot
# calculation

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

def project_mau(population, vector):
    return [population * element for population, element in zip(initial_population, vector)]

with st.container(border=True): 
    st.write("MAU Projection")

with st.container(border=True): 
    col1, col2 = st.columns(2)

    user_age = int(col1.number_input("1. User Age", step=1, key="user_age"))

    month = int(col1.number_input("2. Month", step=1, key="month"))

    initial_population = [col1.number_input("2. Initial Population", step=1, key=f"initial_population_0")]
    for age in range(1, user_age):    
        initial_population.append(col1.number_input(step=1, label_visibility ="collapsed", 
                                                    key=f"initial_population_{age}"))

    inflow = col1.number_input("3. Inflow", step=0.01, key=f"inflow")
    retention = [col1.number_input("4. Retention", step=0.01, min_value=0.0, max_value=1.0, key=f"retention_0")]
    for m in range(1, month):    
        retention.append(col1.number_input(step=0.01, min_value=0.0, max_value=1.0, label_visibility ="collapsed", 
                                           key=f"retention_{m}"))

    col2.write(f"""MAU over {month} months""")
    toggle_on = col2.toggle("Show by user age")

    chart_data = pd.DataFrame(
    {
        "col1": np.random.randn(20),
        "col2": np.random.randn(20),
        "col3": np.random.choice(["A", "B", "C"], 20),
    }
    )

    if toggle_on: 
        # by user age
        col2.line_chart(chart_data, x="col1", y="col2", color="col3")
    else:
        # by total
        col2.line_chart(chart_data, x="col1", y="col2", color="col3")



