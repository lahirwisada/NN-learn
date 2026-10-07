import torch
from model import HealthClassifier
from data import DIAGNOSIS_MAP, GEJALA_MAP

def load_model():
    """Memuat model dari file .pth"""
    model = HealthClassifier()
    try:
        # map_location='cpu' memastikan ini jalan di CPU meski file dibuat di GPU (opsional)
        model.load_state_dict(torch.load("model_bayi_sehat.pth", map_location=torch.device('cpu')))
        model.eval()
        print("✅ Model berhasil dimuat dan siap mendiagnosa!")
        return model
    except FileNotFoundError:
        print("❌ Error: File 'model_bayi_sehat.pth' tidak ditemukan.")
        print("   Jalankan 'python main.py' terlebih dahulu untuk membuat modelnya.")
        return None

def get_user_input():
    """Meminta input gejala dari user"""
    print("\n--- Masukkan Gejala (pisahkan dengan koma) ---")
    print("Daftar Kode Gejala:")
    for name, code in GEJALA_MAP.items():
        print(f"  {code}: {name}")
    
    try:
        raw_input = input("\nKetik kode gejala (contoh: 1,4,10): ")
        # Ubah string "1,4,10" menjadi list of integers [1, 4, 10]
        gejala_list = [int(x.strip()) for x in raw_input.split(",")]
        return gejala_list
    except ValueError:
        print("⚠️ Input tidak valid. Pastikan hanya memasukkan angka.")
        return []

def predict(model, gejala_list):
    """Melakukan prediksi"""
    if not gejala_list:
        return "Tidak ada input", 0.0

    vec = [0.0] * 19
    for g in gejala_list:
        if 1 <= g <= 19:
            vec[g - 1] = 1.0
    
    with torch.no_grad():
        tensor_input = torch.tensor([vec], dtype=torch.float32)
        output = model(tensor_input)
        predicted_idx = torch.argmax(output, dim=1).item()
        confidence = torch.softmax(output, dim=1)[0][predicted_idx].item()
    
    return DIAGNOSIS_MAP.get(predicted_idx, "Unknown"), confidence

if __name__ == "__main__":
    model = load_model()
    
    if model:
        while True:
            gejala = get_user_input()
            if not gejala:
                continue
                
            diagnosis, conf = predict(model, gejala)
            
            print("\n----------------------------------------")
            print(f"🩺 HASIL DIAGNOSA: {diagnosis.upper()}")
            print(f"📊 Tingkat Keyakinan: {conf:.2%}")
            print("----------------------------------------")
            
            lagi = input("\nCoba lagi? (y/n): ").lower()
            if lagi != 'y':
                print("👋 Terima kasih, jaga kesehatan!")
                break