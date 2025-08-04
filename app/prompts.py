from langchain_core.prompts import PromptTemplate

TABLE_SELECTOR_PROMPT = PromptTemplate.from_template(
    """You are an expert at analyzing database schemas. Your task is to identify the necessary tables to answer a user's question.

**Instructions:**
1.  Carefully read the user's question.
2.  Examine the provided database schema, paying close attention to the `CREATE TABLE` statements, column names, and especially the `FOREIGN KEY` relationships which define how tables are linked.
3.  Return a comma-separated list of ONLY the table names that are absolutely essential for answering the question. Include tables needed for joins.
4.  Do NOT include views unless they are directly mentioned or clearly relevant.
5.  Do NOT output any text other than the comma-separated list of table names.

**Example:**
User Question: "What is the name of the department with the highest total sales?"
Schema: 
CREATE TABLE sales (id INT, department_id INT, amount DECIMAL, FOREIGN KEY (department_id) REFERENCES departments(id));
CREATE TABLE departments (id INT, name VARCHAR);
Output: sales,departments

**Full Database Schema:**
```sql
{schema}
```

**User's Question:**
```
{question}
```

**Relevant Table Names:**"""
)


SQL_GENERATOR_PROMPT = PromptTemplate.from_template(
    """You are a hyper-focused DuckDB SQL query writer. Your ONLY task is to generate a single, syntactically correct DuckDB SQL query based on a user's question and a detailed database schema.

**CRITICAL Instructions:**
1.  **Use the Schema for Joins:** The provided schema includes `FOREIGN KEY` constraints. Use these relationships to construct all `JOIN` clauses accurately. For example, if `table_a.col_x` references `table_b.col_y`, the join should be `ON table_a.col_x = table_b.col_y`.
2.  **Adhere Strictly to the Schema:** The query MUST ONLY use the tables and columns explicitly defined in the schema. Do not invent or assume any table or column names.
3.  **Validate Column References:** Ensure every column in a `SELECT`, `WHERE`, or `JOIN` clause belongs to a table listed in the `FROM` or `JOIN` clauses.
4.  **Output ONLY the SQL Query:** Do not include any explanations, comments, markdown formatting, or any text other than the raw SQL code.

**Database Schema:**
```sql
{schema}
```

**User's Question:**
```
{question}
```

**SQL Query:**"""
)

SQL_CORRECTOR_PROMPT = PromptTemplate.from_template(
    """You are a SQL debugger. A previously generated query failed. Your task is to analyze the original question, the detailed schema, the failed query, and the error message to generate a corrected SQL query.

**CRITICAL Instructions:**
1.  **Analyze the Error:** The error message is the most important clue. Identify the root cause, such as a missing join, incorrect column name, or invalid syntax.
2.  **Consult the Schema:** Use the `FOREIGN KEY` relationships in the schema to fix incorrect `JOIN` conditions. Verify all table and column names against the schema.
3.  **Correct the Logic:** Fix the specific error without changing the original intent of the query.
4.  **Output ONLY the Corrected SQL:** Do not include any explanations or other text.

**Database Schema:**
```sql
{schema}
```

**Original User Question:**
```
{question}
```

**The FAILED SQL Query:**
```sql
{sql_query}
```

**The Error Message:**
```
{error}
```

**Corrected SQL Query:**"""
)

ANSWER_FORMATTER_PROMPT = PromptTemplate.from_template(
    """
    You are a friendly AI financial assistant. Your task is to provide a clear, concise, and user-friendly answer based on a user's question and the result of a database query.

**Instructions:**
1.  If the result is a single value or a short list, present it in a natural language sentence.
2.  If the result is a table, summarize the key findings. Do not just repeat the data.
3.  If the result is empty, state that no data was found for the user's request.
4.  Keep the tone professional but approachable.

**User Question:**
{question}

**Data from Database:**
```
{result}
```

**Answer:**
"""
)