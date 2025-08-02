# 🤖 MFT Finance AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/status-active-green" alt="Status"/>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python version"/>
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"/>
</p>

An intelligent, conversational AI agent that allows you to ask questions about your financial database in plain English. No more writing complex SQL queries—just ask, and the AI delivers.

---

## ✨ Core Features

*   **Natural Language Queries:** Ask complex questions like *"What was the total revenue last quarter?"* or *"Show me all transactions for the 'marketing' department"* and get instant answers.
*   **AI-Powered Agentic Workflow:** A sophisticated multi-agent system works behind the scenes to understand your intent, generate the correct database query, and format the answer.
*   **Sleek Dark-Mode UI:** Interact with the AI through a beautiful and intuitive chat interface built with Streamlit.
*   **Efficient & Scalable:** The system intelligently selects only the necessary parts of your database schema to analyze, ensuring it can handle even very large databases without hitting API limits.

---

## ⚙️ How It Works: The AI Assembly Line

Think of your question going through a smart assembly line. Each station is a specialized AI agent with a single, crucial job.

1.  **🕵️‍♂️ The Table Selector**
    *   **Job:** Examines your question and the entire database blueprint.
    *   **Action:** Intelligently picks out *only* the specific tables needed to answer your question, ignoring everything else. This makes the whole process incredibly efficient.

2.  **✍️ The SQL Generator**
    *   **Job:** Receives the small, relevant list of tables from the selector.
    *   **Action:** Acts as an expert database programmer, writing the perfect, syntactically correct SQL query to fetch the information you requested.

3.  **🏃 The Executor**
    *   **Job:** The "doer" of the group.
    *   **Action:** Takes the SQL query, runs it directly on the database file, and retrieves the raw data.

4.  **🎨 The Answer Formatter**
    *   **Job:** The friendly communicator.
    *   **Action:** Takes the raw, technical data from the executor and translates it into a clean, user-friendly, and natural language response.

This entire process is orchestrated seamlessly by **LangGraph**, ensuring a smooth flow from your question to your answer.

---

## 🛠️ Technology Stack

*   **Backend:** Python
*   **AI Orchestration:** LangGraph
*   **LLM Provider:** Groq (for high-speed inference with open-source models like Llama 3)
*   **Database:** DuckDB
*   **Frontend:** Streamlit

---

## 🖼️ Screenshot

*(You can add a screenshot of the dark-mode UI here to showcase the final product!)*

![App Screenshot](placeholder.png)

