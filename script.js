document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('.form-prediksi');

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const tugas = parseFloat(document.getElementById("tugas").value);
        const uts = parseFloat(document.getElementById("uts").value);
        const uas = parseFloat(document.getElementById("uas").value);
        const kehadiran = parseFloat(document.getElementById("kehadiran").value);
        const hasil = document.getElementById('hasil-prediksi');

        if (isNaN(tugas) || isNaN(uts) || isNaN(uas) || isNaN(kehadiran)) {
            hasil.innerHTML = `<p style="color:red;">Mohon isi semua nilai dengan angka yang valid.</p>`;
            return;
        }

        const data = { tugas, uts, uas, kehadiran };

        fetch("http://127.0.0.1:5000/prediksi", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) throw new Error("Gagal menghubungi server.");
            return response.json();
        })
        .then(res => {
            if (typeof res.prediksi_nilai === "number") {
                const nilai = res.prediksi_nilai.toFixed(2);
                const status = res.prediksi_nilai >= 60 ? "✅ Lulus" : "❌ Tidak Lulus";
                const confidence = typeof res.confidence_score === "number" 
                    ? res.confidence_score.toFixed(2) + "%" 
                    : "Tidak tersedia";

                hasil.innerHTML = `
                    <p><strong>Prediksi Nilai:</strong> ${nilai}</p>
                    <p><strong>Status:</strong> ${status}</p>
                    <p><strong>Tingkat Keyakinan Model:</strong> ${confidence}</p>
                `;
            } else {
                hasil.innerHTML = `<p style="color:red;">Terjadi kesalahan saat memproses data.</p>`;
            }
        })
        .catch(error => {
            hasil.innerHTML = `<p style="color:red;">Koneksi ke server gagal: ${error.message}</p>`;
        });
    });
});
