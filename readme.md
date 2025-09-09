# AI Semantic Scout

AI Semantic Scout is an intelligent file search program that uses artificial intelligence to find documents based on their semantic meaning, not just keywords. 
This modular architecture is designed for efficient data processing and accurate search results.

## Table of Contents

1. System Architecture
   - ETL Pipeline (Extract, Transform, Load)
   - Search API
2. Simple Workflow
3. Visualizing the Workflow
4. Search Results

## System Architecture

The system is divided into two main parts:

1. ETL (Extract, Transform, Load)
2. Search API

### ETL Pipeline (Extract, Transform, Load)

This part is responsible for transforming raw documents into searchable data. The process includes:

#### Extract

- `extract_content_document.py` extracts text from various PDF files in the `Storage Document` folder.
- Text is extracted page-by-page and prepared for transformation.

#### Transform

- The extracted text is processed using the AI Embedding Vector Model: `sentence-transformers/all-MiniLM-L6-v2`.
- Text is converted into embeddings (numerical vectors) representing semantic meaning.
- Vectors are stored in `chunks.txt` and `document_index.bin` for fast searching.
- Logs are saved in the `Log ETL` folder.

#### Load

- Vectors are loaded into a Vector Database built with FAISS (Facebook AI Similarity Search).
- This enables high-speed similarity search for user queries.

### Search API

This is the interface for external applications to interact with the search system.

#### API Interface (app.py)

- Accepts REST JSON requests from client applications.

#### Search Module (find.py)

- Converts the user’s query into a vector using the same embedding model.
- Searches the FAISS Vector Database for similar vectors.

#### Output

- Returns the file name and location of the most relevant documents.

## Simple Workflow

1. Place your PDF documents into the `documents/` folder.
2. Run the ETL pipeline to convert the text into semantic vectors.
3. Vectors are saved and indexed by FAISS.
4. An external app sends a query (e.g., "financial report for 2023").
5. The API converts the query into a vector.
6. The system finds the most similar document vectors.
7. The system returns the file name and location of the most relevant files.

## Visualizing the Workflow

### Downloading Models and Indexing Data

- Downloads the AI model from Hugging Face.
- Indexes documents into the FAISS vector database.

### Running the ETL Pipeline

- Each PDF is split into chunks.
- Logs are generated.
- Chunks are indexed and stored.

### Running the API Server

- The API server runs and waits for external search requests.

### Performing a Semantic Search

- Use tools like Postman to send a search query.
- The system processes and returns matching results.

## Search Results

Results are returned in a structured JSON format like below:

```json
{
  "konten": "Summary of the 2023 financial report...",
  "halaman": 3,
  "sumber_file": "financial_report_2023.pdf"
}
