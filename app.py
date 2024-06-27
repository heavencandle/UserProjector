# TODO; Add minimum, fix logic, change chart, design, llm 붙여서 개선하려면 어떻게 해야하는지? 무엇이 문제인지 도출, pill with question
# zero division, placeholder
# llm for key insight
# Change to month label

import streamlit as st
import pandas as pd
import numpy as np


def generate_leslie(matrix_size, inflow, retention):
    leslie = np.zeros((matrix_size, matrix_size))

    leslie[0, 0] = inflow

    for idx in range(len(retention)):
        if idx == 0:
            leslie[idx + 1, 0] = retention[idx]
        else:
            leslie[idx + 1, idx] = retention[idx] / retention[idx - 1]

    return leslie
    

def project_mau(time_periods, initial_population, leslie_matrix):
    current_population = initial_population
    population_history = [current_population]
    calculations = []
    
    for period  in range(time_periods):
        next_population = np.dot(leslie_matrix, current_population)
        calculations.append({
            "Period": period,
            "Current Population": current_population,
            "Leslie Matrix": leslie_matrix,
            "Next Population": next_population
        })
        population_history.append(next_population)
        current_population = next_population

    population_history = np.array(population_history)

    # Creating mau_by_period dictionary
    mau_by_period = {
        "period": list(range(time_periods + 1)),
        "mau": population_history.sum(axis=1)
    }

    # Creating mau_by_age dictionary
    mau_by_age = {
        "period": list(range(time_periods + 1))
    }
    mau_by_age.update({
        f"age_{age}": population_history[:, age] for age in range(population_history.shape[1])
    })

    return mau_by_period, mau_by_age, calculations


def dataframe_to_html(dataframe):
    return dataframe.to_html(index=False, header=False)

calculations, leslie_matrix = {}, []

with st.container(): 
    st.write("MAU Projection")

with st.container(): 
    col1, col2 = st.columns(2)

    with col1:
        user_age = int(st.number_input("1. User Age", step=1, key="user_age"))

        time_periods = int(st.number_input("2. Month", step=1, key="month"))

        initial_population = [st.number_input("2. Initial Population", step=1, key=f"initial_population_0")]
        for age in range(0, user_age):    
            initial_population.append(st.number_input("", step=1, label_visibility ="collapsed", 
                                                        key=f"initial_population_{age+1}"))

        inflow = st.number_input("3. Inflow", step=0.01, key=f"inflow")
        retention = [st.number_input("4. Retention", step=0.01, min_value=0.0, max_value=1.0, key=f"retention_0")]
        for m in range(1, user_age):    
            retention.append(st.number_input("", step=0.01, min_value=0.0, max_value=1.0, label_visibility ="collapsed", 
                                            key=f"retention_{m}"))
    with col2:
        st.write(f"""MAU over {time_periods} months""")
        toggle_on = st.toggle("Show by user age")

        leslie_matrix = generate_leslie(matrix_size=len(initial_population), inflow=inflow, retention=retention)
        mau_by_period, mau_by_age, calculations = project_mau(time_periods, initial_population, leslie_matrix)

        if toggle_on: 
            # by user age
            st.line_chart(mau_by_age, x="period", y=[key for key in mau_by_age.keys() if key != "period"])
        else:
            # by total
            st.line_chart(mau_by_period, x="period", y="mau")
        st.write(f"""Key insight zone""")


with st.container():
    with st.expander("See calculation"):
        st.write('''
            This section describes how the populations were calculated at each time period.
        ''')

        # CSS for better table design
        table_style = """
        <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px 12px;
            text-align: right;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        </style>
        """

        st.markdown(table_style, unsafe_allow_html=True)

        def format_population(data):
            return pd.DataFrame(data).astype(int)

        def format_retention(data):
            return pd.DataFrame(data).applymap(lambda x: f"{x:.2f}")

        for calc in calculations:
            st.write(f"**Calculation for Period {calc['Period']}**")

            # Create columns for side-by-side display
            col1, col2, col3 = st.columns([2.5, 5, 2.5])

            # Display current population
            with col1:
                st.write("Current Population")
                current_pop_df = format_population(calc["Current Population"])
                current_pop_html = current_pop_df.to_html(index=False, header=False)
                st.write(current_pop_html, unsafe_allow_html=True)

            # Display Leslie matrix
            with col2:
                st.write("Leslie Matrix")
                leslie_df = format_retention(calc["Leslie Matrix"])
                leslie_html = leslie_df.to_html(index=False, header=False)
                st.write(leslie_html, unsafe_allow_html=True)

            # Display next population
            with col3:
                st.write("Next Population")
                next_pop_df = format_population(calc["Next Population"])
                next_pop_html = next_pop_df.to_html(index=False, header=False)
                st.write(next_pop_html, unsafe_allow_html=True)





