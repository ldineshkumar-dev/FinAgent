def handle_fallback(state):
    """Provides a polite, canned response for non-SQL queries."""
    print("---HANDLING FALLBACK---")
    
    fallback_message = "I can only answer questions related to the financial database. Please ask a question about accounts, revenue, transactions, etc."
    
    return {"answer": fallback_message}
