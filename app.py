from flask import Flask, request, jsonify
from find import find_relevant_documents
from flask_cors import CORS # Memungkinkan permintaan dari frontend

app = Flask(__name__)
CORS(app) # Mengaktifkan CORS untuk API

@app.route("/ask", methods=["POST"])
def ask():
    """
    Endpoint untuk menerima pertanyaan dan mengembalikan jawaban.
    """
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query tidak ditemukan di body permintaan."}), 400

    #print(f"Menerima pertanyaan: {query}")
    
    # Memanggil fungsi yang sudah diperbarui dari main.py
    _, source_chunks = find_relevant_documents(query)
    
    # Memformat hasil pencarian
    response_chunks = []
    if source_chunks:
        for chunk in source_chunks:
            response_chunks.append({
                "sumber_file": chunk.get("sumber_file"),
                "halaman": chunk.get("halaman"),
                "konten": chunk.get("konten")
            })
    
    response = {
        "query": query,
        "answer": "Berikut adalah potongan dokumen yang relevan.",
        "sources": response_chunks
    }
    
    return jsonify(response)

@app.route("/", methods=["GET"])
def home():
    """
    Endpoint halaman utama.
    """
    return "API berjalan. Gunakan endpoint /ask untuk mengirim pertanyaan."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
