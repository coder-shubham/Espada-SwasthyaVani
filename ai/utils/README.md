# `utils` Folder

This folder contains various utility modules and helper classes used across the AI service. Each module provides specific functionalities to streamline development and maintain code modularity.

## Contents

* **`vectorstores/`**: This subfolder houses modules for interacting with different vector databases.
    * **`weav8.py`**: Contains the `WeaviateCollectionClient` class, which provides an abstraction layer for interacting with Weaviate collections. It includes functionalities for:
        * Initializing and loading Weaviate collections.
        * Inserting data (properties and vectors) into collections.
        * Performing different types of queries:
            * `query_bm25`: Keyword-based search using BM25 algorithm.
            * `query_vector`: Semantic search using vector embeddings.
            * `query`: Hybrid search combining keyword and semantic approaches.
        * Deleting collections and objects within collections based on properties or IDs.
        * Helper methods for processing query responses and extracting relevant information.

## Usage

For detailed usage of the `WeaviateCollectionClient`, please refer to the module's docstrings and the example provided in the `if __name__ == '__main__':` block within the `weav8.py` file. This example demonstrates basic operations like:

* Connecting to a local Weaviate instance.
* Initializing a `WeaviateCollectionClient`.
* Inserting sample data with text and their corresponding embeddings.
* Performing hybrid queries in Hindi, Marathi, and Telugu to test multilingual search capabilities.
* Deleting the created collection.
