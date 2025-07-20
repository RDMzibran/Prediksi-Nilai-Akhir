from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import webbrowser
import threading
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Fungsi prediksi manual
def prediksi_manual(kehadiran, tugas, uts, uas):
    return round(
        0.10 * kehadiran +
        0.20 * tugas +
        0.35 * uts +
        0.35 * uas,
        2
    )

# Endpoint root langsung mengarahkan ke prediksi.html
@app.route("/")
def index():
    return send_from_directory(".", "prediksi.html")

# Endpoint prediksi POST
@app.route("/prediksi", methods=["POST"])
def prediksi():
    try:
        data = request.get_json()

        kehadiran = float(data.get("kehadiran", 0))
        tugas = float(data.get("tugas", 0))
        uts = float(data.get("uts", 0))
        uas = float(data.get("uas", 0))

        # Skala 0–1 ke 100 jika perlu
        if all(n <= 1 for n in [kehadiran, tugas, uts, uas]):
            kehadiran *= 100
            tugas *= 100
            uts *= 100
            uas *= 100

        hasil = prediksi_manual(kehadiran, tugas, uts, uas)

        # Penentuan status kelulusan
        if hasil < 55:
            status = "LULUS" if (tugas >= 70 and uts >= 70 and uas >= 70) else "TIDAK LULUS"
        else:
            status = "LULUS"

        # Load dataset untuk confidence
        dataset_path = "yg mau dipake.csv"
        if not os.path.exists(dataset_path):
            raise FileNotFoundError("Dataset tidak ditemukan!")

        dataset = pd.read_csv(dataset_path)
        fitur_dataset = dataset[["Kehadiran", "Nilai_Tugas", "Nilai_UTS", "UAS"]].apply(pd.to_numeric, errors="coerce").dropna()

        fitur_input = pd.DataFrame([{
            "Kehadiran": kehadiran,
            "Nilai_Tugas": tugas,
            "Nilai_UTS": uts,
            "UAS": uas
        }])

        mean = fitur_dataset.mean()
        std = fitur_dataset.std()
        fitur_norm = (fitur_input - mean) / std
        dataset_norm = (fitur_dataset - mean) / std

        jarak = np.linalg.norm(dataset_norm.to_numpy() - fitur_norm.to_numpy(), axis=1)
        min_jarak = np.min(jarak)

        confidence_score = max(70, min(95, 100 - min_jarak * 15))

        return jsonify({
            "prediksi_nilai": round(hasil, 2),
            "confidence_score": round(confidence_score, 2),
            "status": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Otomatis buka browser
def open_browser():
    import socket
    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)
    webbrowser.open_new(f"http://{ip_local}:5000")

# Run Flask
if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
