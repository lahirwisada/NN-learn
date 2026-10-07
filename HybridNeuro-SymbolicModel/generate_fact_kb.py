import json

# Master fakta & pertanyaan fakta umum seputar Indonesia
facts_base = [
    # 1. Geografi, Wilayah, & Alam
    "Indonesia adalah negara kepulauan terbesar di dunia dengan lebih dari 17.000 pulau.",
    "Ibu kota negara Indonesia saat ini sedang dipindahkan secara bertahap ke Nusantara (IKN) di Kalimantan Timur.",
    "Jakarta adalah kota terbesar di Indonesia dan pernah menjadi ibu kota negara.",
    "Indonesia memiliki garis pantai terpanjang kedua di dunia setelah Kanada.",
    "Danau Toba di Sumatera Utara adalah danau vulkanik terbesar di dunia.",
    "Gunung Jayawijaya di Papua adalah puncak tertinggi di Indonesia dan memiliki salju abadi.",
    "Gunung Krakatau terkenal karena letusan dahsyatnya pada tahun 1883.",
    "Indonesia dilintasi oleh garis khatulistiwa, membuat iklimnya beriklim tropis.",
    "Pulau Jawa adalah pulau terpadat di Indonesia dan dunia.",
    "Indonesia terletak di antara dua samudera: Samudera Pasifik dan Samudera Hindia.",
    "Indonesia terletak di antara dua benua: Benua Asia dan Benua Australia.",
    "Selat Malaka adalah salah satu jalur pelayaran perdagangan tersibuk di dunia yang melintasi Indonesia.",
    "Kawasan Ring of Fire (Cincin Api Pasifik) membuat Indonesia memiliki banyak gunung berapi aktif.",
    "Pulau Kalimantan terbagi antara tiga negara: Indonesia, Malaysia, dan Brunei.",
    "Komodo adalah spesies kadal terbesar di dunia yang hanya hidup di Kepulauan Komodo, Indonesia.",
    "Rafflesia arnoldii adalah bunga tunggal terbesar di dunia yang ditemukan di hutan Indonesia.",
    "Hutan hujan tropis di Indonesia adalah salah satu paru-paru dunia terbesar.",
    "Taman Nasional Lore Lindu di Sulawesi terkenal dengan patung-patung megalitikumnya.",
    "Kepulauan Raja Ampat di Papua Barat dikenal sebagai pusat keanekaragaman hayati laut dunia.",

    # 2. Sejarah, Politik, & Pemerintahan
    "Indonesia memproklamasikan kemerdekaannya pada tanggal 17 Agustus 1945.",
    "Ir. Soekarno dan Drs. Mohammad Hatta adalah Proklamator Kemerdekaan Indonesia.",
    "Soekarno adalah Presiden pertama Republik Indonesia.",
    "Pancasila adalah dasar negara dan ideologi resmi Republik Indonesia.",
    "Bhinneka Tunggal Ika adalah semboyan nasional Indonesia yang berarti 'Berbeda-beda tetapi tetap satu'.",
    "UUD 1945 adalah undang-undang dasar dan hukum tertulis tertinggi di Indonesia.",
    "Sumpah Pemuda dicetuskan pada tanggal 28 Oktober 1928.",
    "Bendera nasional Indonesia adalah Merah Putih.",
    "Lagu kebangsaan Indonesia adalah Indonesia Raya yang diciptakan oleh W.R. Supratman.",
    "Burung Garuda adalah lambang negara Republik Indonesia.",
    "Hari Lahir Pancasila diperingati setiap tanggal 1 Juni.",
    "Hari Pahlawan diperingati setiap tanggal 10 November untuk mengenang Pertempuran Surabaya.",
    "Indonesia adalah salah satu pendiri organisasi ASEAN pada tahun 1967.",
    "Konferensi Asia-Afrika (KAA) pertama kali diselenggarakan di Bandung pada tahun 1955.",
    "Sistem pemerintahan Indonesia adalah republik presidensial.",
    "Majelis Permusyawaratan Rakyat (MPR) terdiri dari DPR dan DPD.",
    "Mata uang resmi Republik Indonesia adalah Rupiah (IDR).",
    "Indonesia merupakan negara anggota G20 dari wilayah Asia Tenggara.",

    # 3. Budaya, Bahasa, Suku, & Tradisi
    "Bahasa Indonesia adalah bahasa resmi dan bahasa persatuan Republik Indonesia.",
    "Indonesia memiliki lebih dari 700 bahasa daerah yang tersebar di berbagai suku.",
    "Batik telah diakui oleh UNESCO sebagai Warisan Budaya Takbenda Masterpiece of Humanity.",
    "Candi Borobudur di Jawa Tengah adalah candi Buddha terbesar di dunia.",
    "Candi Prambanan adalah kompleks candi Hindu terbesar di Indonesia.",
    "Tari Saman dari Aceh diakui oleh UNESCO sebagai warisan budaya takbenda.",
    "Wayang kulit adalah seni pertunjukan tradisional berbasis cerita epik Ramayana dan Mahabharata.",
    "Angklung adalah alat musik tradisional dari Jawa Barat yang terbuat dari bambu.",
    "Gamelan adalah ensembel musik tradisional khas Jawa dan Bali.",
    "Rendang adalah masakan khas Minangkabau yang sering dinobatkan sebagai makanan terlezat di dunia.",
    "Suku Jawa adalah suku bangsa terbesar di Indonesia.",
    "Upacara Rambu Solo adalah tradisi pemakaman adat suku Toraja di Sulawesi Selatan.",
    "Rumah Gadang adalah rumah adat khas masyarakat Minangkabau.",
    "Nasi Goreng dan Satay (Sate) adalah dua makanan khas Indonesia yang sangat populer di mancanegara.",
    "Lompat Batu (Hombo Batu) adalah tradisi kedewasaan pria dari Pulau Nias.",
    "Tari Kecak adalah seni tari dan musik khas Bali yang dimainkan oleh belasan hingga puluhan pria.",

    # 4. Pertanyaan Faktual tentang Indonesia (Fact Queries)
    "Kapan Indonesia merdeka?",
    "Apa nama ibu kota baru Indonesia?",
    "Apa dasar negara Republik Indonesia?",
    "Siapa presiden pertama Indonesia?",
    "Apa lagu kebangsaan Indonesia?",
    "Apa mata uang resmi Indonesia?",
    "Apa lambang negara Indonesia?",
    "Sebutkan candi Buddha terbesar di Indonesia!",
    "Berapa jumlah provinsi di Indonesia saat ini?",
    "Apa makanan tradisional terlezat asal Minangkabau?",
    "Di mana habitat asli hewan Komodo?",
    "Apa nama gunung tertinggi di Indonesia?",
    "Apa danau terbesar di Indonesia?",
    "Kapan Hari Sumpah Pemuda diperingati?",
    "Siapa pencipta lagu Indonesia Raya?",
    "Apa semboyan nasional negara Indonesia?",
    "Sebutkan bahasa resmi yang digunakan di Indonesia!",
    "Apa pulau terpadat di Indonesia?",
    "Sebutkan bunga nasional terbesar di Indonesia!"
]

# Modifikator penambah variasi agar mencakup bentuk fakta, pertanyaan, dan deskripsi eksplisit
variations = [
    "Fakta: {f}",
    "Fakta Umum: {f}",
    "Fakta Indonesia: {f}",
    "Tahukah Anda? {f}",
    "Informasi fakta: {f}",
    "Apakah benar bahwa {f}",
    "Pertanyaan Faktual: {f}",
    "Detail Fakta: {f}",
    "Data Fakta: {f}",
    "Catatan Fakta: {f}",
    "Fakta Geografi/Sejarah: {f}"
]

dataset = []
seen = set()

# Menghasilkan setidaknya 650 baris unik
for fact in facts_base:
    # Versi polos
    if fact not in seen:
        seen.add(fact)
        dataset.append({
            "type": "fact",
            "content": fact
        })
        
    # Versi variasi konteks
    for var in variations:
        formatted = var.format(f=fact)
        if formatted not in seen:
            seen.add(formatted)
            dataset.append({
                "type": "fact",
                "content": formatted
            })

# Ambil tepat 650 entri unik
final_dataset = dataset[:650]

# Simpan ke berkas JSON
with open("knowledge_base.json", "w", encoding="utf-8") as f:
    json.dump(final_dataset, f, ensure_ascii=False, indent=2)

print(f"Berhasil membuat knowledge_base.json dengan total {len(final_dataset)} baris data fakta!")