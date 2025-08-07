"""
SQL Generator
Local SLM-based SQL query generation from natural language.
"""
import logging
import torch
from typing import Optional, Dict, Any
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re
import time

from config import ModelConfig, QueryConfig

logger = logging.getLogger(__name__)

class LocalSQLGenerator:
    """Local Small Language Model for SQL generation"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.device = self._get_device()
        self._load_model()
    
    def _get_device(self) -> str:
        """Determine the best device for model inference"""
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"Using GPU: {torch.cuda.get_device_name()}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"  # Apple Silicon
            logger.info("Using Apple Silicon MPS")
        else:
            device = "cpu"
            logger.info("Using CPU")
        
        return device
    
    def _load_model(self):
        """Load the local SLM model"""
        try:
            logger.info(f"Loading SLM model: {ModelConfig.SLM_MODEL}")
            start_time = time.time()
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                ModelConfig.SLM_MODEL,
                trust_remote_code=True
            )
            
            # Load model with optimizations
            self.model = AutoModelForCausalLM.from_pretrained(
                ModelConfig.SLM_MODEL,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Move to device if not using device_map
            if self.device != "cuda":
                self.model = self.model.to(self.device)
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            load_time = time.time() - start_time
            logger.info(f"✅ SLM model loaded successfully in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to load SLM model: {e}")
            raise
    
    def generate_sql(self, user_query: str, relevant_schema: str) -> str:
        """Generate SQL query from natural language using local SLM"""
        try:
            # Create prompt for SQL generation
            prompt = self._create_sql_prompt(user_query, relevant_schema)
            
            # Generate SQL using the model
            start_time = time.time()
            generated_text = self.generator(
                prompt,
                max_new_tokens=ModelConfig.SLM_MAX_TOKENS,
                temperature=ModelConfig.SLM_TEMPERATURE,
                do_sample=True,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                return_full_text=False
            )[0]['generated_text']
            
            generation_time = time.time() - start_time
            
            # Extract and clean SQL
            sql_query = self._extract_sql_from_response(generated_text)
            
            logger.info(f"SQL generated in {generation_time:.2f}s")
            logger.debug(f"Generated SQL: {sql_query}")
            
            return sql_query
        
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise
    
    def _create_sql_prompt(self, user_query: str, schema: str) -> str:
        """Create a well-structured prompt for SQL generation"""
        
        prompt = f"""You are an expert SQL developer. Generate a syntactically correct DuckDB SQL query based on the user's question and the provided database schema.

**CRITICAL INSTRUCTIONS:**
1. Only use tables and columns that exist in the provided schema
2. Follow DuckDB SQL syntax exactly
3. Use proper JOINs based on foreign key relationships shown in the schema
4. Return ONLY the SQL query, no explanations or additional text
5. Ensure the query directly answers the user's question

**Database Schema:**
```sql
{schema}
```

**User Question:** {user_query}

**SQL Query:**
```sql
"""
        
        return prompt
    
    def _extract_sql_from_response(self, response: str) -> str:
        """Extract clean SQL query from model response"""
        try:
            # Look for SQL code blocks first
            sql_block_match = re.search(r'```sql\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
            if sql_block_match:
                sql = sql_block_match.group(1).strip()
            else:
                # Look for SQL code without markdown
                sql_match = re.search(r'(SELECT.*?;)', response, re.DOTALL | re.IGNORECASE)
                if sql_match:
                    sql = sql_match.group(1).strip()
                else:
                    # Take the entire response and clean it
                    sql = response.strip()
            
            # Clean up the SQL
            sql = self._clean_sql(sql)
            
            # Validate basic SQL structure
            if not self._is_valid_sql_structure(sql):
                raise ValueError(f"Generated SQL has invalid structure: {sql}")
            
            return sql
        
        except Exception as e:
            logger.error(f"Error extracting SQL from response: {e}")
            logger.debug(f"Raw response: {response}")
            raise
    
    def _clean_sql(self, sql: str) -> str:
        """Clean and normalize SQL query"""
        # Remove extra whitespaces
        sql = ' '.join(sql.split())
        
        # Remove trailing semicolon if present
        sql = sql.rstrip(';')
        
        # Ensure it starts with SELECT (for now, focusing on SELECT queries)
        if not sql.upper().strip().startswith('SELECT'):
            # Try to find SELECT in the string
            select_match = re.search(r'(SELECT.*)', sql, re.IGNORECASE)
            if select_match:
                sql = select_match.group(1)
        
        return sql.strip()
    
    def _is_valid_sql_structure(self, sql: str) -> bool:
        """Basic validation of SQL structure"""
        sql_upper = sql.upper().strip()
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return False
        
        # Must contain FROM
        if 'FROM' not in sql_upper:
            return False
        
        # Check for balanced parentheses
        if sql.count('(') != sql.count(')'):
            return False
        
        # Check for some common SQL keywords structure
        basic_keywords = ['SELECT', 'FROM']
        for keyword in basic_keywords:
            if keyword not in sql_upper:
                return False
        
        return True
    
    def validate_sql_syntax(self, sql: str, schema: str) -> tuple[bool, str]:
        """Validate SQL syntax against schema (basic validation)"""
        try:
            # Extract table names from schema
            schema_tables = self._extract_table_names_from_schema(schema)
            
            # Extract table names from SQL
            sql_tables = self._extract_table_names_from_sql(sql)
            
            # Check if all tables in SQL exist in schema
            invalid_tables = [table for table in sql_tables if table not in schema_tables]
            
            if invalid_tables:
                return False, f"Unknown tables used: {', '.join(invalid_tables)}"
            
            # Additional syntax checks could be added here
            
            return True, "SQL syntax appears valid"
        
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _extract_table_names_from_schema(self, schema: str) -> set:
        """Extract table names from schema"""
        table_names = set()
        
        # Look for CREATE TABLE statements
        for match in re.finditer(r'CREATE\s+TABLE\s+(\w+)', schema, re.IGNORECASE):
            table_names.add(match.group(1).lower())
        
        return table_names
    
    def _extract_table_names_from_sql(self, sql: str) -> set:
        """Extract table names from SQL query"""
        table_names = set()
        
        # Simple extraction - look for FROM and JOIN clauses
        # This is a basic implementation and could be enhanced
        
        # FROM clause
        from_matches = re.finditer(r'FROM\s+(\w+)', sql, re.IGNORECASE)
        for match in from_matches:
            table_names.add(match.group(1).lower())
        
        # JOIN clauses
        join_matches = re.finditer(r'JOIN\s+(\w+)', sql, re.IGNORECASE)
        for match in join_matches:
            table_names.add(match.group(1).lower())
        
        return table_names
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model:
            return {}
        
        return {
            'model_name': ModelConfig.SLM_MODEL,
            'device': self.device,
            'model_size': f"{sum(p.numel() for p in self.model.parameters()) / 1e6:.1f}M parameters",
            'dtype': str(self.model.dtype),
            'max_tokens': ModelConfig.SLM_MAX_TOKENS,
            'temperature': ModelConfig.SLM_TEMPERATURE
        }
    
    def generate_explanation(self, sql: str, user_query: str) -> str:
        """Generate explanation for the SQL query"""
        try:
            explanation_prompt = f"""Explain this SQL query in simple terms:

User Question: {user_query}

SQL Query: {sql}

Explanation:"""
            
            response = self.generator(
                explanation_prompt,
                max_new_tokens=200,
                temperature=0.3,
                do_sample=True,
                return_full_text=False
            )[0]['generated_text']
            
            return response.strip()
        
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Unable to generate explanation for this query."

# Fallback simple SQL generator for emergency cases
class FallbackSQLGenerator:
    """Simple fallback SQL generator using templates"""
    
    def __init__(self):
        self.templates = {
            'count': "SELECT COUNT(*) FROM {table}",
            'select_all': "SELECT * FROM {table} LIMIT 10",
            'average': "SELECT AVG({column}) FROM {table}",
            'sum': "SELECT SUM({column}) FROM {table}",
            'max': "SELECT MAX({column}) FROM {table}",
            'min': "SELECT MIN({column}) FROM {table}"
        }
    
    def generate_sql(self, user_query: str, relevant_schema: str) -> str:
        """Generate simple SQL using templates"""
        query_lower = user_query.lower()
        
        # Extract first table name from schema
        table_match = re.search(r'CREATE\s+TABLE\s+(\w+)', relevant_schema, re.IGNORECASE)
        if not table_match:
            return "SELECT 1"  # Minimal valid query
        
        table_name = table_match.group(1)
        
        # Simple pattern matching
        if 'count' in query_lower or 'how many' in query_lower:
            return self.templates['count'].format(table=table_name)
        elif 'average' in query_lower or 'avg' in query_lower:
            return f"SELECT AVG(*) FROM {table_name}"  # Simplified
        elif 'sum' in query_lower or 'total' in query_lower:
            return f"SELECT SUM(*) FROM {table_name}"  # Simplified
        else:
            return self.templates['select_all'].format(table=table_name)

if __name__ == "__main__":
    # Test the SQL generator
    logging.basicConfig(level=logging.INFO)
    
    # Test with fallback generator first
    fallback_gen = FallbackSQLGenerator()
    
    test_schema = """
    CREATE TABLE accounts (
        id INT PRIMARY KEY,
        name VARCHAR(255),
        balance DECIMAL(10,2)
    );
    """
    
    test_query = "How many accounts are there?"
    fallback_sql = fallback_gen.generate_sql(test_query, test_schema)
    print(f"Fallback SQL: {fallback_sql}")
    
    # Test with local SLM (if available)
    try:
        sql_gen = LocalSQLGenerator()
        model_info = sql_gen.get_model_info()
        print(f"Model loaded: {model_info}")
        
        # Generate SQL
        generated_sql = sql_gen.generate_sql(test_query, test_schema)
        print(f"Generated SQL: {generated_sql}")
        
    except Exception as e:
        print(f"SLM not available: {e}")
        print("Using fallback generator instead")
