# Chat with SQL Databases

This project demonstrates a chatbot application for interacting with SQL databases, built using **Streamlit**, **LangChain**, and **OpenAI's GPT models**. The bot generates SQL queries based on user questions, executes them on the database, and returns human-readable responses.

## Features

- **Dynamic SQL Query Generation**: Automatically create SQL queries based on natural language input.
- **Database Compatibility**: 
  - `chat_db.py`: For MySQL databases.
  - `chat_sql_azure.py`: For Azure SQL Server.
- **Interactive Chat Interface**: Built with Streamlit for an engaging user experience.
- **Error Handling and Explanations**: Provides clear feedback on query execution and results.
- **Extensive Query Support**: Supports basic SELECT queries, joins, aggregations, filtering, and more.

## Requirements

- Python 3.8 or higher
- Streamlit
- LangChain Core
- OpenAI API
- Database-specific drivers:
  - `mysql-connector-python` for MySQL
  - `pyodbc` for Azure SQL Server

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo-name/chat-with-sql.git
cd chat-with-sql
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

#### For MySQL
Create a `.env` file in the root directory with the following content:
```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database
```

#### For Azure SQL Server
Create a `.env` file in the root directory with the following content:
```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=your_port
DB_NAME=your_database
DB_DRIVER=ODBC+Driver+17+for+SQL+Server
```

### 4. Run the Application

#### For MySQL
```bash
streamlit run chat_db.py
```

#### For Azure SQL Server
```bash
streamlit run chat_sql_azure.py
```

## Usage

1. Input database credentials in the sidebar for MySQL or use environment variables for Azure.
2. Type a question about your database in the chat box, such as:
   - *What is the email of the employee named John Doe?*
   - *List the top 5 highest-paid employees.*
3. The chatbot will generate, execute the SQL query, and display the results in natural language.

## Example Queries

- **Basic Query**: What is the email address of Jane Smith?
- **Join Query**: What is the department name of John Doe?
- **Aggregation**: What is the average salary by department?
- **Filtering**: Which employees were hired after 2020?

## Screenshots

![Screenshot of Chatbot](screenshot.png)

## Contribution

Feel free to open issues or submit pull requests to improve the project.

## License

This project is licensed under the MIT License.
