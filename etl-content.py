import fitz
import faiss
import numpy as np
import os
import glob
import json
import re
from sentence_transformers import SentenceTransformer

# --- Konfigurasi & Persiapan ---
PDF_FOLDER = "documents" 
LOGS_DIR = "logs"
FAISS_INDEX_FILE = "document_index.bin"
CHUNKS_FILE = "chunks.txt"
EMBEDDER_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2' 

# --- Definisi Fungsi Ekstraksi PDF ---
def extract_text_from_pdf(pdf_path):
    """
    Mengekstrak teks dari file PDF, mengembalikan daftar teks per halaman.
    """
    try:
        doc = fitz.open(pdf_path)
        pages = []
        for i, page in enumerate(doc):
            pages.append(page.get_text())
        return pages
    except fitz.FileDataError as e:
        print(f"Error: File PDF rusak atau tidak dapat diakses: {e}")
        return []
    except Exception as e:
        print(f"Error tidak terduga saat mengekstrak PDF {pdf_path}: {e}")
        return []

# --- Definisi Fungsi Pra-pemrosesan Teks ---
def preprocess_text(text):
    """
    Membersihkan teks dari karakter dan pola yang tidak relevan.
    """
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'(\d+)\.\s+(\d+)', r'\1.\2', text)
    unwanted_patterns = [
        r'^\s*Catatan:\s*Peningkatan pendapatan.*',
        r'^\s*000\s*$',
        r'^\s*\d+\s*$',
        r'^\s*\.\s*$'
    ]
    for pattern in unwanted_patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)
    return text

# --- Definisi Fungsi Chunking Teks ---
def chunk_text(text, source_file, page_number, chunk_size=15):
    """
    Membagi teks menjadi chunks berdasarkan jumlah kata, dan menambahkan nomor halaman.
    """
    if not text:
        return []
    
    cleaned_text = preprocess_text(text)
    words = cleaned_text.split()
    
    chunks_with_meta = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk) > 10: # Filter chunks yang terlalu pendek
            chunks_with_meta.append({
                "sumber_file": source_file,
                "konten": chunk,
                "halaman": page_number
            })
    return chunks_with_meta

# --- Fungsi Utama ETL Pipeline ---
def run_etl_pipeline():
    """Menjalankan seluruh pipeline ETL."""
    if not os.path.exists(PDF_FOLDER):
        print(f"Folder '{PDF_FOLDER}' tidak ditemukan.")
        return
        
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    print("Memuat model SentenceTransformer...")
    embedder = SentenceTransformer(EMBEDDER_MODEL_NAME)
    
    if os.path.exists(FAISS_INDEX_FILE):
        print("Memuat indeks FAISS yang sudah ada...")
        faiss_index = faiss.read_index(FAISS_INDEX_FILE)
    else:
        print("Membuat indeks FAISS baru...")
        dimension = embedder.get_sentence_embedding_dimension()
        faiss_index = faiss.IndexFlatL2(dimension)
    
    if os.path.exists(CHUNKS_FILE):
        os.remove(CHUNKS_FILE)

    with open(CHUNKS_FILE, "a", encoding="utf-8") as chunks_file:
        for pdf_path in glob.glob(os.path.join(PDF_FOLDER, "*.pdf")):
            print(f"Memproses file: {pdf_path}")
            
            file_name = os.path.basename(pdf_path)
            # Dapatkan teks per halaman sebagai daftar
            pages_text = extract_text_from_pdf(pdf_path)
            if not pages_text:
                continue

            for page_num, page_content in enumerate(pages_text, 1):
                chunks_with_meta = chunk_text(page_content, file_name, page_num, chunk_size=15)
                if not chunks_with_meta:
                    continue

                chunk_contents = [chunk['konten'] for chunk in chunks_with_meta]
                embeddings = embedder.encode(chunk_contents)
                
                faiss_index.add(np.array(embeddings).astype('float32'))
                
                for chunk in chunks_with_meta:
                    chunks_file.write(json.dumps(chunk) + "\n")

                log_filename = os.path.splitext(file_name)[0] + ".txt"
                log_path = os.path.join(LOGS_DIR, log_filename)
                with open(log_path, "w", encoding="utf-8") as log_file:
                    log_file.write("\n".join(chunk_contents))
                print(f"Chunks berhasil disimpan sebagai log di {log_path}")
            
    faiss.write_index(faiss_index, FAISS_INDEX_FILE)
    print("Proses ETL selesai. Indeks FAISS dan chunks berhasil diperbarui.")

if __name__ == "__main__":
    run_etl_pipeline()
