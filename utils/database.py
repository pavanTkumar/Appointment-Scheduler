import chromadb
import os
from dotenv import load_dotenv
from chromadb.config import Settings
from typing import List, Dict, Any
import json

class ChromaDBManager:
    def __init__(self):
        load_dotenv()
        self.db_path = os.getenv("DATABASE_PATH", "./chroma_db")
        
        # Initialize the persistent client
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(
                allow_reset=True,
                anonymized_telemetry=False
            )
        )
        
        # Create or get the collection
        self.collection = self.client.get_or_create_collection(
            name="portfolio_data",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize the database if empty
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the database with portfolio data if it's empty"""
        try:
            # Check if collection is empty
            if self.collection.count() == 0:
                self._load_initial_data()
        except Exception as e:
            print(f"Error initializing database: {e}")

    def _load_initial_data(self):
        """Load initial portfolio data into ChromaDB"""
        try:
            with open('data/portfolio_data.json', 'r') as f:
                portfolio_data = json.load(f)
            
            # Prepare data for insertion
            documents = []
            metadatas = []
            ids = []
            
            for idx, item in enumerate(portfolio_data):
                documents.append(item['content'])
                metadatas.append({
                    'type': item['type'],
                    'tags': ','.join(item.get('tags', [])),
                    'date': item.get('date', '')
                })
                ids.append(f"doc_{idx}")
            
            # Add data to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully initialized database with {len(documents)} documents")
        except Exception as e:
            print(f"Error loading initial data: {e}")

    def add_data(self, texts: List[str], metadata_list: List[Dict[str, Any]]) -> bool:
        """
        Add new data to the database
        
        Args:
            texts (List[str]): List of text documents to add
            metadata_list (List[Dict]): List of metadata dictionaries for each document
            
        Returns:
            bool: Success status
        """
        try:
            ids = [f"doc_{i}" for i in range(self.collection.count(), 
                                           self.collection.count() + len(texts))]
            
            self.collection.add(
                documents=texts,
                metadatas=metadata_list,
                ids=ids
            )
            return True
        except Exception as e:
            print(f"Error adding data: {e}")
            return False

    def search_similar(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Search for similar documents
        
        Args:
            query (str): Query text
            n_results (int): Number of results to return
            
        Returns:
            Dict: Search results with documents and metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            return {
                'documents': results['documents'][0],
                'metadata': results['metadatas'][0],
                'distances': results['distances'][0]
            }
        except Exception as e:
            print(f"Error searching database: {e}")
            return {'documents': [], 'metadata': [], 'distances': []}

    def delete_all(self) -> bool:
        """Delete all data from the collection"""
        try:
            self.client.delete_collection("portfolio_data")
            self.collection = self.client.create_collection(
                name="portfolio_data",
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False