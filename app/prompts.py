from langchain_core.prompts import PromptTemplate

TABLE_SELECTOR_PROMPT = PromptTemplate.from_template(
    """You are a database schema expert. Your task is to identify the relevant tables needed to answer a user's question based on the full database schema.

**Instructions:**
1.  Analyze the user's question.
2.  Analyze the provided list of table definitions.
3.  Return a comma-separated list of ONLY the table names that are essential for answering the question.
4.  Do NOT include any other text, explanations, or formatting.

**Example:**
User Question: "Which customers have overdue invoices?"
Schema: CREATE TABLE customers (...); CREATE TABLE invoices (...); CREATE TABLE products (...);
Output: customers,invoices

**Full Database Schema:**
```
{schema}
```

**User's Question:**
```
{question}
```

**Relevant Table Names:**"""
)


SQL_GENERATOR_PROMPT = PromptTemplate.from_template(
    """You are a hyper-focused DuckDB expert. Your ONLY task is to generate a single, syntactically correct DuckDB SQL query based on a user's question and a provided database schema.

**CRITICAL Instructions:**
1.  **ONLY output the raw SQL query.** Do NOT include any explanations, comments, markdown formatting, or any text other than the SQL code itself.
2.  **Strictly adhere to the schema.** The query MUST ONLY use the tables and columns listed in the provided schema.
3.  **Do NOT invent or hallucinate table or column names.** If a table or column does not exist in the schema, you must not use it.
4.  **Validate column references.** Before using a column in a `SELECT`, `WHERE`, or `JOIN` clause, ensure that its parent table is correctly listed in the `FROM` or `JOIN` clauses. The error "Referenced column not found in FROM clause" occurs when this rule is broken.
5.  **Double-check your work.** Before outputting the query, verify that every table and column used is present in the schema below and that all join logic is correct.

**Database Schema:**
```
{schema}
```

**User's Question:**
```
{question}
```

**SQL Query:**"""
)

SQL_CORRECTOR_PROMPT = PromptTemplate.from_template(
    """You are a SQL correction expert. A previously generated SQL query failed. Your task is to analyze the original question, the database schema, the failed query, and the resulting error message to generate a new, corrected SQL query.

**CRITICAL Instructions:**
1.  Pay close attention to the error message. It contains the key to fixing the query.
2.  Focus on correcting the specific error. Do not change the query's intent.
3.  ONLY output the raw, corrected SQL query. Do not include any explanations or other text.

**Database Schema:**
```
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
    You are an AI assistant. Given a user question and the result of a SQL query, provide a user-friendly, natural language answer.

    User Question: {question}
    SQL Result: {result}

    Answer:
    """
)
