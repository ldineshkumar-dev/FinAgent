# 🤖 MFT Finance AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/status-enhanced-brightgreen" alt="Status"/>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python version"/>
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"/>
</p>

An intelligent, conversational AI agent that allows you to ask questions about your financial database in plain English. No more writing complex SQL queries—just ask, and the AI delivers.

---

## ✨ Core Features

*   **Natural Language Queries:** Ask questions like *"What is the average interest rate among all accounts?"* or *"Which account group has the highest number of accounts assigned?
"* and get instant answers.
*   **Advanced, Animated UI:** Interact with the AI through a sleek, modern interface featuring gradient colors, smooth transitions, and a user-friendly layout.
*   **Complex Join Handling:** The AI can now understand detailed database schemas with foreign key relationships, allowing it to accurately answer complex questions that require joining multiple tables.
*   **Robust Error Correction:** The system automatically detects and reflects on SQL query errors. It then enters a retry loop to attempt a corrected query, significantly improving reliability.
*   **Dynamic Response Handling:** Intelligently detects when a query returns a large amount of data. Instead of failing, it displays the results in a clean, scrollable table, preventing token limit errors and ensuring a smooth user experience.
*   **Efficient Agentic Workflow:** A sophisticated multi-agent system works behind the scenes to understand your intent, generate the correct database query, and format the answer.

---

## ⚙️ How It Works: The AI Assembly Line

Think of your question going through a smart assembly line. Each station is a specialized AI agent with a single, crucial job.

1.  **🕵️‍♂️ The Table Selector**
    *   **Job:** Examines your question and a detailed database blueprint that includes table relationships.
    *   **Action:** Intelligently picks out *only* the specific tables needed to answer your question, ensuring complex joins can be resolved.

2.  **✍️ The SQL Generator**
    *   **Job:** Receives the relevant list of tables from the selector.
    *   **Action:** Acts as an expert database programmer, using its understanding of foreign keys to write the perfect SQL query.

3.  **🏃 The Executor & Reflector**
    *   **Job:** The "doer" and "debugger" of the group.
    *   **Action:** It first runs the SQL query. If the query fails, it triggers a **reflection agent** that analyzes the error and generates a corrected query. The system then retries the new query automatically.

4.  **🎨 The Answer Formatter**
    *   **Job:** The friendly communicator and data handler.
    *   **Action:** If the query result is small, it translates the raw data into a clean, natural language response. If the result is large, it bypasses the AI and displays the data directly in a formatted table to prevent token overloads.

This entire process is orchestrated seamlessly by **LangGraph**, ensuring a resilient and smooth flow from your question to your answer.

---

## 🛠️ Technology Stack

*   **Backend:** Python
*   **AI Orchestration:** LangGraph
*   **LLM Provider:** Groq (for high-speed inference with open-source models like Llama 3)
*   **Database:** DuckDB
*   **Frontend:** Streamlit

---

## 🖼️ Screenshot

*A snapshot of the new, redesigned user interface.*

![App Screenshot](./data/UI%20Screenshot.png)

![App Screenshot](./data/UI%20Screenshot%202.png)
