"""
Vector Store
Manages vector database operations for fast similarity search.
"""
import logging
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
import chromadb
from chromadb.config import Settings
import json

from config import VectorConfig, EMBEDDINGS_DIR
from schema_parser import TableInfo

logger = logging.getLogger(__name__)

class VectorStore:
    """ChromaDB-based vector store for semantic search"""
    
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or str(EMBEDDINGS_DIR)
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client"""
        try:
            logger.info(f"Initializing ChromaDB at {self.persist_directory}")
            
            # Configure ChromaDB settings
            settings = Settings(
                persist_directory=self.persist_directory,
                allow_reset=True,
                anonymized_telemetry=False
            )
            
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=settings
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=VectorConfig.COLLECTION_NAME,
                metadata={"description": "Finance database schema embeddings"}
            )
            
            logger.info("ChromaDB initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_table_embeddings(self, table_embeddings: Dict[str, np.ndarray], tables: Dict[str, TableInfo]):
        """Add table embeddings to the vector store"""
        logger.info(f"Adding {len(table_embeddings)} table embeddings to vector store")
        
        try:
            # Prepare data for ChromaDB
            embeddings = []
            metadatas = []
            documents = []
            ids = []
            
            for table_name, embedding in table_embeddings.items():
                table_info = tables[table_name]
                
                # Convert numpy array to list
                embeddings.append(embedding.tolist())
                
                # Create metadata (ChromaDB doesn't support lists)
                metadata = {
                    "type": "table",
                    "table_name": table_name,
                    "column_count": len(table_info.columns),
                    "foreign_key_count": len(table_info.foreign_keys),
                    "columns_str": ",".join([col.name for col in table_info.columns]),
                    "column_types_str": ",".join([col.data_type for col in table_info.columns])
                }
                metadatas.append(metadata)
                
                # Use searchable text as document
                documents.append(table_info.get_searchable_text())
                
                # Create unique ID
                ids.append(f"table_{table_name}")
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
                ids=ids
            )
            
            logger.info("Table embeddings added successfully")
        
        except Exception as e:
            logger.error(f"Failed to add table embeddings: {e}")
            raise
    
    def add_column_embeddings(self, column_embeddings: Dict[str, Dict[str, np.ndarray]], tables: Dict[str, TableInfo]):
        """Add column embeddings to the vector store"""
        logger.info("Adding column embeddings to vector store")
        
        try:
            embeddings = []
            metadatas = []
            documents = []
            ids = []
            
            for table_name, table_columns in column_embeddings.items():
                table_info = tables[table_name]
                
                for column_name, embedding in table_columns.items():
                    # Find column info
                    column_info = next(
                        (col for col in table_info.columns if col.name == column_name),
                        None
                    )
                    
                    if column_info:
                        embeddings.append(embedding.tolist())
                        
                        metadata = {
                            "type": "column",
                            "table_name": table_name,
                            "column_name": column_name,
                            "data_type": column_info.data_type,
                            "constraints_str": ",".join(column_info.constraints)
                        }
                        metadatas.append(metadata)
                        
                        document = f"Table {table_name} column {column_name} {column_info.description}"
                        documents.append(document)
                        
                        ids.append(f"column_{table_name}_{column_name}")
            
            if embeddings:
                self.collection.add(
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents,
                    ids=ids
                )
                
                logger.info(f"✅ Added {len(embeddings)} column embeddings")
        
        except Exception as e:
            logger.error(f"Failed to add column embeddings: {e}")
            raise
    
    def search_similar_tables(self, query_embedding: np.ndarray, top_k: int = None) -> List[Tuple[str, float, Dict]]:
        """Search for similar tables using query embedding"""
        top_k = top_k or VectorConfig.MAX_RELEVANT_TABLES
        
        try:
            # Convert numpy array to list
            query_embedding_list = query_embedding.tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding_list],
                n_results=top_k,
                where={"type": "table"}  # Filter for table embeddings only
            )
            
            # Process results
            similar_tables = []
            
            if results['ids'] and results['ids'][0]:
                for i, table_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    metadata = results['metadatas'][0][i]
                    
                    # Convert distance to similarity (ChromaDB uses squared euclidean distance)
                    similarity = 1 / (1 + distance)  # Convert distance to similarity score
                    
                    # Only include tables above similarity threshold
                    if similarity >= VectorConfig.SIMILARITY_THRESHOLD:
                        table_name = metadata['table_name']
                        similar_tables.append((table_name, similarity, metadata))
            
            # Sort by similarity (highest first)
            similar_tables.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Found {len(similar_tables)} similar tables above threshold {VectorConfig.SIMILARITY_THRESHOLD}")
            return similar_tables
        
        except Exception as e:
            logger.error(f"Error searching similar tables: {e}")
            return []
    
    def search_similar_columns(self, query_embedding: np.ndarray, top_k: int = 20) -> List[Tuple[str, str, float, Dict]]:
        """Search for similar columns using query embedding"""
        try:
            query_embedding_list = query_embedding.tolist()
            
            results = self.collection.query(
                query_embeddings=[query_embedding_list],
                n_results=top_k,
                where={"type": "column"}
            )
            
            similar_columns = []
            
            if results['ids'] and results['ids'][0]:
                for i, column_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    metadata = results['metadatas'][0][i]
                    
                    similarity = 1 / (1 + distance)
                    
                    if similarity >= VectorConfig.SIMILARITY_THRESHOLD:
                        table_name = metadata['table_name']
                        column_name = metadata['column_name']
                        similar_columns.append((table_name, column_name, similarity, metadata))
            
            similar_columns.sort(key=lambda x: x[2], reverse=True)
            return similar_columns
        
        except Exception as e:
            logger.error(f"Error searching similar columns: {e}")
            return []
    
    def get_relevant_schema(self, query_embedding: np.ndarray, tables: Dict[str, TableInfo]) -> str:
        """Get relevant schema based on intelligent column+table similarity"""
        try:
            # Step 1: Search for relevant columns first (more specific)
            similar_columns = self.search_similar_columns(query_embedding, VectorConfig.MAX_RELEVANT_COLUMNS)
            
            # Step 2: Extract unique tables from relevant columns
            relevant_tables = set()
            column_context = {}
            
            for table_name, column_name, similarity, metadata in similar_columns:
                relevant_tables.add(table_name)
                if table_name not in column_context:
                    column_context[table_name] = []
                column_context[table_name].append({
                    'name': column_name,
                    'similarity': similarity,
                    'data_type': metadata.get('data_type', 'UNKNOWN')
                })
            
            # Step 3: If no columns found, fall back to table search
            if not relevant_tables:
                logger.info("No similar columns found, trying table-based search")
                similar_tables = self.search_similar_tables(query_embedding)
                if similar_tables:
                    relevant_tables = {table_name for table_name, _, _ in similar_tables}
                else:
                    logger.warning("No similar tables found either, returning focused schema")
                    return self._get_focused_schema(tables)
            
            # Step 4: Build enhanced schema with column context
            relevant_schema_parts = []
            
            for table_name in relevant_tables:
                if table_name in tables:
                    table_info = tables[table_name]
                    # Generate schema with column priorities
                    priority_columns = column_context.get(table_name, [])
                    schema_part = self._generate_enhanced_table_schema(table_info, priority_columns)
                    relevant_schema_parts.append(schema_part)
            
            relevant_schema = "\n\n".join(relevant_schema_parts)
            
            logger.info(f"Generated relevant schema with {len(relevant_tables)} tables and {len(similar_columns)} relevant columns")
            return relevant_schema
        
        except Exception as e:
            logger.error(f"Error getting relevant schema: {e}")
            return self._get_focused_schema(tables)
    
    def _generate_table_schema(self, table_info: TableInfo) -> str:
        """Generate CREATE TABLE statement for a table"""
        lines = [f"CREATE TABLE {table_info.name} ("]
        
        # Add columns
        column_lines = []
        for column in table_info.columns:
            constraint_str = " ".join(column.constraints) if column.constraints else ""
            column_line = f"    {column.name} {column.data_type}"
            if constraint_str:
                column_line += f" {constraint_str}"
            column_lines.append(column_line)
        
        # Add foreign keys
        for fk_column, fk_reference in table_info.foreign_keys:
            ref_parts = fk_reference.split('.')
            if len(ref_parts) == 2:
                ref_table, ref_column = ref_parts
                column_lines.append(f"    FOREIGN KEY ({fk_column}) REFERENCES {ref_table}({ref_column})")
        
        lines.append(",\n".join(column_lines))
        lines.append(");")
        
        return "\n".join(lines)
    
    def _generate_enhanced_table_schema(self, table_info: TableInfo, priority_columns: List[Dict]) -> str:
        """Generate table schema with column priorities and context"""
        # Sort columns by priority (similarity score)
        priority_col_names = {col['name']: col['similarity'] for col in priority_columns}
        
        # Create enhanced table description
        table_comment = f"-- Table: {table_info.name}"
        if priority_columns:
            top_columns = [col['name'] for col in sorted(priority_columns, key=lambda x: x['similarity'], reverse=True)[:3]]
            table_comment += f" (Key columns: {', '.join(top_columns)})"
        
        lines = [table_comment, f"CREATE TABLE {table_info.name} ("]
        
        # Sort columns: priority columns first, then others
        priority_cols = []
        other_cols = []
        
        for column in table_info.columns:
            if column.name in priority_col_names:
                priority_cols.append((column, priority_col_names[column.name]))
            else:
                other_cols.append(column)
        
        # Sort priority columns by similarity score
        priority_cols.sort(key=lambda x: x[1], reverse=True)
        
        # Add columns (priority first)
        column_lines = []
        
        # Add priority columns with comments
        for column, similarity in priority_cols:
            constraint_str = " ".join(column.constraints) if column.constraints else ""
            column_line = f"    {column.name} {column.data_type}"
            if constraint_str:
                column_line += f" {constraint_str}"
            column_line += f"  -- PRIORITY: {similarity:.2f}"
            column_lines.append(column_line)
        
        # Add other important columns (limit to avoid clutter)
        for column in other_cols[:5]:  # Limit to 5 additional columns
            constraint_str = " ".join(column.constraints) if column.constraints else ""
            column_line = f"    {column.name} {column.data_type}"
            if constraint_str:
                column_line += f" {constraint_str}"
            column_lines.append(column_line)
        
        # Add foreign keys
        for fk_column, fk_reference in table_info.foreign_keys:
            ref_parts = fk_reference.split('.')
            if len(ref_parts) == 2:
                ref_table, ref_column = ref_parts
                column_lines.append(f"    FOREIGN KEY ({fk_column}) REFERENCES {ref_table}({ref_column})")
        
        lines.append(",\n".join(column_lines))
        lines.append(");")
        
        return "\n".join(lines)
    
    def _get_focused_schema(self, tables: Dict[str, TableInfo]) -> str:
        """Generate focused schema with most likely useful tables"""
        # Return a few most common/important tables as fallback
        important_keywords = ['account', 'transaction', 'user', 'balance', 'payment']
        focused_tables = []
        
        for table_name, table_info in tables.items():
            table_lower = table_name.lower()
            if any(keyword in table_lower for keyword in important_keywords):
                focused_tables.append(table_info)
        
        # If no important tables found, return first 3 tables
        if not focused_tables:
            focused_tables = list(tables.values())[:3]
        
        schema_parts = []
        for table_info in focused_tables[:3]:  # Limit to 3 tables
            schema_parts.append(self._generate_table_schema(table_info))
        
        return "\n\n".join(schema_parts)
    
    def _get_full_schema(self, tables: Dict[str, TableInfo]) -> str:
        """Generate full schema as fallback"""
        schema_parts = []
        for table_info in tables.values():
            schema_parts.append(self._generate_table_schema(table_info))
        return "\n\n".join(schema_parts)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        try:
            count = self.collection.count()
            
            # Get sample metadata to understand data distribution
            sample_results = self.collection.get(limit=100)
            
            table_count = sum(1 for meta in sample_results.get('metadatas', []) if meta.get('type') == 'table')
            column_count = sum(1 for meta in sample_results.get('metadatas', []) if meta.get('type') == 'column')
            
            return {
                'total_embeddings': count,
                'table_embeddings': table_count,
                'column_embeddings': column_count,
                'collection_name': VectorConfig.COLLECTION_NAME,
                'persist_directory': self.persist_directory
            }
        
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def reset_collection(self):
        """Reset the collection (delete all data)"""
        try:
            logger.warning("Resetting vector collection - all data will be deleted")
            self.client.delete_collection(VectorConfig.COLLECTION_NAME)
            self.collection = self.client.create_collection(VectorConfig.COLLECTION_NAME)
            logger.info("✅ Collection reset successfully")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            raise
    
    def export_embeddings(self, output_path: str):
        """Export embeddings to a file for backup"""
        try:
            all_data = self.collection.get(include=['embeddings', 'metadatas', 'documents'])
            
            export_data = {
                'embeddings': all_data.get('embeddings', []),
                'metadatas': all_data.get('metadatas', []),
                'documents': all_data.get('documents', []),
                'ids': all_data.get('ids', [])
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Embeddings exported to {output_path}")
        
        except Exception as e:
            logger.error(f"Error exporting embeddings: {e}")
            raise

if __name__ == "__main__":
    # Test the vector store
    logging.basicConfig(level=logging.INFO)
    
    # Initialize vector store
    vector_store = VectorStore()
    
    # Get stats
    stats = vector_store.get_collection_stats()
    print("Vector Store Stats:")
    for key, value in stats.items():
        print(f"- {key}: {value}")
