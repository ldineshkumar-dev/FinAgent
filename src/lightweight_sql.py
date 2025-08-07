"""
Lightweight SQL Generator
Template-based SQL generation optimized for CPU-only operation.
"""
import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class QueryPattern:
    """A query pattern with template and keywords"""
    keywords: List[str]
    template: str
    description: str

class LightweightSQLGenerator:
    """Lightweight template-based SQL generator for CPU operation"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        logger.info("Lightweight SQL generator initialized")
    
    def _initialize_patterns(self) -> List[QueryPattern]:
        """Initialize common SQL patterns"""
        return [
            # Count patterns
            QueryPattern(
                keywords=["count", "how many", "number of", "total"],
                template="SELECT COUNT(*) as total_count FROM {table}",
                description="Count records in table"
            ),
            
            # Average patterns
            QueryPattern(
                keywords=["average", "avg", "mean"],
                template="SELECT AVG({numeric_column}) as average_value FROM {table}",
                description="Calculate average of numeric column"
            ),
            
            # Sum patterns
            QueryPattern(
                keywords=["sum", "total", "add up"],
                template="SELECT SUM({numeric_column}) as total_sum FROM {table}",
                description="Sum numeric column"
            ),
            
            # Max/Min patterns
            QueryPattern(
                keywords=["maximum", "max", "highest", "largest"],
                template="SELECT MAX({column}) as max_value FROM {table}",
                description="Find maximum value"
            ),
            
            QueryPattern(
                keywords=["minimum", "min", "lowest", "smallest"],
                template="SELECT MIN({column}) as min_value FROM {table}",
                description="Find minimum value"
            ),
            
            # List/Show patterns
            QueryPattern(
                keywords=["list", "show", "display", "all"],
                template="SELECT * FROM {table} LIMIT 10",
                description="Show records from table"
            ),
            
            # Group by patterns
            QueryPattern(
                keywords=["group by", "grouped", "by category", "by type"],
                template="SELECT {group_column}, COUNT(*) as count FROM {table} GROUP BY {group_column}",
                description="Group records by column"
            ),
            
            # Top/Bottom patterns
            QueryPattern(
                keywords=["top", "best", "highest"],
                template="SELECT * FROM {table} ORDER BY {order_column} DESC LIMIT {limit}",
                description="Show top records"
            ),
            
            QueryPattern(
                keywords=["bottom", "worst", "lowest"],
                template="SELECT * FROM {table} ORDER BY {order_column} ASC LIMIT {limit}",
                description="Show bottom records"
            ),
            
            # Year/Time patterns
            QueryPattern(
                keywords=["year", "annual", "yearly"],
                template="SELECT EXTRACT(YEAR FROM {date_column}) as year, COUNT(*) as count FROM {table} GROUP BY EXTRACT(YEAR FROM {date_column})",
                description="Group by year"
            )
        ]
    
    def generate_sql(self, user_query: str, relevant_schema: str) -> str:
        """Generate SQL using pattern matching and templates"""
        try:
            logger.info(f"Generating SQL for: {user_query}")
            
            # Extract table information from schema
            tables = self._extract_tables_from_schema(relevant_schema)
            if not tables:
                return "SELECT 1"  # Fallback query
            
            # Use the first table as primary
            primary_table = tables[0]
            table_info = self._extract_table_info(relevant_schema, primary_table)
            
            # Match query pattern
            matched_pattern = self._match_query_pattern(user_query)
            
            if matched_pattern:
                # Generate SQL from template
                sql = self._generate_from_template(
                    matched_pattern, 
                    user_query, 
                    primary_table, 
                    table_info
                )
                logger.info(f"Generated SQL: {sql}")
                return sql
            else:
                # Default fallback
                logger.warning("No pattern matched, using default query")
                return f"SELECT * FROM {primary_table} LIMIT 10"
        
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            return "SELECT 1"  # Safe fallback
    
    def _extract_tables_from_schema(self, schema: str) -> List[str]:
        """Extract table names from schema"""
        tables = []
        for match in re.finditer(r'CREATE\s+TABLE\s+(\w+)', schema, re.IGNORECASE):
            tables.append(match.group(1))
        return tables
    
    def _extract_table_info(self, schema: str, table_name: str) -> Dict[str, List[str]]:
        """Extract column information for a table"""
        info = {
            'all_columns': [],
            'numeric_columns': [],
            'date_columns': [],
            'text_columns': []
        }
        
        # Find the table definition
        table_pattern = rf'CREATE\s+TABLE\s+{re.escape(table_name)}\s*\((.*?)\);'
        match = re.search(table_pattern, schema, re.IGNORECASE | re.DOTALL)
        
        if match:
            table_def = match.group(1)
            
            # Extract columns
            for line in table_def.split('\n'):
                line = line.strip().rstrip(',')
                if line and not line.upper().startswith(('FOREIGN KEY', 'PRIMARY KEY')):
                    parts = line.split()
                    if len(parts) >= 2:
                        col_name = parts[0]
                        col_type = parts[1].upper()
                        
                        info['all_columns'].append(col_name)
                        
                        if any(t in col_type for t in ['INT', 'DECIMAL', 'FLOAT', 'NUMERIC']):
                            info['numeric_columns'].append(col_name)
                        elif any(t in col_type for t in ['DATE', 'TIME', 'TIMESTAMP']):
                            info['date_columns'].append(col_name)
                        else:
                            info['text_columns'].append(col_name)
        
        return info
    
    def _match_query_pattern(self, user_query: str) -> Optional[QueryPattern]:
        """Match user query to a pattern"""
        query_lower = user_query.lower()
        
        best_match = None
        best_score = 0
        
        for pattern in self.patterns:
            score = 0
            for keyword in pattern.keywords:
                if keyword in query_lower:
                    score += len(keyword)  # Longer matches get higher scores
            
            if score > best_score:
                best_score = score
                best_match = pattern
        
        return best_match if best_score > 0 else None
    
    def _generate_from_template(self, pattern: QueryPattern, user_query: str, 
                              table_name: str, table_info: Dict[str, List[str]]) -> str:
        """Generate SQL from template with smart column selection"""
        template = pattern.template
        
        # Replace table name
        template = template.replace('{table}', table_name)
        
        # Enhanced column selection using priority context from schema
        priority_columns = self._extract_priority_columns_from_query(user_query, table_info)
        
        # Handle column replacements with priority context
        if '{numeric_column}' in template:
            numeric_col = self._select_best_column_with_priority(
                user_query, table_info['numeric_columns'], priority_columns, 'numeric'
            )
            template = template.replace('{numeric_column}', numeric_col or 'id')
        
        if '{column}' in template:
            # Try to find the best column based on query context and priorities
            best_col = self._select_best_column_with_priority(
                user_query, table_info['all_columns'], priority_columns, 'any'
            )
            template = template.replace('{column}', best_col or table_info['all_columns'][0])
        
        if '{group_column}' in template:
            # Prefer text columns for grouping
            group_col = self._select_best_column_with_priority(
                user_query, table_info['text_columns'], priority_columns, 'text'
            )
            template = template.replace('{group_column}', group_col or 'id')
        
        if '{order_column}' in template:
            # Prefer numeric columns for ordering
            order_col = self._select_best_column_with_priority(
                user_query, table_info['numeric_columns'], priority_columns, 'numeric'
            )
            template = template.replace('{order_column}', order_col or 'id')
        
        if '{date_column}' in template:
            date_col = self._select_best_column_with_priority(
                user_query, table_info['date_columns'], priority_columns, 'date'
            )
            template = template.replace('{date_column}', date_col or 'create_dnt')
        
        if '{limit}' in template:
            limit = self._extract_limit_from_query(user_query)
            template = template.replace('{limit}', str(limit))
        
        return template
    
    def _extract_priority_columns_from_query(self, user_query: str, table_info: Dict[str, List[str]]) -> Dict[str, float]:
        """Extract priority columns mentioned in the query"""
        priority_columns = {}
        query_lower = user_query.lower()
        
        # Look for column names mentioned in the query
        all_columns = table_info.get('all_columns', [])
        
        for column in all_columns:
            col_lower = column.lower()
            # Direct mention gets highest priority
            if col_lower in query_lower:
                priority_columns[column] = 1.0
            # Partial word matches
            elif any(word in col_lower for word in query_lower.split() if len(word) > 2):
                priority_columns[column] = 0.7
            # Common financial terms mapping
            elif self._is_financial_term_match(query_lower, col_lower):
                priority_columns[column] = 0.8
        
        return priority_columns
    
    def _is_financial_term_match(self, query: str, column: str) -> bool:
        """Check if query contains financial terms that match column"""
        financial_mappings = {
            'balance': ['balance', 'amount', 'total'],
            'name': ['name', 'title', 'description'],
            'account': ['account', 'acct'],
            'date': ['date', 'time', 'created', 'modified', 'dnt'],
            'id': ['id', 'number', 'code'],
            'type': ['type', 'category', 'kind'],
            'status': ['status', 'state', 'active']
        }
        
        for term, variations in financial_mappings.items():
            if term in query:
                if any(var in column for var in variations):
                    return True
        
        return False
    
    def _select_best_column_with_priority(self, user_query: str, columns: List[str], 
                                        priority_columns: Dict[str, float], column_type: str) -> Optional[str]:
        """Enhanced column selection using priority context"""
        if not columns:
            return None
        
        # First, check if any priority columns are in the available columns
        priority_matches = []
        for column in columns:
            if column in priority_columns:
                priority_matches.append((column, priority_columns[column]))
        
        if priority_matches:
            # Return highest priority column
            priority_matches.sort(key=lambda x: x[1], reverse=True)
            return priority_matches[0][0]
        
        # Fallback to original selection logic
        return self._select_best_column(user_query, columns)
    
    def _select_best_column(self, user_query: str, columns: List[str]) -> Optional[str]:
        """Select the best column based on query context"""
        if not columns:
            return None
        
        query_lower = user_query.lower()
        
        # Score columns based on query keywords
        scored_columns = []
        for col in columns:
            score = 0
            col_lower = col.lower()
            
            # Exact name match
            if col_lower in query_lower:
                score += 10
            
            # Partial matches
            for word in query_lower.split():
                if word in col_lower or col_lower in word:
                    score += 5
            
            # Context-based scoring
            if 'balance' in query_lower and 'balance' in col_lower:
                score += 15
            if 'name' in query_lower and 'name' in col_lower:
                score += 15
            if 'amount' in query_lower and 'amount' in col_lower:
                score += 15
            if 'date' in query_lower and ('date' in col_lower or 'dnt' in col_lower):
                score += 15
            
            scored_columns.append((col, score))
        
        # Return highest scored column
        scored_columns.sort(key=lambda x: x[1], reverse=True)
        return scored_columns[0][0] if scored_columns[0][1] > 0 else columns[0]
    
    def _extract_limit_from_query(self, user_query: str) -> int:
        """Extract limit number from query"""
        import re
        
        # Look for numbers in the query
        numbers = re.findall(r'\b(\d+)\b', user_query)
        
        if numbers:
            limit = int(numbers[0])
            # Reasonable limits
            return min(max(limit, 1), 100)
        
        # Default limits based on context
        if any(word in user_query.lower() for word in ['top', 'best', 'worst']):
            return 10
        else:
            return 5
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the generator"""
        return {
            'type': 'lightweight_template_based',
            'patterns': len(self.patterns),
            'device': 'cpu',
            'memory_usage': 'minimal',
            'performance': 'instant'
        }

if __name__ == "__main__":
    # Test the lightweight generator
    generator = LightweightSQLGenerator()
    
    test_schema = """
    CREATE TABLE i_acct_account_mst (
        id INT PRIMARY KEY,
        account_name VARCHAR(255),
        balance DECIMAL(10,2),
        create_dnt DATETIME
    );
    """
    
    test_queries = [
        "How many accounts are there?",
        "What is the average balance?",
        "Show me the top 5 accounts by balance",
        "List all account names"
    ]
    
    for query in test_queries:
        sql = generator.generate_sql(query, test_schema)
        print(f"Query: {query}")
        print(f"SQL: {sql}")
        print()
