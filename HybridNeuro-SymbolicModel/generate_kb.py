import json

# Master data percakapan seputar topik kabar
# Format: (type, input_pola, jawaban_ai)
raw_interactions = [
    # --- Kelompok 1: Pengguna Menanyakan Kabar (Pertanyaan Netral/Santai) ---
    ("qa", "apa kabar", "Kabarku baik! Kamu sendiri bagaimana kabarnya hari ini?"),
    ("qa", "apa kabar?", "Kabarku baik! Bagaimana denganmu?"),
    ("qa", "pakabar", "Baik! Semoga kamu juga dalam keadaan sehat ya."),
    ("qa", "pakabar nih", "Semua berjalan lancar di sini. Kamu gimana kabarnya?"),
    ("qa", "gimana kabar", "Kabar baik! Ada cerita menarik apa hari ini?"),
    ("qa", "gimana kabarnya", "Alhamdulillah baik. Semoga harimu juga menyenangkan!"),
    ("qa", "gimana kabar nih", "Kabar baik! Semoga kamu juga sehat dan bahagia selalu."),
    ("qa", "gimana-gimana", "Semua aman dan lancar! Kamu sendiri gimana kondisinya?"),
    ("qa", "gimana harimu", "Hariku berjalan lumayan seru! Harimu gimana?"),
    ("qa", "gimana harimu hari ini", "Lancar dan menyenangkan! Semoga harimu juga begitu ya."),
    ("qa", "kabar gimana", "Kabar baik kok! Kamu lagi sibuk apa hari ini?"),
    ("qa", "piye kabare", "Kabare becik! (Kabarku baik!). Kamu gimana kabarnya?"),
    ("qa", "kabar baik?", "Kabar baik banget! Kamu sendiri gimana?"),
    ("qa", "sehat?", "Sehat selalu! Kamu gimana, sehat juga kan?"),
    ("qa", "sehat bro", "Sehat dong! Kamu gimana kabarnya bro?"),
    ("qa", "sehat sis", "Sehat selalu! Kamu gimana kabarnya sis?"),
    ("qa", "lagi sehat gak", "Sehat dan siap nemenin kamu obrol! Kamu sehat?"),
    ("qa", "ada kabar apa hari ini", "Tidak ada hal buruk, semua lancar! Kalau kamu ada kabar menarik apa?"),

    # --- Kelompok 2: Pengguna Menyampaikan Kabar Baik ---
    ("qa", "baik", "Senang mendengarnya! Ada yang bisa aku bantu hari ini?"),
    ("qa", "baik-baik saja", "Syukurlah kalau begitu. Semoga harimu terus menyenangkan ya!"),
    ("qa", "baik kok", "Alhamdulillah. Ada cerita seru apa hari ini?"),
    ("qa", "baik, kamu gimana", "Aku juga baik-baik saja! Terima kasih sudah menanyakan kembali."),
    ("qa", "kabar baik", "Mantap! Semoga semangatmu terus terjaga sepanjang hari."),
    ("qa", "sehat walafiat", "Alhamdulillah, senang banget dengarnya! Jaga kesehatan terus ya."),
    ("qa", "lagi bahagia banget hari ini", "Wah, ikut senang mendengarnya! Cerita dong ada kabar bahagia apa?"),
    ("qa", "semua lancar", "Keren! Semoga semua urusanmu berikutnya tetap berjalan mulus ya."),
    ("qa", "luar biasa", "Luar biasa! Energi positifmu terasa sampai sini."),

    # --- Kelompok 3: Pengguna Menyampaikan Kabar Netral / Biasa Saja ---
    ("qa", "ya begini-begini aja", "Yang penting tetap stabil dan sehat ya. Ada yang mau diceritakan?"),
    ("qa", "ya begini-begini aja, tidak berubah banyak", "Kadang rutinitas yang tenang itu juga sebuah berkah. Semoga harimu tetap menyenangkan!"),
    ("qa", "biasa aja", "Tetap jalani dengan santai ya. Kalau bosan, kita bisa ngobrolin topik seru!"),
    ("qa", "lumayan", "Lumayan bagus dong! Ada hal menarik yang terjadi hari ini?"),
    ("qa", "flat aja hari ini", "Gak apa-apa, hari yang tenang juga butuh sesekali. Mau coba bahas sesuatu?"),
    ("qa", "ya begitu deh", "Tetap semangat ya! Kalau ada ganjalan, mau cerita-cerita?"),
    ("qa", "standar aja", "Yang penting semua aman terendali ya."),

    # --- Kelompok 4: Pengguna Menyampaikan Kabar Kurang Baik / Sedih / Lelah ---
    ("qa", "lumayan, aga kurang sehat nih", "Wah, jaga kesehatan ya! Jangan lupa minum air hangat dan istirahat yang cukup."),
    ("qa", "lagi kurang sehat", "Duh, semoga cepat sembuh ya! Istirahat dulu dan jangan terlalu memaksakan diri."),
    ("qa", "lagi sakit nih", "Lekas sembuh ya! Coba minum obat dan istirahat total dulu."),
    ("qa", "lagi tidak baik-baik saja", "Turut prihatin mendengarnya. Mau cerita ada masalah apa? Aku di sini siap mendengarkan."),
    ("qa", "lagi sedih", "Semoga perasaannmu segera membaik ya. Kalau butuh teman cerita, aku di sini."),
    ("qa", "capek banget hari ini", "Istirahat sejenak ya. Rehatkan pikiran dan selonjorkan kaki dulu."),
    ("qa", "lagi stres", "Coba tarik napas dalam-dalam dulu... Jangan lupa istirahat sejenak ya."),
    ("qa", "buruk banget hari ini", "Maaf ya kamu harus melewati hari yang berat. Semoga besok jauh lebih baik."),
    ("qa", "lagi pusing nih", "Jangan lupa minum air putih dan istirahatkan matamu dari layar sejenak ya."),

    # --- Kelompok 5: Basa-basi & Tindak Lanjut Tanya Kabar ---
    ("qa", "lama gak dengar kabar", "Iya nih! Senang bisa ngobrol bareng kamu lagi. Kamu gimana kabarnya?"),
    ("qa", "long time no see, gimana kabar", "Senang berjumpa lagi! Kabarku baik, kamu sendiri gimana?"),
    ("qa", "gimana keadaan keluarga", "Semoga keluarga di rumah selalu sehat dan dilindungi ya!"),
    ("qa", "gimana pekerjaanmu", "Semua berjalan lancar! Gimana dengan kesibukanmu sendiri?"),
    ("qa", "gimana sekolah/kuliah", "Semoga tugas-tugas dan ujianmu berjalan lancar ya! Tetap semangat!"),
    ("qa", "gimana bisnis kamu", "Semoga makin lancar dan sukses selalu ya usahamu!")
]

# Modifikator Awalan & Akhiran untuk menghasilkan variasi realistis
prefixes = ["", "halo, ", "hai, ", "eh, ", "permisi, ", "bro, ", "sis, ", "gan, ", "oi, "]
suffixes = ["", " nih", " dong", " ya", " sekarang", " hari ini", "?", "!!", " :)"]

dataset = []
seen = set()

# Generasi dataset hingga lebih dari 500 baris unik
for item_type, q_base, a_base in raw_interactions:
    for pref in prefixes:
        for suff in suffixes:
            # Konstruksi pertanyaan dengan variasi
            q_var = f"{pref}{q_base}{suff}".strip()
            
            # Normalisasi spasi dan kapitalisasi sederhana
            q_var = " ".join(q_var.split())
            if not q_var.endswith("?") and not q_var.endswith("!") and not q_var.endswith(":)"):
                # Tambahkan tanda baca opsional secara variatif
                pass

            pair_key = (q_var.lower(), a_base)
            if pair_key not in seen:
                seen.add(pair_key)
                dataset.append({
                    "type": item_type,
                    "question": q_var,
                    "answer": a_base
                })

# Ambil tepat 550 entri unik
final_dataset = dataset[:550]

# Simpan ke berkas JSON
with open("knowledge_base.json", "w", encoding="utf-8") as f:
    json.dump(final_dataset, f, ensure_ascii=False, indent=2)

print(f"Berhasil membuat knowledge_base.json dengan total {len(final_dataset)} baris data!")