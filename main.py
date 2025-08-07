"""
MFT Finance AI Assistant - Main Application
Efficient single-SLM natural language to SQL system.
"""
import logging
import argparse
import time
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# Add src to path - Windows compatible
import os
src_path = os.path.join(os.path.dirname(__file__), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.config import (
    ModelConfig, VectorConfig, QueryConfig, LogConfig, 
    validate_config, ensure_directories
)
from src.schema_parser import SchemaParser
from src.embedding_service import EmbeddingService, EmbeddingCache
from src.vector_store import VectorStore
from src.sql_generator import FallbackSQLGenerator
from src.query_executor import QueryExecutor

# Configure logging
logging.basicConfig(
    level=getattr(logging, LogConfig.LOG_LEVEL),
    format=LogConfig.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('finance_ai.log')
    ]
)

logger = logging.getLogger(__name__)

class FinanceAISystem:
    """Main system orchestrator for the Finance AI Assistant"""
    
    def __init__(self):
        self.schema_parser = None
        self.embedding_service = None
        self.vector_store = None
        self.sql_generator = None
        self.query_executor = None
        self.tables = {}
        self.initialized = False
        
        # Performance metrics
        self.metrics = {
            'queries_processed': 0,
            'total_response_time': 0,
            'avg_response_time': 0,
            'embedding_time': 0,
            'sql_generation_time': 0,
            'query_execution_time': 0
        }
    
    def initialize(self, force_rebuild: bool = False) -> bool:
        """Initialize all system components"""
        try:
            logger.info("Initializing MFT Finance AI System...")
            start_time = time.time()
            
            # Validate configuration
            validate_config()
            ensure_directories()
            
            # Initialize components
            self._init_schema_parser()
            self._init_embedding_service()
            self._init_vector_store()
            self._init_sql_generator()
            self._init_query_executor()
            
            # Load or generate embeddings
            if force_rebuild or not self._embeddings_exist():
                logger.info("Building embeddings from scratch...")
                self._build_embeddings()
            else:
                logger.info("Using existing embeddings...")
            
            self.initialized = True
            init_time = time.time() - start_time
            
            logger.info(f"System initialized successfully in {init_time:.2f}s")
            return True
        
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            return False
    
    def _init_schema_parser(self):
        """Initialize schema parser"""
        from src.config import SCHEMA_PATH
        self.schema_parser = SchemaParser(SCHEMA_PATH)
        self.tables = self.schema_parser.parse_schema()
        logger.info(f"Schema parser initialized with {len(self.tables)} tables")
    
    def _init_embedding_service(self):
        """Initialize embedding service"""
        self.embedding_service = EmbeddingService()
        logger.info("Embedding service initialized")
    
    def _init_vector_store(self):
        """Initialize vector store"""
        self.vector_store = VectorStore()
        logger.info("Vector store initialized")
    
    def _init_sql_generator(self):
        """Initialize SQL generator"""
        try:
            # Use advanced generator for complex query support
            from src.advanced_sql_generator import AdvancedSQLGenerator
            self.sql_generator = AdvancedSQLGenerator()
            logger.info("Advanced SQL generator initialized")
        except Exception as e:
            logger.warning(f"Failed to load advanced generator: {e}")
            try:
                # Fallback to lightweight generator
                from src.lightweight_sql import LightweightSQLGenerator
                self.sql_generator = LightweightSQLGenerator()
                logger.info("Using lightweight SQL generator as fallback")
            except Exception as e2:
                logger.warning(f"Failed to load lightweight generator: {e2}")
                logger.info("Using basic fallback SQL generator")
                from src.sql_generator import FallbackSQLGenerator
                self.sql_generator = FallbackSQLGenerator()
    
    def _init_query_executor(self):
        """Initialize query executor"""
        self.query_executor = QueryExecutor()
        logger.info("Query executor initialized")
    
    def _embeddings_exist(self) -> bool:
        """Check if embeddings already exist"""
        try:
            stats = self.vector_store.get_collection_stats()
            return stats.get('total_embeddings', 0) > 0
        except:
            return False
    
    def _build_embeddings(self):
        """Build and store embeddings"""
        logger.info("Generating embeddings...")
        
        # Generate table embeddings
        table_embeddings = self.embedding_service.generate_table_embeddings(self.tables)
        
        # Generate column embeddings
        column_embeddings = self.embedding_service.generate_column_embeddings(self.tables)
        
        # Store in vector database
        logger.info("Storing embeddings in vector database...")
        self.vector_store.add_table_embeddings(table_embeddings, self.tables)
        self.vector_store.add_column_embeddings(column_embeddings, self.tables)
        
        # Cache embeddings for future use
        if hasattr(self.embedding_service, 'cache'):
            cache = EmbeddingCache(str(Path(__file__).parent / "embeddings"))
            cache.save_embeddings(table_embeddings, "table_embeddings")
            cache.save_embeddings(column_embeddings, "column_embeddings")
        
        logger.info("✅ Embeddings built and stored successfully")
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process a natural language query and return results"""
        if not self.initialized:
            return {'error': 'System not initialized'}
        
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: {user_query}")
            
            # Step 1: Generate query embeddings
            embedding_start = time.time()
            query_embedding = self.embedding_service.generate_query_embedding(user_query)
            embedding_time = time.time() - embedding_start
            
            # Step 2: Find relevant tables using vector similarity
            relevant_schema = self.vector_store.get_relevant_schema(query_embedding, self.tables)
            
            # Step 3: Generate SQL using advanced generator
            sql_start = time.time()
            if hasattr(self.sql_generator, 'generate_sql') and len(self.sql_generator.generate_sql.__code__.co_varnames) > 3:
                # Advanced generator with tables parameter
                sql_query = self.sql_generator.generate_sql(user_query, relevant_schema, self.tables)
            else:
                # Fallback generator
                sql_query = self.sql_generator.generate_sql(user_query, relevant_schema)
            sql_time = time.time() - sql_start
            
            # Step 4: Execute SQL query
            exec_start = time.time()
            success, result = self.query_executor.execute_query(sql_query)
            exec_time = time.time() - exec_start
            
            if not success:
                return {
                    'success': False,
                    'error': result,
                    'sql_query': sql_query,
                    'user_query': user_query
                }
            
            # Step 5: Format results
            formatted_result = self.query_executor.format_results(result, user_query)
            
            # Calculate metrics
            total_time = time.time() - start_time
            self._update_metrics(total_time, embedding_time, sql_time, exec_time)
            
            return {
                'success': True,
                'answer': formatted_result,
                'sql_query': sql_query,
                'user_query': user_query,
                'row_count': len(result) if hasattr(result, '__len__') else 0,
                'response_time': total_time,
                'metrics': {
                    'embedding_time': embedding_time,
                    'sql_generation_time': sql_time,
                    'query_execution_time': exec_time,
                    'total_time': total_time
                }
            }
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'success': False,
                'error': str(e),
                'user_query': user_query
            }
    
    def _update_metrics(self, total_time: float, embedding_time: float, sql_time: float, exec_time: float):
        """Update performance metrics"""
        self.metrics['queries_processed'] += 1
        self.metrics['total_response_time'] += total_time
        self.metrics['avg_response_time'] = self.metrics['total_response_time'] / self.metrics['queries_processed']
        self.metrics['embedding_time'] += embedding_time
        self.metrics['sql_generation_time'] += sql_time
        self.metrics['query_execution_time'] += exec_time
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and metrics"""
        try:
            vector_stats = self.vector_store.get_collection_stats()
            db_info = self.query_executor.get_database_info()
            
            if hasattr(self.sql_generator, 'get_model_info'):
                model_info = self.sql_generator.get_model_info()
            else:
                model_info = {'type': 'fallback'}
            
            embedding_info = self.embedding_service.get_model_info()
            
            return {
                'initialized': self.initialized,
                'components': {
                    'schema_parser': len(self.tables) if self.tables else 0,
                    'vector_store': vector_stats,
                    'database': db_info,
                    'sql_generator': model_info,
                    'embedding_service': embedding_info
                },
                'metrics': self.metrics
            }
        
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    def reset_system(self):
        """Reset the system (clear embeddings, etc.)"""
        try:
            logger.warning("Resetting system...")
            if self.vector_store:
                self.vector_store.reset_collection()
            self.metrics = {key: 0 for key in self.metrics}
            logger.info("✅ System reset successfully")
        except Exception as e:
            logger.error(f"Error resetting system: {e}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='MFT Finance AI Assistant')
    parser.add_argument('--init-embeddings', action='store_true', 
                       help='Initialize embeddings from scratch')
    parser.add_argument('--status', action='store_true', 
                       help='Show system status')
    parser.add_argument('--reset', action='store_true', 
                       help='Reset system and clear embeddings')
    parser.add_argument('--query', type=str, 
                       help='Process a single query')
    parser.add_argument('--interactive', action='store_true', 
                       help='Start interactive mode')
    
    args = parser.parse_args()
    
    # Initialize system
    system = FinanceAISystem()
    
    if args.reset:
        system.reset_system()
        return
    
    if not system.initialize(force_rebuild=args.init_embeddings):
        print("❌ Failed to initialize system")
        return
    
    if args.status:
        status = system.get_system_status()
        print("📊 System Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        return
    
    if args.query:
        result = system.process_query(args.query)
        if result['success']:
            print(f"✅ Answer: {result['answer']}")
            print(f"🔍 SQL: {result['sql_query']}")
            print(f"⏱️ Response time: {result['response_time']:.2f}s")
        else:
            print(f"❌ Error: {result['error']}")
        return
    
    if args.interactive or len(sys.argv) == 1:
        # Interactive mode
        print("🤖 MFT Finance AI Assistant - Interactive Mode")
        print("Type your questions or 'exit' to quit")
        print("Commands: 'status', 'metrics', 'help'")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n💬 Your question: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                
                elif user_input.lower() == 'status':
                    status = system.get_system_status()
                    print(f"📊 System Status: {status}")
                    continue
                
                elif user_input.lower() == 'metrics':
                    print(f"📈 Metrics: {system.metrics}")
                    continue
                
                elif user_input.lower() == 'help':
                    print("Available commands:")
                    print("  - Ask any question about your financial data")
                    print("  - 'status': Show system status")
                    print("  - 'metrics': Show performance metrics")
                    print("  - 'exit': Quit the application")
                    continue
                
                elif not user_input:
                    continue
                
                # Process the query
                print("🔄 Processing...")
                result = system.process_query(user_input)
                
                if result['success']:
                    print(f"\n✅ {result['answer']}")
                    print(f"\n🔍 SQL Query: {result['sql_query']}")
                    print(f"⏱️ Response Time: {result['response_time']:.2f}s")
                else:
                    print(f"\n❌ Error: {result['error']}")
                    if 'sql_query' in result:
                        print(f"🔍 Attempted SQL: {result['sql_query']}")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
