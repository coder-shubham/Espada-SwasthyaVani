# `utils` Folder

This folder contains various utility modules and helper classes used across the AI service. Each module provides specific functionalities to streamline development and maintain code modularity.

## Contents

* **`llms/`**: This subfolder contains modules for interacting with different Language Model (LLM) providers.
    * **`ollama/`**: This subfolder contains modules for interacting with the Ollama local LLM server.
        * **`llama.py`**: Contains the `OllamaLlama3Client` class, which provides an interface for interacting with the Llama 3 model served by Ollama. It includes functionalities for:
            * Initializing the client with a specified model name (defaulting to "llama3.1:8b"), temperature, and maximum tokens.
            * Creating message dictionaries in the format expected by the Ollama API.
            * Generating a single response based on a list of messages.
            * Handling potential errors from the Ollama API or unexpected response formats.
            * Streaming responses from the Ollama API.
        * **Usage:**
            To use the `OllamaLlama3Client`, ensure you have Ollama installed and the desired model (e.g., `llama3.1:8b`) downloaded and running. You can download the Llama 3.1 model by running `ollama run llama3.1:8b` in your terminal. The `if __name__ == '__main__':` block in `llama.py` provides a basic example of how to initialize the client, create messages, and generate a response.

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