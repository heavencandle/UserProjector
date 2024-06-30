# MAU Projection Tool

This project is a Streamlit application that projects Monthly Active Users (MAU) based on a Leslie matrix. The tool allows users to input initial population data, inflow rate, and retention rates, and then generates projections for future periods. The application also provides insights using an LLM (Language Learning Model) to help analyze the population trends.

## Features

- **User Inputs**: Allows users to input initial population data, inflow rate, and retention rates.
- **Projection Calculation**: Uses a Leslie matrix to calculate population projections over a specified number of periods.
- **Visualization**: Provides line charts to visualize the population projections by user age or as a total.
- **Insights**: Generates insights using an LLM to analyze population trends.
- **Detailed Calculations**: Displays detailed calculations for each period in an expandable section.

## Installation

To run this project, you need to have Python installed. You can install the required dependencies using `pip`.

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/mau-projection-tool.git
    ```

2. Navigate to the project directory:
    ```bash
    cd mau-projection-tool
    ```

3. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

4. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```

2. Open the provided local URL in your web browser.

3. Use the application interface to input the user age, number of periods, initial population, inflow rate, and retention rates.

4. Click the "Confirm" button to generate the projections.

5. Toggle between showing projections by user age or total MAU.

6. View detailed calculations by expanding the "See calculation" section.

## Leslie Matrix and Initial Population

### Leslie Matrix

The Leslie matrix is a matrix used in population ecology to model the dynamics of a population. It is particularly useful for projecting the number of active users (MAU) in different age groups over time.

- **First Row**: Only the element at [0,0] is non-zero. This element represents the inflow rate change (inflow_Month2/inflow_Month1), indicating the growth rate of new individuals entering the population.
- **Diagonal Elements**: These elements have non-zero values at positions [i+1, i] (e.g., [1,0], [2,1]). Each element indicates the retention rate as the ratio of the population in the next age group to the population in the current age group in the following period. For example, the element at [1,0] represents the retention rate for the first age group after one month, using just \(\text{retention}_1\) since there is no \(\text{retention}_0\).
- **Other Elements**: Typically zero because individuals do not transition directly from one non-adjacent age group to another (e.g., children do not become seniors directly).

### Initial Population

The initial population represents the number of active users in each age group at the start of the projection period. This is provided by the user and used as the starting point for projecting future active user numbers.

### How They Are Used

The Leslie matrix and initial population are used together to project the number of active users over a specified number of periods. The Leslie matrix defines how the population transitions between age groups, while the initial population provides the starting values. The projections are calculated by multiplying the Leslie matrix by the current population vector to get the population for the next period.

### Example

Suppose we have an initial population of 100 users in the first age group and 50 users in the second age group, with an inflow rate of 1.2 and retention rates of 0.8 and 0.9. The Leslie matrix and initial population would be:

- **Initial Population**: `[100, 50]`
- **Inflow Rate**: `1.2`
- **Retention Rates**: `[0.8, 0.9]`

The Leslie matrix would be generated as:

\[ \text{Leslie Matrix} = \begin{bmatrix}
1.2 & 0 \\
0.8 & 1.125
\end{bmatrix} \]

Using this matrix and the initial population, the tool will project the population for future periods.
