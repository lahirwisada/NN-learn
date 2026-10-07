import torch
import torch.optim as optim
import torch.nn as nn
from data import get_training_data, DIAGNOSIS_MAP
from model import HealthClassifier

def train():
    print("🚀 Memulai proses training model...")
    
    # 1. Load data dari file data.py
    X_train, y_train = get_training_data()
    
    # 2. Inisialisasi Model
    model = HealthClassifier()
    total_params = HealthClassifier.count_parameters(model)
    print(f"✅ Struktur model siap dengan {total_params} parameter.")
    
    # 3. Setup Training (Optimasi untuk CPU)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01) 
    
    # 4. Loop Training
    model.train()
    epochs = 1000
    for epoch in range(epochs):
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        
        optimizer.zero_grad() # Bersihkan gradien lama
        loss.backward()       # Hitung arah perbaikan
        optimizer.step()      # Update parameter (angka-angka)
        
        # Tampilkan progress setiap 200 epoch
        if (epoch + 1) % 200 == 0:
            print(f"   Epoch [{epoch+1}/{epochs}] | Loss: {loss.item():.4f}")

    # 5. Simpan Hasil Training ke File .pth
    save_path = "model_bayi_sehat.pth"
    torch.save(model.state_dict(), save_path)
    print(f"\n💾 Sukses! Model telah disimpan sebagai '{save_path}'")
    print(f"   Ukuran file sangat kecil (sekitar 1-2 KB), aman untuk CPU/RAM.")
    
    return model

def predict(model, gejala_list):
    """Fungsi untuk melakukan prediksi menggunakan model yang sudah dilatih"""
    model.eval() # Mode evaluasi (mematikan fitur training agar lebih cepat)
    
    # Siapkan input vektor (19 slot)
    vec = [0.0] * 19
    for g in gejala_list:
        if 1 <= g <= 19:
            vec[g - 1] = 1.0
    
    with torch.no_grad(): # Hemat memori RAM karena tidak perlu simpan history
        tensor_input = torch.tensor([vec], dtype=torch.float32)
        output = model(tensor_input)
        
        # Cari diagnosis dengan nilai tertinggi
        predicted_idx = torch.argmax(output, dim=1).item()
        confidence = torch.softmax(output, dim=1)[0][predicted_idx].item()
    
    return DIAGNOSIS_MAP.get(predicted_idx, "Unknown"), confidence

if __name__ == "__main__":
    # Jalankan training dan dapatkan modelnya
    trained_model = train()
    
    print("\n--- 🔍 Uji Coba Prediksi (Testing) ---")
    
    # Daftar kasus uji
    test_cases = [
        ([1, 4], "Kepala + Pusing"),
        ([13, 18, 19], "Perut + Melilit + Panas"),
        ([3, 7], "Memar + Luka"),
        ([1, 4, 10, 12], "Kepala + Pusing + Berkunang + Lemas"),
        ([13, 2], "Perut + Sakit")
    ]
    
    for gejala, deskripsi in test_cases:
        diagnosis, conf = predict(trained_model, gejala)
        print(f"  Input : {deskripsi:35s}")
        print(f"  Hasil : {diagnosis:30s} (Keyakinan: {conf:.2%})\n")