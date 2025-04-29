from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv, find_dotenv
from dash import Dash, html, dcc, callback, Output, Input, State
from sqlalchemy import create_engine

import dash_ag_grid as dag
import pandas as pd
import re
import base64
import io
import os
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg") #disable GUi display 

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama3-70b-8192",
)

#function to extract the figure from generated code
def get_fig_from_code(code):
    local_variables = {}  # Initialize as an empty dictionary
    exec(code, {}, local_variables)
    return local_variables.get("fig")
        
#function parse the uploaded file
def parse_contents(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    
    try:
        if "csv" in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["ther was an error processing this file"])

    return html.Div([
        html.H5(filename),
        dag.AgGrid(
            rowData=df.to_dict("records"),
            columnDefs=[{"field": i} for i in df.columns],
            defaultColDef={"filter": True, "sortable": True, "floatingFilter": True}
        ),
        dcc.Store(id="stored-data", data=df.to_dict("records")),
        dcc.Store(id="stored-file-name", data=filename),
        html.Hr()
    ])
def fetch_data_from_db():
    engine = create_engine("postgresql://username:password@localhost:5432/mydatabase")
    query = "SELECT * FROM sales_data"
    df = pd.read_sql(query, engine)
    return df

#dash app
app = Dash(suppress_callback_exceptions=True)
app.layout = [
    html.H1("Agentic AI for creating graphs"),
    dcc.Upload(
        id="upload-data",
        children=html.Div(["Drag and drop or ", html.A("Select a File")]),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px"
        },
        multiple=True,
    ),
    html.Div(id="output-grid"),
    dcc.Textarea(id="user-request", style={"width": "50%", "height": "50", "margin-top": 20}),
    html.Br(),
    html.Button("Submit", id="my-button"),
    dcc.Loading([
        html.Div(id="my-figure", children=""),
        dcc.Markdown(id="content", children="")
    ], type="cube")
]

#Callback for uploading files
@callback(
    Output("output-grid", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        return [parse_contents(c, n) for c, n in zip(list_of_contents, list_of_names)]
    return html.Div("No file uploaded")

#allback for creating graph based on user input
@callback(
    Output("my-figure", "children"),
    Output("content", "children"),
    Input("my-button", "n_clicks"),
    State("user-request", "value"),
    State("stored-data", "data"),
    State("stored-file-name", "data")
)
def create_graph(_, user_input, file_data, file_name):
    if file_name is None:
        df = fetch_data_from_db()
    else:
        df = pd.DataFrame(file_data)
    csv_string = df.head().to_string(index=False)
    # df = pd.DataFrame(file_data)
    # df_5_rows = df.head()
    # csv_string = df_5_rows.to_string(index=False)

    prompt = ChatPromptTemplate.from_messages([
        ("system", 
            "You are a data visualization expert. Your task is to create a graph using the Plotly library (not matplotlib). ..."
            "You are a data visualization expert. Your task is to create a graph using libraries like matplotlib or plotly. "
            "You are given a {name_of_file} file. Here are the first 5 rows of the data: {data}. "
            "Based on user instructions, generate the necessary code to create a graph and store it in a variable 'fig'. "
            "Make sure the code contains a 'fig' variable which represents the plot you generate."),
        MessagesPlaceholder(variable_name="messages"),
    ])

    # Chain the prompt and model
    chain = prompt | model
    response = chain.invoke({
        "messages": [HumanMessage(content=user_input)],
        "data": csv_string,
        "name_of_file": file_name
    })

    result_output = response.content
    print(result_output)

    # Search for the Python code block in the response
    code_block_match = re.search(r"```(?:python)?\n(.*?)```", result_output, re.DOTALL)
    print(code_block_match)

    if code_block_match:
        # Extract and clean the code
        code_block = code_block_match.group(1).strip()
        cleaned_code = re.sub(r"(?m)^\s*fig\.show\(\)\s*$", "", code_block)  # Fix: remove unnecessary show() call
        fig = get_fig_from_code(cleaned_code)
        return dcc.Graph(figure = fig),result_output
    else:
        return "", result_output

if __name__ == "__main__":
    app.run(debug=False, port=8008) 