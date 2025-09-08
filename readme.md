AI Semantic Scout

AI Semantic Scout is an intelligent file search program that uses artificial intelligence to find documents based on their semantic meaning, not just keywords. This modular architecture is designed for efficient data processing and accurate search.
System Architecture

The system is divided into two main parts: ETL (Extract, Transform, Load) and the Search API.
1. ETL Pipeline (Extract, Transform, Load)

This part is responsible for transforming raw documents into searchable data. The process is done in three steps:

    Extract:
    The extract_content_document.py module extracts text from various PDF files stored in the Storage Document folder. Text from each page is extracted and prepared for the next step.

    Transform:
    The extracted text is then processed by the AI Embedding Vector Model (using sentence-transformers/all-MiniLM-L6-v2). This model converts the text into numerical vectors (embeddings) that represent its semantic meaning. These vectors are then saved in chunks.txt and document_index.bin for fast searching. Logs of each extraction process are also saved in the Log ETL folder for reference.

    Load:
    The created vectors are loaded into a Vector Database (document_index.bin) built with FAISS, a library for efficient similarity search. This allows the system to quickly find the vectors most similar to a user's query.

2. Search API

This part is the interface that allows external applications to interact with the search system.

    API Interface (app.py):
    The system receives search queries from external applications through a REST JSON API.

    Search Module (find.py):
    The user's query is processed by find.py. This query is transformed into a vector using the same embedding model. This query vector is then searched in the Vector Database (FAISS) to find the most similar vectors.

    Output:
    The search results display the most relevant file location and name, allowing users to instantly find the information they need.

Simple Workflow

    You place PDF documents into the documents folder.

    The ETL pipeline runs, converting the text in each document into vectors.

    These vectors are saved and indexed by FAISS.

    An external application sends a query (e.g., "financial report for 2023").

    The API converts the query into a vector.

    The system searches for the query vector in the database, finding the most similar document vectors.

    The system returns the name and location of the most relevant files.

This architecture ensures AI Semantic Scout can handle large document collections with very fast and accurate search performance.
Visualizing the Workflow

Here is a visual overview of the AI Semantic Scout workflow from start to finish.
1. Downloading Models and Indexing Data

The process begins by downloading the AI model from Hugging Face and indexing your documents.
2. Running the ETL Pipeline

Once the model is ready, the program processes each PDF file, converts it into chunks, and saves it as a log while adding it to the index.
3. Running the API Server

The API server will start running and wait for search requests from external applications.
4. Performing a Semantic Search

You can use an application like Postman to send a search request. The query will be processed, and the server will return the most relevant files.
5. Search Results

The search results are displayed in an easy-to-read JSON format, containing the relevant text snippet (konten), page (halaman), and source file name (sumber_file) for your query.