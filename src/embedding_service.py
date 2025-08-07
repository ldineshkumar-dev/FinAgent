"""
Embedding Service
Handles generation and management of embeddings for database schema elements.
"""
import logging
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import torch
from tqdm import tqdm
from dataclasses import asdict

from schema_parser import TableInfo, SchemaParser
from config import ModelConfig, PerformanceConfig

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating and managing embeddings"""
    
    def __init__(self):
        self.model = None
        self.device = self._get_device()
        self._load_model()
    
    def _get_device(self) -> str:
        """Force CPU usage for lightweight operation"""
        device = "cpu"
        logger.info("Using CPU for embeddings (optimized for local operation)")
        return device
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {ModelConfig.EMBEDDING_MODEL}")
            self.model = SentenceTransformer(
                ModelConfig.EMBEDDING_MODEL,
                device=self.device
            )
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def generate_table_embeddings(self, tables: Dict[str, TableInfo]) -> Dict[str, np.ndarray]:
        """Generate embeddings for all tables"""
        logger.info(f"Generating embeddings for {len(tables)} tables")
        
        # Prepare texts for embedding
        table_texts = []
        table_names = []
        
        for name, table in tables.items():
            table_texts.append(table.get_searchable_text())
            table_names.append(name)
        
        # Generate embeddings in batches
        embeddings = self._generate_embeddings_batch(table_texts)
        
        # Create mapping
        table_embeddings = {
            name: embedding 
            for name, embedding in zip(table_names, embeddings)
        }
        
        logger.info("Table embeddings generated successfully")
        return table_embeddings
    
    def generate_column_embeddings(self, tables: Dict[str, TableInfo]) -> Dict[str, Dict[str, np.ndarray]]:
        """Generate embeddings for individual columns"""
        logger.info("Generating column-level embeddings")
        
        column_embeddings = {}
        
        for table_name, table in tables.items():
            column_texts = []
            column_names = []
            
            for column in table.columns:
                # Create descriptive text for column
                column_text = f"Table {table_name} column {column.name} {column.data_type} {column.description}"
                column_texts.append(column_text)
                column_names.append(column.name)
            
            if column_texts:
                embeddings = self._generate_embeddings_batch(column_texts)
                column_embeddings[table_name] = {
                    name: embedding 
                    for name, embedding in zip(column_names, embeddings)
                }
        
        logger.info("✅ Column embeddings generated successfully")
        return column_embeddings
    
    def generate_relationship_embeddings(self, tables: Dict[str, TableInfo]) -> Dict[str, np.ndarray]:
        """Generate embeddings for table relationships"""
        logger.info("Generating relationship embeddings")
        
        relationship_texts = []
        relationship_ids = []
        
        for table_name, table in tables.items():
            for fk_column, fk_reference in table.foreign_keys:
                relationship_text = f"Table {table_name} column {fk_column} references {fk_reference} foreign key relationship"
                relationship_texts.append(relationship_text)
                relationship_ids.append(f"{table_name}.{fk_column} -> {fk_reference}")
        
        if relationship_texts:
            embeddings = self._generate_embeddings_batch(relationship_texts)
            relationship_embeddings = {
                rel_id: embedding 
                for rel_id, embedding in zip(relationship_ids, embeddings)
            }
        else:
            relationship_embeddings = {}
        
        logger.info(f"✅ Generated {len(relationship_embeddings)} relationship embeddings")
        return relationship_embeddings
    
    def _generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a batch of texts"""
        if not texts:
            return []
        
        try:
            # Generate embeddings with progress bar
            with tqdm(total=len(texts), desc="Generating embeddings") as pbar:
                embeddings = []
                batch_size = ModelConfig.EMBEDDING_BATCH_SIZE
                
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    batch_embeddings = self.model.encode(
                        batch_texts,
                        convert_to_numpy=True,
                        show_progress_bar=False,
                        batch_size=len(batch_texts)
                    )
                    embeddings.extend(batch_embeddings)
                    pbar.update(len(batch_texts))
            
            return embeddings
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for a user query"""
        try:
            embedding = self.model.encode([query], convert_to_numpy=True)[0]
            return embedding
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def compute_similarity(self, query_embedding: np.ndarray, candidate_embeddings: List[np.ndarray]) -> List[float]:
        """Compute cosine similarity between query and candidate embeddings"""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Reshape for sklearn
            query_embedding = query_embedding.reshape(1, -1)
            candidate_embeddings = np.array(candidate_embeddings)
            
            # Compute similarities
            similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
            return similarities.tolist()
        
        except ImportError:
            # Fallback to manual computation
            return self._manual_cosine_similarity(query_embedding, candidate_embeddings)
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            raise
    
    def _manual_cosine_similarity(self, query_embedding: np.ndarray, candidate_embeddings: List[np.ndarray]) -> List[float]:
        """Manual cosine similarity computation"""
        similarities = []
        
        for candidate in candidate_embeddings:
            # Cosine similarity = dot product / (norm1 * norm2)
            dot_product = np.dot(query_embedding, candidate)
            norm_query = np.linalg.norm(query_embedding)
            norm_candidate = np.linalg.norm(candidate)
            
            if norm_query == 0 or norm_candidate == 0:
                similarity = 0.0
            else:
                similarity = dot_product / (norm_query * norm_candidate)
            
            similarities.append(float(similarity))
        
        return similarities
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model:
            return {}
        
        return {
            'model_name': ModelConfig.EMBEDDING_MODEL,
            'device': self.device,
            'max_seq_length': getattr(self.model, 'max_seq_length', 'Unknown'),
            'embedding_dimension': self.model.get_sentence_embedding_dimension(),
            'tokenizer': str(type(self.model.tokenizer).__name__)
        }

class EmbeddingCache:
    """Cache for storing and retrieving embeddings"""
    
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        self.cache = {}
    
    def save_embeddings(self, embeddings: Dict[str, np.ndarray], filename: str):
        """Save embeddings to cache"""
        import pickle
        from pathlib import Path
        
        cache_path = Path(self.cache_dir) / f"{filename}.pkl"
        cache_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(embeddings, f)
            logger.info(f"Embeddings saved to cache: {cache_path}")
        except Exception as e:
            logger.error(f"Failed to save embeddings to cache: {e}")
    
    def load_embeddings(self, filename: str) -> Dict[str, np.ndarray]:
        """Load embeddings from cache"""
        import pickle
        from pathlib import Path
        
        cache_path = Path(self.cache_dir) / f"{filename}.pkl"
        
        try:
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    embeddings = pickle.load(f)
                logger.info(f"Embeddings loaded from cache: {cache_path}")
                return embeddings
            else:
                logger.info(f"No cache found at: {cache_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load embeddings from cache: {e}")
            return {}

if __name__ == "__main__":
    from config import SCHEMA_PATH, EMBEDDINGS_DIR
    
    # Test the embedding service
    logger.basicConfig(level=logging.INFO)
    
    # Parse schema
    parser = SchemaParser(SCHEMA_PATH)
    tables = parser.parse_schema()
    
    # Generate embeddings
    embedding_service = EmbeddingService()
    
    # Test table embeddings
    table_embeddings = embedding_service.generate_table_embeddings(tables)
    print(f"Generated embeddings for {len(table_embeddings)} tables")
    
    # Test query embedding
    test_query = "show me all account information"
    query_embedding = embedding_service.generate_query_embedding(test_query)
    print(f"Query embedding shape: {query_embedding.shape}")
    
    # Test similarity
    table_emb_list = list(table_embeddings.values())
    similarities = embedding_service.compute_similarity(query_embedding, table_emb_list)
    
    # Show top matches
    table_names = list(table_embeddings.keys())
    scored_tables = list(zip(table_names, similarities))
    scored_tables.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop 5 most similar tables:")
    for name, score in scored_tables[:5]:
        print(f"- {name}: {score:.3f}")
