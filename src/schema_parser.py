"""
Database Schema Parser
Extracts table and column information from database schema for embedding generation.
"""
import re
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ColumnInfo:
    """Information about a database column"""
    name: str
    data_type: str
    constraints: List[str]
    description: str

@dataclass
class TableInfo:
    """Information about a database table"""
    name: str
    columns: List[ColumnInfo]
    foreign_keys: List[Tuple[str, str]]  # (column, reference)
    description: str
    
    def get_searchable_text(self) -> str:
        """Generate searchable text representation for embeddings"""
        column_names = [col.name for col in self.columns]
        column_types = [col.data_type for col in self.columns]
        
        text_parts = [
            f"Table: {self.name}",
            f"Description: {self.description}",
            f"Columns: {', '.join(column_names)}",
            f"Column types: {', '.join(column_types)}"
        ]
        
        if self.foreign_keys:
            fk_info = [f"{col} references {ref}" for col, ref in self.foreign_keys]
            text_parts.append(f"Foreign keys: {', '.join(fk_info)}")
        
        return " | ".join(text_parts)

class SchemaParser:
    """Parser for database schema files"""
    
    def __init__(self, schema_path: Path):
        self.schema_path = schema_path
        self.tables: Dict[str, TableInfo] = {}
    
    def parse_schema(self) -> Dict[str, TableInfo]:
        """Parse the complete schema file"""
        logger.info(f"Parsing schema from {self.schema_path}")
        
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema_content = f.read()
        except FileNotFoundError:
            logger.error(f"Schema file not found: {self.schema_path}")
            raise
        
        # Split into individual CREATE TABLE statements
        table_statements = self._extract_table_statements(schema_content)
        
        for statement in table_statements:
            table_info = self._parse_table_statement(statement)
            if table_info:
                self.tables[table_info.name] = table_info
        
        logger.info(f"Successfully parsed {len(self.tables)} tables")
        return self.tables
    
    def _extract_table_statements(self, schema_content: str) -> List[str]:
        """Extract individual CREATE TABLE statements"""
        # Remove comments
        schema_content = re.sub(r'--.*?\n', '\n', schema_content)
        
        # Split by CREATE TABLE (case insensitive)
        statements = re.split(r'(?i)(?=CREATE\s+TABLE)', schema_content)
        
        # Filter out empty statements
        return [stmt.strip() for stmt in statements if stmt.strip()]
    
    def _parse_table_statement(self, statement: str) -> TableInfo:
        """Parse a single CREATE TABLE statement"""
        try:
            # Extract table name
            table_match = re.search(r'CREATE\s+TABLE\s+(\w+)', statement, re.IGNORECASE)
            if not table_match:
                return None
            
            table_name = table_match.group(1)
            
            # Extract columns and constraints
            columns = []
            foreign_keys = []
            
            # Find the content between parentheses
            content_match = re.search(r'\((.*)\)', statement, re.DOTALL)
            if not content_match:
                return None
            
            content = content_match.group(1)
            
            # Split by lines and parse each
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            for line in lines:
                line = line.rstrip(',')
                
                if line.upper().startswith('FOREIGN KEY'):
                    # Parse foreign key constraint
                    fk_match = re.search(r'FOREIGN\s+KEY\s*\((\w+)\)\s+REFERENCES\s+(\w+)\s*\((\w+)\)', line, re.IGNORECASE)
                    if fk_match:
                        col_name, ref_table, ref_col = fk_match.groups()
                        foreign_keys.append((col_name, f"{ref_table}.{ref_col}"))
                
                elif not line.upper().startswith(('PRIMARY KEY', 'UNIQUE', 'INDEX', 'CONSTRAINT')):
                    # Parse column definition
                    column_info = self._parse_column_definition(line)
                    if column_info:
                        columns.append(column_info)
            
            # Generate table description
            description = self._generate_table_description(table_name, columns)
            
            return TableInfo(
                name=table_name,
                columns=columns,
                foreign_keys=foreign_keys,
                description=description
            )
        
        except Exception as e:
            logger.warning(f"Error parsing table statement: {e}")
            return None
    
    def _parse_column_definition(self, line: str) -> ColumnInfo:
        """Parse a single column definition"""
        try:
            # Basic pattern: column_name data_type [constraints]
            parts = line.split()
            if len(parts) < 2:
                return None
            
            col_name = parts[0]
            data_type = parts[1]
            
            # Extract constraints
            constraints = []
            line_upper = line.upper()
            
            if 'PRIMARY KEY' in line_upper:
                constraints.append('PRIMARY KEY')
            if 'NOT NULL' in line_upper:
                constraints.append('NOT NULL')
            if 'UNIQUE' in line_upper:
                constraints.append('UNIQUE')
            if 'AUTO_INCREMENT' in line_upper or 'AUTOINCREMENT' in line_upper:
                constraints.append('AUTO_INCREMENT')
            
            # Generate column description
            description = self._generate_column_description(col_name, data_type, constraints)
            
            return ColumnInfo(
                name=col_name,
                data_type=data_type,
                constraints=constraints,
                description=description
            )
        
        except Exception as e:
            logger.warning(f"Error parsing column definition '{line}': {e}")
            return None
    
    def _generate_table_description(self, table_name: str, columns: List[ColumnInfo]) -> str:
        """Generate a human-readable description of the table"""
        # Extract semantic meaning from table name
        name_parts = table_name.lower().replace('_', ' ').split()
        
        # Common business domain mappings
        domain_mappings = {
            'account': 'financial accounts and customer information',
            'transaction': 'financial transactions and movements',
            'customer': 'customer data and profiles',
            'product': 'financial products and services',
            'loan': 'loan and credit information',
            'deposit': 'deposit and savings accounts',
            'payment': 'payment processing and methods',
            'interest': 'interest rates and calculations',
            'balance': 'account balances and statements',
            'fee': 'fees and charges',
            'audit': 'audit trails and logging',
            'config': 'configuration and settings',
            'master': 'reference data and lookups',
            'mst': 'master reference data'
        }
        
        description_parts = []
        for part in name_parts:
            if part in domain_mappings:
                description_parts.append(domain_mappings[part])
            else:
                description_parts.append(part)
        
        base_description = f"Table containing {' '.join(description_parts)}"
        
        # Add column context
        key_columns = [col.name for col in columns if 'id' in col.name.lower() or 'name' in col.name.lower()]
        if key_columns:
            base_description += f" with key fields: {', '.join(key_columns[:3])}"
        
        return base_description
    
    def _generate_column_description(self, col_name: str, data_type: str, constraints: List[str]) -> str:
        """Generate a human-readable description of the column"""
        # Basic description from column name
        name_parts = col_name.lower().replace('_', ' ')
        
        description = f"{name_parts} ({data_type})"
        
        if constraints:
            description += f" - {', '.join(constraints)}"
        
        return description
    
    def get_all_tables(self) -> Dict[str, TableInfo]:
        """Get all parsed tables"""
        return self.tables
    
    def get_table_by_name(self, table_name: str) -> TableInfo:
        """Get specific table information"""
        return self.tables.get(table_name)
    
    def get_table_names(self) -> List[str]:
        """Get list of all table names"""
        return list(self.tables.keys())
    
    def export_summary(self) -> Dict:
        """Export a summary of the parsed schema"""
        return {
            'total_tables': len(self.tables),
            'tables': {
                name: {
                    'columns': len(table.columns),
                    'foreign_keys': len(table.foreign_keys),
                    'description': table.description
                }
                for name, table in self.tables.items()
            }
        }

if __name__ == "__main__":
    from config import SCHEMA_PATH
    
    # Test the parser
    parser = SchemaParser(SCHEMA_PATH)
    tables = parser.parse_schema()
    
    print(f"Parsed {len(tables)} tables:")
    for name, table in tables.items():
        print(f"- {name}: {len(table.columns)} columns, {len(table.foreign_keys)} FKs")
        print(f"  Description: {table.description}")
        print()
