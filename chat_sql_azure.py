from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import streamlit as st
import os

def init_database() -> SQLDatabase:
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve database credentials from environment variables
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    driver = os.getenv("DB_DRIVER")

    # Construct the database URI
    db_uri = f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?driver={driver}"
    return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
    template = """
      You are a skilled data analyst at a company. You are interacting with a user who is asking you questions about the company's database. 
      Your role is to understand the user's intent and provide an accurate SQL query to retrieve the desired information from the database.

      Based on the table schema provided below, write a SQL query that answers the user's question. Use the conversation history to understand the context of the question and ensure the query is tailored to the user's needs.

      <SHEMA>{schema}</SCHEMA>

      Conversation History: {chat_history}

      Instructions:
      1. Write a valid SQL query that answers the user's question. 
      2. Use multiple fields and calculated fields where appropriate.
      3. If the query requires information from multiple tables, join them using primary key and foreign key relationships.
      4. Ensure the query is optimized and includes conditions (e.g., WHERE, HAVING) to filter data as required by the user's question.
      5. Follow these SQL Server syntax guidelines:
        - Do not use backticks (`) for identifiers. Use square brackets `[]` only when necessary (e.g., when identifiers contain spaces or reserved keywords).
        - Avoid using LIMIT; instead, use the `TOP` keyword with `ORDER BY` for limiting results.
        - Use fully qualified table and column names where appropriate (e.g., TableName.ColumnName).
        - Use `IS NULL` or `IS NOT NULL` instead of `= NULL` or `!= NULL`.
      6. Support a wide range of question types, including but not limited to:
        - Basic SELECT queries.
        - Aggregations and groupings.
        - Sorting and limiting results.
        - Filtering data based on specific conditions.
        - Complex joins across multiple tables.
        - Calculations (e.g., totals, averages, percentages).
        - Subqueries and nested queries where necessary.
        - Data type checks, NULL handling, and CASE expressions.
      7. Do not wrap the SQL query in any formatting, code fences, or backticks. Return only the SQL query.

      ### Example Questions and Queries:

      1. **Basic Query**:
        - Question: What is the email address of the employee named "Jane Smith"?
          SQL Query: SELECT Email FROM Employee WHERE FirstName = 'Jane' AND LastName = 'Smith';

      2. **Join Query**:
        - Question: What country is John Doe from?
          SQL Query: SELECT Country.CountryName FROM Employee JOIN Country ON Employee.CountryID = Country.CountryID WHERE Employee.FirstName = 'John' AND Employee.LastName = 'Doe';

      3. **Aggregation and Grouping**:
        - Question: What is the average salary by department?
          SQL Query: SELECT DepartmentID, AVG(Salary) AS AverageSalary FROM Employee GROUP BY DepartmentID;

      4. **Sorting and Limiting**:
        - Question: Who are the top 5 highest-paid employees?
          SQL Query: SELECT TOP 5 FirstName, LastName, Salary FROM Employee ORDER BY Salary DESC;

      5. **Filtering Data**:
        - Question: Which employees were hired after 2020?
          SQL Query: SELECT FirstName, LastName, HireDate FROM Employee WHERE HireDate > '2020-12-31';

      6. **Complex Join**:
        - Question: List all employees along with their department names and country names.
          SQL Query: SELECT Employee.FirstName, Employee.LastName, Department.DepartmentName, Country.CountryName FROM Employee JOIN Department ON Employee.DepartmentID = Department.DepartmentID JOIN Country ON Employee.CountryID = Country.CountryID;

      7. **Conditional Logic (CASE)**:
        - Question: Categorize employees into "High", "Medium", or "Low" salary bands.
          SQL Query: SELECT FirstName, LastName, Salary, CASE WHEN Salary > 100000 THEN 'High' WHEN Salary BETWEEN 50000 AND 100000 THEN 'Medium' ELSE 'Low' END AS SalaryBand FROM Employee;

      8. **Subquery**:
        - Question: Which employees earn more than the average salary?
          SQL Query: SELECT FirstName, LastName, Salary FROM Employee WHERE Salary > (SELECT AVG(Salary) FROM Employee);

      9. **NULL Handling**:
        - Question: Find all employees whose phone number is not provided.
          SQL Query: SELECT FirstName, LastName FROM Employee WHERE Phone IS NULL;

      10. **Multi-table Query with Calculations**:
          - Question: What is the total salary expense for each country?
            SQL Query: SELECT Country.CountryName, SUM(Employee.Salary) AS TotalSalaryExpense FROM Employee JOIN Country ON Employee.CountryID = Country.CountryID GROUP BY Country.CountryName;

      11. **Date Filtering**:
          - Question: Find all employees hired in the last 6 months.
            SQL Query: SELECT FirstName, LastName, HireDate FROM Employee WHERE HireDate >= DATEADD(MONTH, -6, GETDATE());

      12. **Distinct Values**:
          - Question: What are the unique job titles in the company?
            SQL Query: SELECT DISTINCT JobTitle FROM Employee;

      13. **Count and Aggregation**:
          - Question: How many employees work in each department?
            SQL Query: SELECT DepartmentID, COUNT(*) AS EmployeeCount FROM Employee GROUP BY DepartmentID;

      14. **Joining with Conditions**:
          - Question: List all employees in the IT department and their country names.
            SQL Query: SELECT Employee.FirstName, Employee.LastName, Country.CountryName FROM Employee JOIN Department ON Employee.DepartmentID = Department.DepartmentID JOIN Country ON Employee.CountryID = Country.CountryID WHERE Department.DepartmentName = 'IT';

      15. **String Matching**:
          - Question: Find all employees whose last name starts with 'S'.
            SQL Query: SELECT FirstName, LastName FROM Employee WHERE LastName LIKE 'S%';

      16. **Data Type Check**:
          - Question: Check if there are any invalid salaries (negative or NULL).
            SQL Query: SELECT EmployeeID, FirstName, LastName, Salary FROM Employee WHERE Salary IS NULL OR Salary < 0;

      ### End of Examples

      Your turn:
      Question: {question}
      SQL Query:

       
      """
      
    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatOpenAI(model="gpt-4o")
    
    def get_schema(_):
        return db.get_table_info()
    
    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
    )
      
def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)
    
    template = """
      You are a skilled data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
      Based on the table schema below, user question, SQL query, and SQL response, write a clear and accurate natural language response to the user. Use the schema, SQL query, and SQL response to provide a well-reasoned explanation.

      <SHEMA>{schema}</SCHEMA>

      Conversation History: {chat_history}

      SQL Query: <SQL>{query}</SQL>
      User question: {question}
      SQL Response: {response}

      ### Instructions:
      1. **Understand Context**: Use the schema and conversation history to understand the user's intent and the SQL query provided.
      2. **Interpret Results**: Analyze the SQL response and interpret the data retrieved. Highlight key insights, patterns, and metrics.
      3. **Provide Meaningful Explanations**: If the query involves calculations, aggregations, or joins, explain these results in simple terms.
      4. **Error Handling**:
        - If the SQL response is empty, explain why (e.g., no matching records, missing relationships, invalid data).
        - If the query is invalid or encounters an error, provide a helpful explanation and suggest a solution.
      5. **Data-Driven Insights**: Provide insights based on the SQL response where appropriate (e.g., trends, anomalies, relationships).
      6. **Clear Communication**: Ensure the explanation is concise, avoids technical jargon, and is easy for a non-technical user to understand.

      ### Example Scenarios:

      #### Example 1: Simple Query
      - **User Question**: What is the email address of John Doe?
      - **SQL Query**: SELECT Email FROM Employee WHERE FirstName = 'John' AND LastName = 'Doe';
      - **SQL Response**: john.doe@example.com
      - **Natural Language Response**: The email address of John Doe is `john.doe@example.com`.

      #### Example 2: Aggregation
      - **User Question**: What is the average salary in the IT department?
      - **SQL Query**: SELECT AVG(Salary) AS AverageSalary FROM Employee WHERE DepartmentID = 1;
      - **SQL Response**: 75000
      - **Natural Language Response**: The average salary in the IT department is $75,000.

      #### Example 3: Join Query
      - **User Question**: Which country is John Doe from?
      - **SQL Query**: SELECT Country.CountryName FROM Employee JOIN Country ON Employee.CountryID = Country.CountryID WHERE Employee.FirstName = 'John' AND Employee.LastName = 'Doe';
      - **SQL Response**: United States
      - **Natural Language Response**: John Doe is from the United States.

      #### Example 4: Empty Response
      - **User Question**: Who are the employees hired in 2015?
      - **SQL Query**: SELECT FirstName, LastName FROM Employee WHERE YEAR(HireDate) = 2015;
      - **SQL Response**: (Empty)
      - **Natural Language Response**: No employees were hired in 2015.

      #### Example 5: Error Handling
      - **User Question**: What is the total revenue by department?
      - **SQL Query**: SELECT DepartmentID, SUM(Salary) FROM Employee GROUP BY DepartmentID;
      - **SQL Response**: (Error - Column 'DepartmentID' is invalid in the select list because it is not contained in either an aggregate function or the GROUP BY clause.)
      - **Natural Language Response**: There is an issue with the SQL query. The `DepartmentID` column must either be aggregated (e.g., SUM, AVG) or included in the `GROUP BY` clause. The corrected query would be: `SELECT DepartmentID, SUM(Salary) FROM Employee GROUP BY DepartmentID`.

      #### Example 6: Complex Join
      - **User Question**: List all employees along with their department and country.
      - **SQL Query**: SELECT Employee.FirstName, Employee.LastName, Department.DepartmentName, Country.CountryName FROM Employee JOIN Department ON Employee.DepartmentID = Department.DepartmentID JOIN Country ON Employee.CountryID = Country.CountryID;
      - **SQL Response**:
        | FirstName | LastName | DepartmentName | CountryName    |
        |-----------|----------|----------------|----------------|
        | John      | Doe      | IT             | United States  |
        | Jane      | Smith    | HR             | United Kingdom |
      - **Natural Language Response**: Here is the list of employees along with their department and country:
        - John Doe works in the IT department and is from the United States.
        - Jane Smith works in the HR department and is from the United Kingdom.

      #### Example 7: Handling NULL Values
      - **User Question**: Which employees do not have a phone number?
      - **SQL Query**: SELECT FirstName, LastName FROM Employee WHERE Phone IS NULL;
      - **SQL Response**:
        | FirstName | LastName   |
        |-----------|------------|
        | Emily     | Davis      |
        | Chris     | Taylor     |
      - **Natural Language Response**: The following employees do not have a phone number:
        - Emily Davis
        - Chris Taylor

      ### Your turn:
      User Question: {question}
      SQL Query: <SQL>{query}</SQL>
      SQL Response: {response}
      Natural Language Response:
"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatOpenAI(model="gpt-4o")
    
    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
            schema=lambda _: db.get_table_info(),
            response=lambda vars: db.run(vars["query"]),
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })
      
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
      AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
    ]

st.set_page_config(page_title="Chat with Azure SQL Server", page_icon=":speech_balloon:")

st.title("Chat with Azure SQL Server")

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type a message...")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        db = init_database()
        response = get_response(user_query, db, st.session_state.chat_history)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))
