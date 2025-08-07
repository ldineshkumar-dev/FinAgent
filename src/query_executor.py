"""
Query Executor
Handles SQL execution and result formatting for the finance database.
"""
import logging
import duckdb
import pandas as pd
from typing import Any, Dict, Optional, Tuple, Union
import time
from pathlib import Path

from config import DB_PATH, QueryConfig

logger = logging.getLogger(__name__)

class QueryExecutor:
    """Executes SQL queries and formats results"""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or DB_PATH
        self._validate_database()
    
    def _validate_database(self):
        """Validate that the database exists and is accessible"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        
        try:
            # Test connection
            with duckdb.connect(str(self.db_path), read_only=True) as conn:
                conn.execute("SELECT 1").fetchall()
            logger.info(f"✅ Database connection validated: {self.db_path}")
        except Exception as e:
            logger.error(f"Database validation failed: {e}")
            raise
    
    def execute_query(self, sql_query: str) -> Tuple[bool, Union[pd.DataFrame, str]]:
        """
        Execute SQL query and return results
        
        Returns:
            Tuple of (success: bool, result: DataFrame or error_message: str)
        """
        try:
            start_time = time.time()
            
            # Clean and validate SQL
            sql_query = self._clean_sql_query(sql_query)
            
            # Execute query with timeout
            with duckdb.connect(str(self.db_path), read_only=True) as conn:
                # Set query timeout if supported
                try:
                    conn.execute(f"SET statement_timeout = '{QueryConfig.TIMEOUT_SECONDS}s'")
                except:
                    pass  # Timeout setting might not be supported in all versions
                
                # Execute query
                result_df = conn.execute(sql_query).fetchdf()
            
            execution_time = time.time() - start_time
            
            # Limit result size
            if len(result_df) > QueryConfig.MAX_RESULT_ROWS:
                logger.warning(f"Query returned {len(result_df)} rows, limiting to {QueryConfig.MAX_RESULT_ROWS}")
                result_df = result_df.head(QueryConfig.MAX_RESULT_ROWS)
            
            logger.info(f"Query executed successfully in {execution_time:.2f}s, returned {len(result_df)} rows")
            return True, result_df
        
        except Exception as e:
            error_msg = f"SQL execution error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """Clean and validate SQL query"""
        # Remove extra whitespace
        sql_query = ' '.join(sql_query.split())
        
        # Remove potential SQL injection patterns (basic protection)
        dangerous_patterns = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 
            'TRUNCATE', 'EXEC', 'EXECUTE', '--', '/*', '*/'
        ]
        
        sql_upper = sql_query.upper()
        for pattern in dangerous_patterns:
            if pattern in sql_upper and not self._is_safe_context(sql_upper, pattern):
                raise ValueError(f"Potentially dangerous SQL pattern detected: {pattern}")
        
        # Ensure it's a SELECT query (for safety)
        if not sql_upper.strip().startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")
        
        # Length check
        if len(sql_query) > QueryConfig.MAX_SQL_LENGTH:
            raise ValueError(f"SQL query too long (max {QueryConfig.MAX_SQL_LENGTH} characters)")
        
        return sql_query
    
    def _is_safe_context(self, sql_upper: str, pattern: str) -> bool:
        """Check if a potentially dangerous pattern is in a safe context"""
        # This is a simple check - in production, use a proper SQL parser
        safe_contexts = {
            'CREATE': ['CREATE TABLE', 'CREATE VIEW'],  # Only in schema definitions
            'DROP': False,  # Never safe in our context
            'DELETE': False,  # Never safe in our context
            'INSERT': False,  # Never safe in our context
            'UPDATE': False,  # Never safe in our context
        }
        
        if pattern in safe_contexts:
            if safe_contexts[pattern] is False:
                return False
            elif isinstance(safe_contexts[pattern], list):
                return any(safe_pattern in sql_upper for safe_pattern in safe_contexts[pattern])
        
        return True
    
    def format_results(self, result_df: pd.DataFrame, user_query: str) -> str:
        """Format query results for display"""
        try:
            if result_df.empty:
                return "No data found for your query."
            
            # Determine formatting based on result size and type
            num_rows, num_cols = result_df.shape
            
            if num_rows == 1 and num_cols == 1:
                # Single value result
                value = result_df.iloc[0, 0]
                return self._format_single_value(value, user_query)
            
            elif num_rows <= 10 and num_cols <= 5:
                # Small table - format as natural language
                return self._format_small_table(result_df, user_query)
            
            else:
                # Large table - return HTML table
                return self._format_large_table(result_df, user_query)
        
        except Exception as e:
            logger.error(f"Error formatting results: {e}")
            return f"Results found but formatting failed: {str(e)}"
    
    def _format_single_value(self, value: Any, user_query: str) -> str:
        """Format single value results"""
        # Determine the type of query for context
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['count', 'how many', 'number of']):
            return f"The count is **{value:,}**."
        
        elif any(word in query_lower for word in ['average', 'avg', 'mean']):
            if isinstance(value, (int, float)):
                return f"The average is **{value:,.2f}**."
            else:
                return f"The average is **{value}**."
        
        elif any(word in query_lower for word in ['sum', 'total']):
            if isinstance(value, (int, float)):
                return f"The total is **{value:,.2f}**."
            else:
                return f"The total is **{value}**."
        
        elif any(word in query_lower for word in ['max', 'maximum', 'highest']):
            return f"The maximum value is **{value}**."
        
        elif any(word in query_lower for word in ['min', 'minimum', 'lowest']):
            return f"The minimum value is **{value}**."
        
        else:
            return f"The result is **{value}**."
    
    def _format_small_table(self, result_df: pd.DataFrame, user_query: str) -> str:
        """Format small tables with enhanced container"""
        num_rows = len(result_df)
        num_cols = len(result_df.columns)
        
        if num_rows == 1:
            # Single row - list the values with enhanced styling
            row = result_df.iloc[0]
            items = []
            for col, val in row.items():
                if pd.notna(val):
                    items.append(f"**{col}**: `{val}`")
            
            return f'<div class="table-info">📄 1 record found</div>\n' + "\n".join(items)
        
        else:
            # Multiple rows - create enhanced table
            summary = f'<div class="table-info">📊 {num_rows} records found • {num_cols} columns</div>'
            
            table_html = result_df.to_html(
                index=False, 
                classes='result-table', 
                border=0,
                escape=False
            )
            
            # Use container even for small tables for consistency
            scroll_class = "has-scroll" if num_cols > 6 else ""
            
            enhanced_table = f"""
            {summary}
            <div class="table-container {scroll_class}">
                {table_html}
                <div class="column-indicator">{num_cols} columns</div>
            </div>
            """
            
            return enhanced_table
    
    def _format_large_table(self, result_df: pd.DataFrame, user_query: str) -> str:
        """Format large tables as HTML with enhanced scrollable container"""
        num_rows = len(result_df)
        num_cols = len(result_df.columns)
        display_rows = min(num_rows, 50)  # Show first 50 rows
        
        # Create enhanced summary with table info
        summary = f'<div class="table-info">📊 {num_rows:,} records found • {num_cols} columns</div>'
        if display_rows < num_rows:
            summary += f'<div style="color: #a0a0a0; font-size: 0.9rem; margin-bottom: 1rem;">Showing first {display_rows} rows</div>'
        
        # Create HTML table with enhanced container
        display_df = result_df.head(display_rows)
        table_html = display_df.to_html(
            index=False, 
            classes='result-table', 
            border=0,
            table_id='query-results',
            escape=False
        )
        
        # Determine if horizontal scroll is needed
        scroll_class = "has-scroll" if num_cols > 6 else ""
        
        # Wrap in enhanced container with scroll indicators
        enhanced_table = f"""
        {summary}
        <div class="table-container {scroll_class}">
            {table_html}
            <div class="column-indicator">{num_cols} columns</div>
        </div>
        <div style="font-size: 0.8rem; color: #a0a0a0; margin-top: 0.5rem;">
            💡 Tip: Hover over cells to see full content • Scroll horizontally for more columns
        </div>
        """
        
        return enhanced_table
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database"""
        try:
            with duckdb.connect(str(self.db_path), read_only=True) as conn:
                # Get table count
                tables_result = conn.execute("""
                    SELECT COUNT(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = 'main'
                """).fetchone()
                
                table_count = tables_result[0] if tables_result else 0
                
                # Get database size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                return {
                    'database_path': str(self.db_path),
                    'database_size_mb': db_size / (1024 * 1024),
                    'table_count': table_count,
                    'max_result_rows': QueryConfig.MAX_RESULT_ROWS,
                    'query_timeout_seconds': QueryConfig.TIMEOUT_SECONDS
                }
        
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {'error': str(e)}
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with duckdb.connect(str(self.db_path), read_only=True) as conn:
                conn.execute("SELECT 1").fetchone()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data from a table"""
        try:
            sql = f"SELECT * FROM {table_name} LIMIT {limit}"
            success, result = self.execute_query(sql)
            
            if success:
                return result
            else:
                logger.error(f"Failed to get sample data: {result}")
                return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Error getting sample data: {e}")
            return pd.DataFrame()

class ResultCache:
    """Simple cache for query results"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get(self, query_hash: str) -> Optional[pd.DataFrame]:
        """Get cached result"""
        if query_hash in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(query_hash)
            self.access_order.append(query_hash)
            return self.cache[query_hash].copy()
        return None
    
    def set(self, query_hash: str, result: pd.DataFrame):
        """Cache result"""
        # Remove oldest if cache is full
        if len(self.cache) >= self.max_size:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[query_hash] = result.copy()
        self.access_order.append(query_hash)
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_order.clear()

if __name__ == "__main__":
    # Test the query executor
    logging.basicConfig(level=logging.INFO)
    
    try:
        executor = QueryExecutor()
        
        # Test connection
        if executor.test_connection():
            print("✅ Database connection successful")
            
            # Get database info
            db_info = executor.get_database_info()
            print(f"Database info: {db_info}")
            
            # Test a simple query
            test_sql = "SELECT COUNT(*) as total_tables FROM information_schema.tables WHERE table_schema = 'main'"
            success, result = executor.execute_query(test_sql)
            
            if success:
                formatted_result = executor.format_results(result, "How many tables are in the database?")
                print(f"Test query result: {formatted_result}")
            else:
                print(f"Test query failed: {result}")
        
        else:
            print("❌ Database connection failed")
    
    except Exception as e:
        print(f"Error testing query executor: {e}")
