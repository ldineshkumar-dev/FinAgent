# 🚀 MFT Finance AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status"/>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python version"/>
  <img src="https://img.shields.io/badge/local--first-100%25-orange" alt="Local First"/>
  <img src="https://img.shields.io/badge/privacy-enhanced-blue" alt="Privacy Enhanced"/>
</p>

<p align="center">
  <strong>Ask questions in plain English. Get SQL answers.</strong>
  <br />
  An intelligent, offline-first AI assistant that translates natural language into accurate SQL queries, enabling you to interact with your database effortlessly.
</p>

---

## ✨ Core Features

*   💬 **Natural Language to SQL**: Interact with your database using everyday language.
*   🧠 **Smart Schema Analysis**: Automatically understands your database structure, including complex table relationships.
*   🌐 **100% Offline**: Your data never leaves your machine. No API calls, no external dependencies.
*   ⚡ **Lightning Fast**: Get near-instant query results powered by a local vector search.
*   🔒 **Privacy by Design**: Ensures complete data confidentiality.
*   💸 **Cost-Effective**: No API fees or expensive cloud compute.

---


### Workflow Explained Step-by-Step

#### Phase 1: One-Time Analysis
This happens only once when you run the `--init-embeddings` command.

1.  **Parse Schema**: The system reads your `db_schema.txt` file to learn the structure of your database, including all tables, columns, and their relationships.
2.  **Generate Embeddings**: It then converts the *meaning* of every table and column into numerical representations called "embeddings" or "vectors".
3.  **Store Embeddings**: These vectors are saved locally in a high-speed vector database (ChromaDB), creating a searchable, semantic map of your database.

#### Phase 2: Live Query Processing
This happens every time you ask a question.

4.  **Vectorize Question**: Your plain English question is converted into a vector, just like the schema was.
5.  **Semantic Search**: The system compares your question's vector against the schema vectors to find the most relevant tables and columns for your query. This is incredibly fast and efficient.
6.  **Build Prompt**: A precise, context-rich prompt is constructed using your question and the relevant schema snippets.
7.  **Generate SQL**: The prompt is sent to the local AI model, which, based on the context, generates the appropriate SQL query.
8.  **Execute Query**: The generated SQL is run against your actual database.
9.  **Format Answer**: The results from the database are formatted into a clean, human-readable answer and presented to you.

---

## 🖥️ User Interface

The application includes a simple and intuitive web interface built with **Streamlit**.

*   **Interactive Chat**: Ask your questions in a clean, chat-like window.
*   **Instant Results**: View the formatted answer directly in the UI.
*   **SQL Transparency**: See the exact SQL query that was generated and executed for your question.
*   **Easy to Use**: No complex setup required. Just run the command, and the interface opens in your browser.

---

## 💡 Sample Questions

Here are a few examples of questions you can ask the assistant:

*   "List all the financial years available."
*   "For each group, list its parent group (if any)."
*   "What is the sort order of each account group?"

---

## 🛠️ Technology Stack

| Component           | Technology                                       | Purpose                               |
| ------------------- | ------------------------------------------------ | ------------------------------------- |
| **AI Model**        |     `distilbert-base-uncased`             | Natural Language to SQL Generation    |
| **Embeddings**      | `sentence-transformers/all-MiniLM-L6-v2`         | Semantic Representation of Schema     |
| **Vector Database** | `ChromaDB`                                       | Fast Similarity Search                |
| **Database**        | `DuckDB`                                         | Analytical Query Engine               |
| **Backend**         | `Python`                                         | Core Application Logic                |
| **Frontend**        | `Streamlit`                                      | Interactive User Interface            |

---

## 🚀 Quick Start

Follow these steps to get the application running.

### 1. Prerequisites

*   **Python**: Ensure you have Python `3.9` or newer installed.

### 2. Install Dependencies

Open your terminal in the project root and run:

```bash
pip install -r requirements.txt
```

### 3. Initialize the System (One-Time Setup)

Before the first run, you must initialize the system to analyze your database schema and create the necessary embeddings.

```bash
python main.py --init-embeddings
```

This process will:
1.  Parse your database schema.
2.  Download the required AI models.
3.  Generate and store embeddings locally.

### 4. Run the Application

Start the interactive Streamlit interface:

```bash
streamlit run ui.py
```

Your web browser will open with the application, ready for you to ask questions!

---

## 📁 Project Structure

```
MFT_Finance/
├── README.md
├── requirements.txt
├── main.py                    # Application entry point
├── ui.py                      # Streamlit interface
├── data/
│   └── finance_module.duckdb  # Financial database
│   └── db_schema.txt          # Database schema definition
├── src/
│   ├── advanced_sql_generator.py # Advanced prompt engineering
│   ├── embedding_service.py   # Embedding generation
│   ├── schema_parser.py       # Database schema extraction
│   ├── vector_store.py        # Vector similarity search
│   ├── query_executor.py      # SQL execution & formatting
│   └── config.py              # Configuration settings
└── embeddings/                # Local vector storage
```

---

## 🔧 Configuration

You can customize the models and vector search settings in `src/config.py`.

```python
# Model settings
SLM_MODEL = "distilbert-base-uncased"  # Much smaller fallback model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Vector search settings
SIMILARITY_THRESHOLD = 0.7
MAX_RELEVANT_TABLES = 5
```

## 🔮 Future Enhancements

-    Multi-database support
-    Query result caching
-    Natural language explanations for results
-    User-specific query history and learning

## 📝 License

This project is licensed under the MIT License.

---