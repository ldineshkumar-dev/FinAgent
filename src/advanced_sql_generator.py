"""
Advanced SQL Generator
Handles complex queries with JOINs, GROUP BY, ORDER BY, and subqueries
using enhanced schema understanding and relationship mapping.
"""
import logging
import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

from schema_parser import TableInfo
from lightweight_sql import QueryPattern

logger = logging.getLogger(__name__)

@dataclass
class TableRelationship:
    """Represents a relationship between two tables"""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: str = "foreign_key"
    
    def get_join_condition(self) -> str:
        """Get SQL JOIN condition"""
        return f"{self.from_table}.{self.from_column} = {self.to_table}.{self.to_column}"

@dataclass
class ComplexQueryPattern:
    """Pattern for complex SQL queries"""
    keywords: List[str]
    requires_join: bool
    requires_groupby: bool
    requires_orderby: bool
    requires_subquery: bool
    template: str
    description: str

class AdvancedSQLGenerator:
    """Advanced SQL generator with schema relationship understanding"""
    
    def __init__(self):
        self.relationships = {}
        self.table_graph = defaultdict(list)
        self.complex_patterns = self._initialize_complex_patterns()
        logger.info("Advanced SQL generator initialized")
    
    def build_relationship_map(self, tables: Dict[str, TableInfo]):
        """Build comprehensive relationship mapping from schema"""
        logger.info("Building advanced relationship map...")
        
        relationships = []
        
        for table_name, table_info in tables.items():
            for fk_column, fk_reference in table_info.foreign_keys:
                # Parse foreign key reference
                if '.' in fk_reference:
                    ref_table, ref_column = fk_reference.split('.')
                    
                    relationship = TableRelationship(
                        from_table=table_name,
                        from_column=fk_column,
                        to_table=ref_table,
                        to_column=ref_column
                    )
                    
                    relationships.append(relationship)
                    
                    # Build bidirectional graph for path finding
                    self.table_graph[table_name].append((ref_table, relationship))
                    self.table_graph[ref_table].append((table_name, relationship))
        
        self.relationships = {
            f"{rel.from_table}->{rel.to_table}": rel 
            for rel in relationships
        }
        
        logger.info(f"Built relationship map with {len(relationships)} connections")
        return relationships
    
    def _initialize_complex_patterns(self) -> List[ComplexQueryPattern]:
        """Initialize patterns for complex queries"""
        return [
            # GROUP BY patterns
            ComplexQueryPattern(
                keywords=["group by", "count by", "total by", "sum by", "average by", "count of", "by type", "by category"],
                requires_join=False,
                requires_groupby=True,
                requires_orderby=False,
                requires_subquery=False,
                template="SELECT {group_column}, COUNT(*) as count FROM {main_table} GROUP BY {group_column}",
                description="Group records by column"
            ),
            
            # JOIN patterns with aggregation
            ComplexQueryPattern(
                keywords=["accounts with", "customers with", "details with", "information with"],
                requires_join=True,
                requires_groupby=False,
                requires_orderby=False,
                requires_subquery=False,
                template="SELECT {select_columns} FROM {main_table} {joins} WHERE {conditions}",
                description="Join tables for detailed information"
            ),
            
            # ORDER BY patterns
            ComplexQueryPattern(
                keywords=["top", "highest", "lowest", "largest", "smallest", "order by", "sort by"],
                requires_join=False,
                requires_groupby=False,
                requires_orderby=True,
                requires_subquery=False,
                template="SELECT {select_columns} FROM {table} ORDER BY {order_column} {order_direction} LIMIT {limit}",
                description="Sort and limit results"
            ),
            
            # Complex aggregation with JOIN
            ComplexQueryPattern(
                keywords=["total accounts by type", "sum accounts by", "count customers by"],
                requires_join=True,
                requires_groupby=True,
                requires_orderby=True,
                requires_subquery=False,
                template="""SELECT {group_column}, COUNT(*) as count, SUM({sum_column}) as total 
                           FROM {main_table} {joins} 
                           GROUP BY {group_column} 
                           ORDER BY count DESC""",
                description="Complex aggregation with relationships"
            ),
            
            # Subquery patterns
            ComplexQueryPattern(
                keywords=["accounts that have", "customers who have", "records where exists"],
                requires_join=False,
                requires_groupby=False,
                requires_orderby=False,
                requires_subquery=True,
                template="""SELECT {select_columns} FROM {main_table} 
                           WHERE EXISTS (SELECT 1 FROM {sub_table} WHERE {sub_condition})""",
                description="Subquery for complex filtering"
            ),
            
            # Financial year patterns (common in finance)
            ComplexQueryPattern(
                keywords=["financial year", "yearly", "annual", "by year"],
                requires_join=False,
                requires_groupby=True,
                requires_orderby=True,
                requires_subquery=False,
                template="""SELECT EXTRACT(YEAR FROM {date_column}) as financial_year, 
                           COUNT(*) as count 
                           FROM {table} 
                           GROUP BY EXTRACT(YEAR FROM {date_column}) 
                           ORDER BY financial_year DESC""",
                description="Financial year analysis"
            ),
            
            # Account balance analysis
            ComplexQueryPattern(
                keywords=["account balance", "balance analysis", "account summary"],
                requires_join=True,
                requires_groupby=True,
                requires_orderby=True,
                requires_subquery=False,
                template="""SELECT acc.account_type, 
                           COUNT(*) as account_count,
                           AVG(acc.balance) as avg_balance,
                           SUM(acc.balance) as total_balance
                           FROM {main_table} acc
                           {joins}
                           GROUP BY acc.account_type
                           ORDER BY total_balance DESC""",
                description="Account balance analysis with types"
            )
        ]
    
    def generate_sql(self, user_query: str, relevant_schema: str, tables: Dict[str, TableInfo]) -> str:
        """Generate advanced SQL with complex query support"""
        try:
            logger.info(f"Generating advanced SQL for: {user_query}")
            
            # Build relationship map if not exists
            if not self.relationships:
                self.build_relationship_map(tables)
            
            # Detect query complexity
            complexity = self._analyze_query_complexity(user_query)
            logger.info(f"Query complexity: {complexity}")
            
            # Find best pattern
            pattern = self._match_complex_pattern(user_query)
            
            if pattern:
                # Generate complex SQL
                return self._generate_complex_sql(pattern, user_query, relevant_schema, tables)
            else:
                # Fallback to enhanced simple generation
                return self._generate_enhanced_simple_sql(user_query, relevant_schema, tables)
        
        except Exception as e:
            logger.error(f"Advanced SQL generation failed: {e}")
            # Ultimate fallback
            return self._generate_fallback_sql(user_query, relevant_schema)
    
    def _analyze_query_complexity(self, user_query: str) -> Dict[str, bool]:
        """Analyze what type of complex operations are needed"""
        query_lower = user_query.lower()
        
        complexity = {
            'needs_join': any(keyword in query_lower for keyword in [
                'with', 'along with', 'including', 'details', 'information',
                'account type', 'customer name', 'branch details'
            ]),
            'needs_groupby': any(keyword in query_lower for keyword in [
                'group by', 'count by', 'total by', 'sum by', 'each', 'per',
                'by type', 'by category', 'by year', 'by month'
            ]),
            'needs_orderby': any(keyword in query_lower for keyword in [
                'top', 'bottom', 'highest', 'lowest', 'largest', 'smallest',
                'sort', 'order', 'first', 'last', 'best', 'worst'
            ]),
            'needs_subquery': any(keyword in query_lower for keyword in [
                'that have', 'who have', 'which have', 'exists', 'contains',
                'where there is', 'with at least'
            ]),
            'needs_aggregation': any(keyword in query_lower for keyword in [
                'count', 'sum', 'total', 'average', 'avg', 'max', 'min',
                'how many', 'what is the total'
            ])
        }
        
        return complexity
    
    def _match_complex_pattern(self, user_query: str) -> Optional[ComplexQueryPattern]:
        """Match user query to complex patterns"""
        query_lower = user_query.lower()
        
        best_match = None
        best_score = 0
        
        for pattern in self.complex_patterns:
            score = 0
            for keyword in pattern.keywords:
                if keyword in query_lower:
                    score += len(keyword)  # Longer matches get higher scores
            
            if score > best_score:
                best_score = score
                best_match = pattern
        
        return best_match if best_score > 0 else None
    
    def _generate_complex_sql(self, pattern: ComplexQueryPattern, user_query: str, 
                            schema: str, tables: Dict[str, TableInfo]) -> str:
        """Generate SQL from complex pattern"""
        
        # Extract tables from schema
        schema_tables = self._extract_schema_tables(schema)
        main_table = self._select_main_table(user_query, schema_tables, tables)
        
        # Build context
        context = {
            'main_table': main_table,
            'select_columns': self._build_select_columns(user_query, main_table, tables),
            'group_column': self._find_group_column(user_query, main_table, tables),
            'order_column': self._find_order_column(user_query, main_table, tables),
            'order_direction': self._determine_order_direction(user_query),
            'date_column': self._find_date_column(main_table, tables),
            'sum_column': self._find_numeric_column(user_query, main_table, tables),
            'limit': self._extract_limit(user_query),
            'joins': '',
            'conditions': '1=1'
        }
        
        # Add JOINs if needed
        if pattern.requires_join:
            context['joins'] = self._build_joins(user_query, main_table, schema_tables)
        
        # Generate SQL from template
        sql = pattern.template.format(**context)
        
        # Clean up the SQL
        sql = self._clean_generated_sql(sql)
        
        logger.info(f"Generated complex SQL: {sql}")
        return sql
    
    def _build_joins(self, user_query: str, main_table: str, available_tables: List[str]) -> str:
        """Build JOIN clauses based on relationships"""
        joins = []
        
        # Find related tables mentioned in query
        query_lower = user_query.lower()
        related_tables = []
        
        for table in available_tables:
            table_lower = table.lower()
            if table != main_table and any(word in table_lower for word in query_lower.split()):
                related_tables.append(table)
        
        # Build JOINs using relationship map
        for related_table in related_tables:
            join_path = self._find_join_path(main_table, related_table)
            if join_path:
                joins.extend(join_path)
        
        return ' '.join(joins) if joins else ''
    
    def _find_join_path(self, from_table: str, to_table: str) -> List[str]:
        """Find JOIN path between two tables"""
        # Simple direct relationship check
        direct_key = f"{from_table}->{to_table}"
        reverse_key = f"{to_table}->{from_table}"
        
        if direct_key in self.relationships:
            rel = self.relationships[direct_key]
            return [f"JOIN {to_table} ON {rel.get_join_condition()}"]
        elif reverse_key in self.relationships:
            rel = self.relationships[reverse_key]
            return [f"JOIN {to_table} ON {rel.get_join_condition()}"]
        
        return []
    
    def _build_select_columns(self, user_query: str, table: str, tables: Dict[str, TableInfo]) -> str:
        """Build SELECT column list based on query intent"""
        query_lower = user_query.lower()
        
        if table not in tables:
            return "*"
        
        table_info = tables[table]
        important_columns = []
        
        # Add columns based on query keywords
        for column in table_info.columns:
            col_lower = column.name.lower()
            
            # Always include ID columns
            if 'id' in col_lower and len(important_columns) < 5:
                important_columns.append(f"{table}.{column.name}")
            
            # Include name/description columns
            elif any(word in col_lower for word in ['name', 'description', 'title']):
                important_columns.append(f"{table}.{column.name}")
            
            # Include columns mentioned in query
            elif any(word in col_lower for word in query_lower.split() if len(word) > 2):
                important_columns.append(f"{table}.{column.name}")
        
        # If no specific columns found, use key columns
        if not important_columns:
            key_columns = [col.name for col in table_info.columns[:3]]
            important_columns = [f"{table}.{col}" for col in key_columns]
        
        return ', '.join(important_columns[:5])  # Limit to 5 columns
    
    def _find_group_column(self, user_query: str, table: str, tables: Dict[str, TableInfo]) -> str:
        """Find appropriate column for GROUP BY"""
        if table not in tables:
            return "id"
        
        query_lower = user_query.lower()
        table_info = tables[table]
        
        # Look for columns mentioned in query
        for column in table_info.columns:
            col_lower = column.name.lower()
            if any(word in col_lower for word in query_lower.split() if len(word) > 2):
                return f"{table}.{column.name}"
        
        # Default to type/category columns
        for column in table_info.columns:
            col_lower = column.name.lower()
            if any(word in col_lower for word in ['type', 'category', 'status', 'group']):
                return f"{table}.{column.name}"
        
        return f"{table}.id"
    
    def _find_order_column(self, user_query: str, table: str, tables: Dict[str, TableInfo]) -> str:
        """Find appropriate column for ORDER BY"""
        if table not in tables:
            return "id"
        
        query_lower = user_query.lower()
        table_info = tables[table]
        
        # For balance-related queries, prefer balance columns
        if any(word in query_lower for word in ['balance', 'amount', 'total']):
            for column in table_info.columns:
                col_lower = column.name.lower()
                if any(word in col_lower for word in ['balance', 'amount', 'total']):
                    return f"{table}.{column.name}"
        
        # For date-related queries, prefer date columns
        if any(word in query_lower for word in ['recent', 'latest', 'newest', 'oldest']):
            for column in table_info.columns:
                col_lower = column.name.lower()
                if any(word in col_lower for word in ['date', 'time', 'created', 'modified']):
                    return f"{table}.{column.name}"
        
        return f"{table}.id"
    
    def _determine_order_direction(self, user_query: str) -> str:
        """Determine ASC or DESC for ORDER BY"""
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['top', 'highest', 'largest', 'best', 'desc']):
            return "DESC"
        elif any(word in query_lower for word in ['bottom', 'lowest', 'smallest', 'worst', 'asc']):
            return "ASC"
        else:
            return "DESC"  # Default to descending
    
    def _find_date_column(self, table: str, tables: Dict[str, TableInfo]) -> str:
        """Find date column for temporal queries"""
        if table not in tables:
            return "create_dnt"
        
        table_info = tables[table]
        
        for column in table_info.columns:
            col_lower = column.name.lower()
            if any(word in col_lower for word in ['date', 'time', 'created', 'dnt']):
                return f"{table}.{column.name}"
        
        return f"{table}.create_dnt"
    
    def _find_numeric_column(self, user_query: str, table: str, tables: Dict[str, TableInfo]) -> str:
        """Find numeric column for aggregation"""
        if table not in tables:
            return "id"
        
        query_lower = user_query.lower()
        table_info = tables[table]
        
        # Look for balance/amount columns
        for column in table_info.columns:
            col_lower = column.name.lower()
            data_type = column.data_type.upper()
            
            if ('DECIMAL' in data_type or 'FLOAT' in data_type or 'NUMERIC' in data_type):
                if any(word in col_lower for word in ['balance', 'amount', 'total', 'sum']):
                    return f"{table}.{column.name}"
        
        return f"{table}.id"
    
    def _extract_limit(self, user_query: str) -> int:
        """Extract LIMIT value from query"""
        import re
        numbers = re.findall(r'\b(\d+)\b', user_query)
        
        if numbers:
            limit = int(numbers[0])
            return min(max(limit, 1), 100)  # Between 1 and 100
        
        # Default limits based on query type
        query_lower = user_query.lower()
        if any(word in query_lower for word in ['top', 'first']):
            return 10
        elif any(word in query_lower for word in ['all', 'every']):
            return 100
        else:
            return 20
    
    def _extract_schema_tables(self, schema: str) -> List[str]:
        """Extract table names from schema"""
        tables = []
        for match in re.finditer(r'CREATE TABLE (\w+)', schema, re.IGNORECASE):
            tables.append(match.group(1))
        return tables
    
    def _select_main_table(self, user_query: str, available_tables: List[str], 
                          tables: Dict[str, TableInfo]) -> str:
        """Select the main table for the query"""
        query_lower = user_query.lower()
        
        # Score tables based on query relevance
        table_scores = []
        
        for table in available_tables:
            score = 0
            table_lower = table.lower()
            
            # Direct table name mentions
            if table_lower in query_lower:
                score += 10
            
            # Keyword matching
            for word in query_lower.split():
                if word in table_lower:
                    score += 5
            
            # Domain-specific scoring
            if 'account' in query_lower and 'account' in table_lower:
                score += 8
            if 'customer' in query_lower and 'customer' in table_lower:
                score += 8
            if 'transaction' in query_lower and 'transaction' in table_lower:
                score += 8
            
            table_scores.append((table, score))
        
        # Return highest scoring table
        table_scores.sort(key=lambda x: x[1], reverse=True)
        return table_scores[0][0] if table_scores else available_tables[0]
    
    def _generate_enhanced_simple_sql(self, user_query: str, schema: str, 
                                    tables: Dict[str, TableInfo]) -> str:
        """Enhanced simple SQL generation with relationship awareness"""
        schema_tables = self._extract_schema_tables(schema)
        main_table = self._select_main_table(user_query, schema_tables, tables)
        
        # Analyze if simple query needs enhancement
        complexity = self._analyze_query_complexity(user_query)
        
        if complexity['needs_groupby']:
            group_col = self._find_group_column(user_query, main_table, tables)
            return f"SELECT {group_col}, COUNT(*) as count FROM {main_table} GROUP BY {group_col}"
        
        elif complexity['needs_orderby']:
            order_col = self._find_order_column(user_query, main_table, tables)
            direction = self._determine_order_direction(user_query)
            limit = self._extract_limit(user_query)
            return f"SELECT * FROM {main_table} ORDER BY {order_col} {direction} LIMIT {limit}"
        
        else:
            return f"SELECT * FROM {main_table} LIMIT 10"
    
    def _generate_fallback_sql(self, user_query: str, schema: str) -> str:
        """Ultimate fallback SQL generation"""
        tables = self._extract_schema_tables(schema)
        if tables:
            return f"SELECT * FROM {tables[0]} LIMIT 10"
        return "SELECT 1"
    
    def _clean_generated_sql(self, sql: str) -> str:
        """Clean and format generated SQL"""
        # Remove extra whitespace
        sql = ' '.join(sql.split())
        
        # Remove empty JOINs
        sql = re.sub(r'\s+JOIN\s+WHERE', ' WHERE', sql)
        sql = re.sub(r'\s+WHERE\s+1=1\s+', ' ', sql)
        
        return sql.strip()
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about the advanced generator"""
        return {
            'type': 'advanced_schema_aware',
            'patterns': len(self.complex_patterns),
            'relationships': len(self.relationships),
            'capabilities': [
                'JOINs', 'GROUP BY', 'ORDER BY', 'Subqueries',
                'Complex aggregations', 'Relationship mapping'
            ]
        }

if __name__ == "__main__":
    # Test the advanced generator
    generator = AdvancedSQLGenerator()
    print("Advanced SQL Generator initialized")
    print(f"Capabilities: {generator.get_model_info()}")
