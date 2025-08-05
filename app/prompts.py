from langchain_core.prompts import PromptTemplate

# --- INTENT AND FALLBACK ---

INTENT_PARSER_PROMPT = PromptTemplate.from_template(
    """You are an expert at classifying user intent. Your task is to determine if a user's question can be answered by the provided database schema.

**Instructions:**
1.  Analyze the user's question.
2.  Examine the database schema to see if the entities mentioned in the question (e.g., "accounts," "revenue," "groups") exist in the schema.
3.  Classify the intent into one of two categories:
    *   `sql_query`: The user is asking a question that CAN be answered by querying the database.
    *   `non_sql_query`: The user is asking a question that is off-topic or cannot be answered by the database schema.
4.  Return ONLY the category name (`sql_query` or `non_sql_query`).

**Database Schema:**
```sql
{schema}
```

**User's Question:**
```
{question}
```

**Intent:**"""
)

# --- CORE SQL AND SCHEMA ---

TABLE_SELECTOR_PROMPT = PromptTemplate.from_template(
    """You are an expert at analyzing database schemas. Your task is to identify the necessary tables to answer a user's question.
    
**Instructions:**
1.  Carefully read the user's question.
2.  Examine the provided database schema, paying close attention to the `FOREIGN KEY` relationships.
3.  Return a comma-separated list of ONLY the table names essential for answering the question.
    
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

SQL_CORRECTOR_PROMPT = PromptTemplate.from_template(
    """You are a SQL debugger. A previously generated query failed. Your task is to analyze the original question, the detailed schema, the failed query, and the error message to generate a corrected SQL query.
    
**CRITICAL Instructions:**
1.  Analyze the error message—it is the most important clue.
2.  Use the `FOREIGN KEY` relationships in the schema to fix incorrect `JOIN` conditions.
3.  Output ONLY the corrected, raw SQL query.

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
    """You are a friendly AI financial assistant. Your task is to provide a clear, concise, and user-friendly answer based on a user's question and the result of a database query.
    
**User Question:**
{question}

**Data from Database:**
```
{result}
```

**Answer:**"""
)


# --- SPECIALIZED SQL GENERATOR PROMPTS ---

BASE_SQL_PROMPT_TEMPLATE = """
You are a hyper-focused DuckDB SQL query writer. Your task is to generate a single, syntactically correct DuckDB SQL query.

**Context:**
*   **User's Goal:** The user wants to ask a question about their financial database.
*   **Database Schema:** You have been provided with a detailed schema, including foreign key relationships.

**CRITICAL Instructions:**
1.  **Adhere Strictly to the Schema:** The query MUST ONLY use the tables and columns explicitly defined in the schema.
2.  **Use Foreign Keys for Joins:** Use the `FOREIGN KEY` constraints in the schema to construct all `JOIN` clauses accurately.
3.  **Output ONLY the SQL Query:** Do not include any explanations, comments, markdown, or any text other than the raw SQL code.

**{specialized_instructions}**

**Database Schema:**
```sql
{schema}
```

**User's Question:**
```
{question}
```

**SQL Query:**"""

DEFAULT_SQL_PROMPT = PromptTemplate.from_template(
    BASE_SQL_PROMPT_TEMPLATE,
    partial_variables={"specialized_instructions": "You have been selected as the default query generator. Analyze the user's question and generate the most appropriate query."}
)