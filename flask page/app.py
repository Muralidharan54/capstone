import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template
import io
import base64

app = Flask(__name__)

def sql_query():

    server = 'MSI'
    database = 'src_data'
    username = 'INFA_role_2'
    password = 'abc123'
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    query = """
    SELECT 
        ci.INDICATOR_CODE,
        ci.INDICATOR_NAME,
        co.Country_ID,
        co.Country_Code,
        co.Region,
        co.IncomeGroup,
        co.CountryName,
        fe.RECORDED_YEAR,
        fe.EMISSION
    FROM dbo.DIM_INDICATOR ci
    INNER JOIN dbo.FACT_CO_2_EMISSION fe ON ci.INDICATOR_ID = fe.INDICATOR_ID
    INNER JOIN dbo.DIM_COUNTRY co ON fe.COUNTRY_ID = co.Country_ID
    """

    conn = pyodbc.connect(conn_str)
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@app.route('/')
def home():
    df=sql_query()
    charts = [
        {"image": render_plot_1(df), "text": ""},
        {"image": render_plot_2(df), "text": ""},
         {"image": render_plot_3(df), "text": ""}
    ]
    return render_template('charts.html', charts=charts)

if __name__ == '__main__':
    app.run(debug=True)


def render_plot_1(df):
    grouped = df.groupby(["IncomeGroup", "RECORDED_YEAR"])["EMISSION"].mean().reset_index()
    pivot_table = grouped.pivot(index="RECORDED_YEAR", columns="IncomeGroup", values="EMISSION")

    fig, ax = plt.subplots(figsize=(10, 6))
    for income_group in pivot_table.columns:
        ax.plot(pivot_table.index, pivot_table[income_group], marker='o', label=income_group)
    
    ax.set_title("CO2 Emissions by Income Group (per Year)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Emissions (metric tons per capita)")
    ax.legend(title="Income Group")
    ax.grid(True)
    fig.tight_layout()

    output = io.BytesIO()
    plt.savefig(output, format='png')
    output.seek(0)
    plt.close(fig)
    chart_data = base64.b64encode(output.getvalue()).decode('utf-8')
    output.close()
    plt.close()
    return chart_data


def render_plot_2(df):
    
    grouped = df[df.RECORDED_YEAR == 2020].groupby(["IncomeGroup"])["EMISSION"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(
        grouped["EMISSION"],
        labels=grouped["IncomeGroup"],
        autopct='%1.1f%%',
        startangle=140
    )
    ax.set_title("CO2 Emissions by Income Group (2020)")

    fig.tight_layout()

    output = io.BytesIO()
    plt.savefig(output, format='png')
    output.seek(0)
    plt.close(fig)
    chart_data = base64.b64encode(output.getvalue()).decode('utf-8')
    output.close()
    plt.close()
    return chart_data

def render_plot_3(df):
    grouped_region_year = df.groupby(["RECORDED_YEAR", "Region"])["EMISSION"].mean().reset_index()
    pivot_region = grouped_region_year.pivot(index="RECORDED_YEAR", columns="Region", values="EMISSION")


    fig, ax = plt.subplots(figsize=(10, 6))

    for region in pivot_region.columns:
        ax.plot(pivot_region.index, pivot_region[region].T,  label=region,marker='o')
        
    ax.set_title("Trend of CO2 Emissions by Region (Per Year)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Emissions")
    ax.legend(title="Region", loc="upper left")
    ax.grid(True)

    fig.tight_layout()
    output = io.BytesIO()
    plt.savefig(output, format='png')
    output.seek(0)
    plt.close(fig)
    chart_data = base64.b64encode(output.getvalue()).decode('utf-8')
    output.close()
    plt.close()
    return chart_data
