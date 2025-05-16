<h1 align = "center">Agentic AI for auto generate graphs</h1>

This application uses Groq AI to generate graph based on client's prompt. The application is able to take both dataframe and database and generate visualizations. <br> 

<h2>Features</h2>
<ul>
<li>Upload CSV or XML data</li>
<li>Connect to local MySQL</li>
<li>LLM generate charts and Plotly code</li>
</ul>

![Screenshot 2025-05-16 142221](https://github.com/user-attachments/assets/03a274b5-1ee4-4043-8791-88dbe28a4b1e)


<h2>Example Use case</h2>
<b>Prompt</b>: "Create a bar gaph showing top movies with highest revenue"

<h2>Setup</h2>
<h2>1. Clone repo</h2>

```bash
git clone https://github.com/Sujal-Rajbhandari/agentic-ai-graph.git
cd agentic-ai-graph
```

<h2>2. Add Environment Variables</h2>
Make sure to create .env file and add your groq api key.

```bash
GROQ_API_KEY = your_groq_api_key_here
```

<h2>3. Steps fot getting you API key</h2>
<ul>
  <li>Go to https://console.groq.com/keys</li>
  <li>Sign up or log in.</li>
  <li>Click "Create API Key"</li>
  <li>Copy the generated key.</li>
</ul>
<h2>4. Setup up local databse for Mysql</h2>
Make sure to replace your username, password, localhost and databasename

```bash
engine = create_engine("mysql+mysqlconnector://username:password@localhost:3306/database")
```
<h2>4. Run the application</h2>

```bash
python app.py #replace app.py with your main file
```
