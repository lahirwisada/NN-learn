import torch

# Mapping variabel input (Gejala)
GEJALA_MAP = {
    "kepala": 1, "sakit": 2, "memar": 3, "pusing": 4, "sebagian": 5,
    "seluruhnya": 6, "luka": 7, "tergores": 8, "nyeri": 9, "berkunangKunang": 10,
    "berat": 11, "lemas": 12, "perut": 13, "kanan": 14, "kiri": 15,
    "depan": 16, "belakang": 17, "melilit": 18, "panas": 19
}

# Mapping variabel output (Diagnosis)
DIAGNOSIS_MAP = {
    0: "pusingBiasa", 1: "migrain", 2: "iritasi", 3: "cidera", 4: "vertigo",
    5: "tekananDarahNaikAtauTurun", 6: "hanyaLapar", 7: "sangatLapar", 
    8: "gerd", 9: "tidakTerdeksiTanyaDokter"
}

def get_training_data():
    """
    Mengembalikan tensor X (input) dan y (target) yang siap dipakai training.
    Format input: One-hot atau value-based untuk 19 slot gejala.
    """
    # Contoh data latih (bisa ditambah ratusan baris lagi)
    raw_data = [
        {"gejala": [1, 4], "diagnosis": 0},          # Kepala + Pusing -> Pusing Biasa
        {"gejala": [1, 4, 9, 10, 11], "diagnosis": 1}, # Kepala + Pusing + Nyeri + Berkunang + Berat -> Migrain
        {"gejala": [3, 7, 8], "diagnosis": 3},        # Memar + Luka + Tergores -> Cidera
        {"gejala": [13, 18, 19], "diagnosis": 8},     # Perut + Melilit + Panas -> GERD
        {"gejala": [1, 4, 10, 12], "diagnosis": 4},   # Kepala + Pusing + Berkunang + Lemas -> Vertigo
        {"gejala": [13, 2], "diagnosis": 6},          # Perut + Sakit -> Hanya Lapar
    ]
    
    X_list = []
    y_list = []
    
    for item in raw_data:
        # Buat vektor input berukuran 19 (sesuai jumlah gejala)
        vec = [0.0] * 19
        for g in item["gejala"]:
            if 1 <= g <= 19:
                vec[g - 1] = 1.0  # Set posisi gejala menjadi 1.0
        
        X_list.append(vec)
        y_list.append(item["diagnosis"])
    
    return torch.tensor(X_list, dtype=torch.float32), torch.tensor(y_list, dtype=torch.long)