# 🚀 MFT Finance AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/status-active-brightgreen" alt="Status"/>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python version"/>
  <img src="https://img.shields.io/badge/local-SLM-orange" alt="Local SLM"/>
</p>

An AI assistant that transforms your natural language questions into SQL queries. It runs completely offline, using **semantic similarity search** and a **local Small Language Model (SLM)** to give you fast, accurate, and private results.

## ✨ Core Features

*   **Natural Language to SQL**: Ask questions in plain English and get SQL queries back.
*   **Semantic Table Discovery**: Automatically finds the most relevant tables for your query using vector embeddings.
*   **100% Local**: Runs completely offline. No API calls, no data ever leaves your machine.
*   **Fast & Responsive**: Get near-instant responses thanks to vector similarity search.
*   **Smart Schema Understanding**: Understands your database structure, including table relationships and column meanings.
*   **Cost-Effective**: No API fees or expensive computational overhead.

## 🏗️ How It Works

The system follows a simple yet powerful workflow:

```
User Query → Query Embeddings → Vector Similarity Search → Relevant Tables → Local SLM → SQL Generation → Execution → Results
```

1.  **📊 Database Preprocessing** (One-time setup)
    *   The database schema is parsed to understand its structure.
    *   Semantic embeddings (vector representations) are generated for all tables and columns.
    *   These embeddings are stored in a local vector database for fast lookups.

2.  **🔍 Query Processing** (At runtime)
    *   Your question is converted into an embedding.
    *   The system searches the vector database to find the most semantically similar tables.
    *   The relevant schema information and your question are passed to the local SLM.
    *   The SLM generates the SQL query, which is then executed to fetch the results.

## 🛠️ Technology Stack

*   **Local SLM**: Phi-3-Mini (3.8B parameters) - Optimized for code generation.
*   **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2).
*   **Vector Database**: ChromaDB for fast similarity search.
*   **Database**: DuckDB for analytical queries.
*   **Backend**: Python.
*   **Frontend**: Streamlit for the interactive interface.

## 📁 Project Structure

```
MFT_Finance/
├── README.md
├── requirements.txt
├── main.py                    # Application entry point
├── data/
│   └── finance_module.duckdb  # Financial database
├── src/
│   ├── schema_parser.py       # Database schema extraction
│   ├── embedding_service.py   # Embedding generation
│   ├── vector_store.py        # Vector similarity search
│   ├── sql_generator.py       # Local SLM SQL generation
│   ├── query_executor.py      # SQL execution & formatting
│   └── config.py              # Configuration settings
├── embeddings/                # Vector database storage
└── ui.py                      # Streamlit interface
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ldineshkumar-dev/FinAgent
cd FinAgent

# Install dependencies
pip install -r requirements.txt

# Initialize embeddings (one-time setup)
python main.py --init-embeddings

# Start the application
streamlit run ui.py
```

### First-Time Setup

On the first run, the system will automatically:
1.  Parse your database schema.
2.  Generate and store embeddings for all tables and columns.
3.  Create a local vector database.
4.  Download and cache the local SLM model.

## 💡 Example Usage

**Your Question**: "What is the average interest rate among all accounts?"

**System Process**:
1.  The query is converted to an embedding.
2.  The system identifies `i_acct_account_mst` and `i_acct_interest_config` as the most relevant tables.
3.  The local SLM generates the following SQL:
    ```sql
    SELECT AVG(interest_rate) FROM i_acct_account_mst a JOIN i_acct_interest_config i ON a.id = i.account_id
    ```
4.  The query is executed, and the result is returned in under a second.

## 🔧 Configuration

You can customize the models and settings in `src/config.py`:

```python
# Model settings
SLM_MODEL = "microsoft/Phi-3-mini-4k-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Vector search settings
SIMILARITY_THRESHOLD = 0.7
MAX_RELEVANT_TABLES = 5

# Performance settings
VECTOR_BATCH_SIZE = 100
CACHE_EMBEDDINGS = True
```

## 🎯 Key Advantages

*   **Efficient**: Uses a single, local model call for SQL generation.
*   **Fast**: Combines vector search with local inference for quick results.
*   **Cost-Effective**: Runs locally with no API fees.
*   **Private**: All data and queries are processed on your machine.
*   **Reliable**: Works offline without any network dependencies.
*   **Scalable**: Can be easily extended to support new databases.

## 🔮 Future Enhancements

-    Multi-database support
-    Query result caching
-    Advanced SQL optimization
-    Natural language explanations for results
-    Query history and learning

## 📝 License

This project is licensed under the MIT License.

---

**Built with ❤️ for efficiency and performance.**