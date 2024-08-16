# !!!important caching!!!! and button
# TODO; Add minimum, fix logic, change chart, design,
# zero division, placeholder
# llm for key insight
# Change to month label

import streamlit as st
import pandas as pd
import numpy as np
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def generate_leslie(matrix_size, inflow, retention):
    leslie = np.zeros((matrix_size, matrix_size))

    leslie[0, 0] = inflow

    for idx in range(len(retention)):
        if idx == 0:
            leslie[idx + 1, 0] = retention[idx]
        else:
            leslie[idx + 1, idx] = retention[idx] / retention[idx - 1]

    st.session_state["leslie"] = leslie
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
    mau_by_period_arr = population_history.sum(axis=1)

    # Creating mau_by_age dictionary
    mau_by_age = {
        "period": list(range(time_periods + 1))
    }
    mau_by_age.update({
        f"age_{age}": population_history[:, age] for age in range(population_history.shape[1])
    })
    mau_by_age_arr= [population_history[:, age] for age in range(population_history.shape[1])]

    st.session_state["mau_by_period"] = mau_by_period
    st.session_state["mau_by_period_arr"] = mau_by_period_arr
    st.session_state["mau_by_age"] = mau_by_age
    st.session_state["mau_by_age_arr"] = mau_by_age_arr
    st.session_state["calculations"] = calculations

    return mau_by_period, mau_by_period_arr, mau_by_age, mau_by_age_arr, calculations

def dataframe_to_html(dataframe):
    return dataframe.to_html(index=False, header=False)

@st.cache_data(show_spinner=False)
def extract_insight(leslie_matrix, initial_population, retentions, projections):
    projections_str = "\n\n".join([f"Month {i+1}: {p.tolist()}" for i, p in enumerate(projections)])

    system_prompt = f"""
    Use the following vector and matrices to answer the question.

    You are a data analyst extracting insights for a CEO, product manager, or product owner,
    and you are trying to analyze the number of active users in a product such as website or application.
    Determine the reasons for population increase or decrease and suggest ways to increase the population if it is decreasing. 
    Important:Respond in no more than than 5 sentences, and try to contain:
    - the most effective reasons based on inflow and retention.
    - or which age group they need to concentrate on.
    DO NOT confuse the idea of retention and survivorship, use straightforward word and do not confusing use word like "retention rate" rather use retention or survivorship.
    DO NOT contain content that you are not certain. 

    Explanation of the Leslie Matrix Structure
    1. Rows and Columns Represent Age Groups:
    The population is divided into different age groups.
    Each row and column represents one of these age groups.
    Age means how many months they have been using the product, user age starts from 0 when they entered the product and change to 1 the next month.
    
    2. Structure of the Matrix:
    The matrix is typically square, meaning it has the same number of rows and columns.
    The size of the matrix (e.g., 3x3, 4x4) depends on the number of age groups considered.
    
    3.Elements of the Matrix:
    - The numbers in the matrix represent different rates that affect the population.
    - First Row: Only the element at [0,0] is non-zero. This element represents the inflow rate change (inflow_Month2/inflow_Month1), indicating the growth rate of new individuals entering the population.
    - Diagonal Elements: These elements have non-zero values at positions [i+1, i] (e.g., [1,0], [2,1]). Each element indicates the retention rate as the ratio of the population in the next age group to the population in the current age group in the following period. For example, the element at [1,0] represents the retention rate for the first age group after one month, using just \(\text{retention}_1\) since there is no \(\text{retention}_0\).
    - Other Elements: Typically zero because individuals do not transition directly from one non-adjacent age group to another (e.g., children do not become seniors directly).
    ----------
    Given Data
    Leslie matrix:
    {leslie_matrix}

    Initial population:
    {initial_population}

    Retention:
    {retentions}

    Here are the population projections for the next months:
    {projections_str}
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Please provide insights and analysis based on these projections.")
        ]
    )

    llm = ChatOpenAI()
    chain = (prompt | llm)
    response = chain.invoke({})

    return response

def draw_chart(toggle_on):
    mau_by_age = st.session_state.mau_by_age
    mau_by_period = st.session_state.mau_by_period

    leslie_matrix = st.session_state.leslie
    initial_population = st.session_state.initial_population

    retention = st.session_state.retention
    mau_by_age_arr = st.session_state.mau_by_age_arr
    
    if toggle_on: 
        # by user age
        st.line_chart(mau_by_age, x="period", y=[key for key in mau_by_age.keys() if key != "period"])
    else:
        # by total
        st.line_chart(mau_by_period, x="period", y="mau")
    st.write(extract_insight(leslie_matrix, initial_population, retention, mau_by_age_arr).content)

calculations, leslie_matrix = {}, []

with st.container(): 
    st.write("MAU Projection")

with st.container(): 
    col1, col2 = st.columns([3, 7])

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
            retention.append(st.number_input("", step=0.01, min_value=0.0, max_value=1.0, label_visibility ="collapsed", key=f"retention_{m}"))
        
        button_click = st.button("Comfirm")
        
        if button_click:
            if user_age>0 and time_periods>0:
                try:
                    st.session_state["button_click"]+=1
                    st.write(st.session_state["button_click"])
                except:
                    st.session_state["button_click"]=1
                    st.write(st.session_state["button_click"])
            else:
                st.toast("User Age and Month should be bigger than 0.")   
    

        st.session_state["time_periods"] = time_periods
        st.session_state["initial_population"] = initial_population
        st.session_state["retention"] = retention
        
    with col2:
        try: 
            if st.session_state.button_click >= 1:
                toggle_on=st.toggle("Show by user age")
                st.session_state["toggle_on"] = toggle_on

                leslie_matrix = generate_leslie(matrix_size=len(initial_population), inflow=inflow, retention=retention)
                mau_by_period, mau_by_period_arr, mau_by_age, mau_by_age_arr, calculations = project_mau(time_periods, initial_population, leslie_matrix)

                draw_chart(st.session_state["toggle_on"])
        except:
            pass
                

with st.container():
    try: 
        if st.session_state.button_click >= 1:
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
    except:
        pass



