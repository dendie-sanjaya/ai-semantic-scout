import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import json

# --- Konfigurasi ---
FAISS_INDEX_FILE = "document_index.bin"
CHUNKS_FILE = "chunks.txt" 
EMBEDDER_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
#EMBEDDER_MODEL_NAME = 'BAAI/bge-large-en-v1.5'

try:
    embedder = SentenceTransformer(EMBEDDER_MODEL_NAME)
    print("Model embeddings berhasil dimuat.")
except Exception as e:
    print(f"Gagal memuat model: {e}")
    embedder = None

try:
    if not os.path.exists(FAISS_INDEX_FILE):
        print("Error: File database FAISS tidak ditemukan. Jalankan 'python etl-content.py' terlebih dahulu.")
        faiss_index = None
    else:
        faiss_index = faiss.read_index(FAISS_INDEX_FILE)
        print("Database FAISS berhasil dimuat.")
except Exception as e:
    print(f"Gagal memuat database FAISS: {e}")
    faiss_index = None

def get_chunks_by_indices(indices):
    """
    Mengambil chunks dari file CHUNKS_FILE berdasarkan indeks yang diberikan
    dan mem-parsing konten JSON.
    """
    if not os.path.exists(CHUNKS_FILE):
        print("File chunks.txt tidak ditemukan.")
        return []
    
    retrieved_chunks_meta = []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
        for i in indices:
            if 0 <= i < len(all_lines):
                try:
                    chunk_data = json.loads(all_lines[i])
                    retrieved_chunks_meta.append(chunk_data)
                except json.JSONDecodeError as e:
                    print(f"Error: Gagal membaca baris {i} dari chunks.txt sebagai JSON: {e}")
    return retrieved_chunks_meta

def find_relevant_documents(query, top_k=3):
    """
    Mencari dokumen paling relevan berdasarkan query.
    """
    if not all([embedder, faiss_index]):
        return "Layanan tidak siap. Silakan periksa log server.", []
        
    query_embedding = embedder.encode([query])
    distances, indices = faiss_index.search(np.array(query_embedding).astype('float32'), top_k)
    
    retrieved_chunks_with_meta = get_chunks_by_indices(indices[0])
    
    if not retrieved_chunks_with_meta:
        return "Maaf, tidak ada informasi relevan yang ditemukan.", []

    return "", retrieved_chunks_with_meta

if __name__ == "__main__":
    user_query = "Laporan Keuangan Kuartal 2 Tahun 2025"
    
    _, source_chunks = find_relevant_documents(user_query)
    
    print("====================================")
    print("     Hasil Pencarian Vektor Asli    ")
    print("====================================")
    if source_chunks:
        for i, chunk in enumerate(source_chunks):
            print(f"Chunk #{i+1} dari file: {chunk['sumber_file']} (Halaman: {chunk.get('halaman', 'N/A')})")
            print(f"Konten: {chunk['konten']}","...")
            print("-" * 20)
    else:
        print("Tidak ada chunks relevan yang ditemukan.")
