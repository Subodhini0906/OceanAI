"""
Vector store management for knowledge base
"""
import chromadb
from chromadb.config import Settings
# Note: Using direct sentence-transformers instead of langchain wrappers
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict
import hashlib

class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize vector store with ChromaDB"""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="qa_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embeddings model
        self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Simple text splitter (can be replaced with langchain's RecursiveCharacterTextSplitter)
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to vector store
        
        Args:
            documents: List of dicts with 'content' and 'metadata' keys
        """
        all_texts = []
        all_metadatas = []
        all_ids = []
        
        for doc in documents:
            # Split document into chunks
            chunks = self._split_text(doc['content'])
            
            for i, chunk in enumerate(chunks):
                all_texts.append(chunk)
                all_metadatas.append({
                    **doc.get('metadata', {}),
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
                # Generate unique ID
                doc_id = hashlib.md5(
                    f"{doc.get('metadata', {}).get('source', 'unknown')}_{i}".encode()
                ).hexdigest()
                all_ids.append(doc_id)
        
        # Generate embeddings
        embeddings = self.embeddings_model.encode(all_texts).tolist()
        
        # Add to collection
        self.collection.add(
            ids=all_ids,
            embeddings=embeddings,
            documents=all_texts,
            metadatas=all_metadatas
        )
        
        return len(all_ids)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embeddings_model.encode([query]).tolist()[0]
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
        
        return formatted_results
    
    def clear(self):
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(name="qa_knowledge_base")
            self.collection = self.client.get_or_create_collection(
                name="qa_knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False
    
    def get_collection_count(self) -> int:
        """Get number of documents in collection"""
        return self.collection.count()
    
    def _split_text(self, text: str) -> List[str]:
        """Simple text splitter with overlap"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= text_length:
                break
        
        return chunks

