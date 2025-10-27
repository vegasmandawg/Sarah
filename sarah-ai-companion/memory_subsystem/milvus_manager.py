"""
Milvus Vector Database Manager for the Memory Subsystem
Handles vector storage and similarity search for conversations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)

logger = logging.getLogger(__name__)


class MilvusManager:
    """Manages Milvus vector database operations"""
    
    def __init__(self, host: str = "localhost", port: int = 19530):
        self.host = host
        self.port = port
        self.collection_name = "conversational_memories"
        self.collection: Optional[Collection] = None
        self._connected = False
    
    async def connect(self):
        """Connect to Milvus server"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            self._connected = True
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from Milvus server"""
        if self._connected:
            connections.disconnect("default")
            self._connected = False
            logger.info("Disconnected from Milvus")
    
    def is_connected(self) -> bool:
        """Check if connected to Milvus"""
        return self._connected and connections.has_connection("default")
    
    async def create_collections(self):
        """Create necessary collections if they don't exist"""
        try:
            # Check if collection exists
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                logger.info(f"Using existing collection: {self.collection_name}")
            else:
                # Define schema
                fields = [
                    FieldSchema(
                        name="embedding_id",
                        dtype=DataType.VARCHAR,
                        is_primary=True,
                        max_length=128
                    ),
                    FieldSchema(
                        name="user_id",
                        dtype=DataType.VARCHAR,
                        max_length=255
                    ),
                    FieldSchema(
                        name="character_id",
                        dtype=DataType.VARCHAR,
                        max_length=255
                    ),
                    FieldSchema(
                        name="conversation_text",
                        dtype=DataType.VARCHAR,
                        max_length=4096
                    ),
                    FieldSchema(
                        name="embedding",
                        dtype=DataType.FLOAT_VECTOR,
                        dim=384  # all-MiniLM-L6-v2 dimension
                    ),
                    FieldSchema(
                        name="timestamp",
                        dtype=DataType.INT64
                    )
                ]
                
                schema = CollectionSchema(
                    fields=fields,
                    description="Conversational memory embeddings"
                )
                
                # Create collection
                self.collection = Collection(
                    name=self.collection_name,
                    schema=schema
                )
                
                # Create index for vector field
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 1024}
                }
                
                self.collection.create_index(
                    field_name="embedding",
                    index_params=index_params
                )
                
                logger.info(f"Created collection: {self.collection_name}")
            
            # Load collection to memory
            self.collection.load()
            logger.info("Collection loaded to memory")
            
        except Exception as e:
            logger.error(f"Failed to create collections: {e}")
            raise
    
    async def insert_conversation(
        self,
        user_id: str,
        character_id: str,
        text: str,
        embedding: List[float]
    ) -> str:
        """Insert a conversation embedding into Milvus"""
        try:
            embedding_id = str(uuid.uuid4())
            timestamp = int(datetime.utcnow().timestamp())
            
            data = [
                [embedding_id],  # embedding_id
                [user_id],       # user_id
                [character_id],  # character_id
                [text[:4096]],   # conversation_text (truncate if needed)
                [embedding],     # embedding
                [timestamp]      # timestamp
            ]
            
            self.collection.insert(data)
            
            # Flush to ensure data is persisted
            self.collection.flush()
            
            logger.debug(f"Inserted conversation embedding: {embedding_id}")
            return embedding_id
            
        except Exception as e:
            logger.error(f"Failed to insert conversation: {e}")
            raise
    
    async def search_conversations(
        self,
        user_id: str,
        character_id: str,
        query_embedding: List[float],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar conversations"""
        try:
            # Build search expression
            expr = f'user_id == "{user_id}" and character_id == "{character_id}"'
            
            # Search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Perform search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit * 2,  # Get more results to filter
                expr=expr,
                output_fields=["conversation_text", "timestamp"]
            )
            
            # Process results
            conversations = []
            for hits in results:
                for hit in hits[:limit]:  # Limit final results
                    conversations.append({
                        "text": hit.entity.get("conversation_text"),
                        "score": hit.score,
                        "timestamp": hit.entity.get("timestamp")
                    })
            
            # Sort by score (highest first)
            conversations.sort(key=lambda x: x["score"], reverse=True)
            
            logger.debug(f"Found {len(conversations)} similar conversations")
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return []
    
    async def delete_user_conversations(
        self,
        user_id: str,
        character_id: Optional[str] = None
    ) -> int:
        """Delete conversations for a user (and optionally character)"""
        try:
            expr = f'user_id == "{user_id}"'
            if character_id:
                expr += f' and character_id == "{character_id}"'
            
            # Delete entities
            result = self.collection.delete(expr)
            
            # Flush to ensure deletion
            self.collection.flush()
            
            deleted_count = result.delete_count if hasattr(result, 'delete_count') else 0
            logger.info(f"Deleted {deleted_count} conversations for user {user_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete conversations: {e}")
            return 0
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            if not self.collection:
                return {}
            
            stats = {
                "collection_name": self.collection_name,
                "entity_count": self.collection.num_entities,
                "loaded": utility.load_state(self.collection_name),
                "index_info": self.collection.index().params
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
