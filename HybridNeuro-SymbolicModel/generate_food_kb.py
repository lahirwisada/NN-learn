import json

# Master data fakta kuliner Indonesia (masakan, jajanan, minuman, bumbu, & budaya)
food_facts_base = [
    # 1. Masakan Utama & Lauk
    "Rendang adalah masakan olahan daging sapi asal Minangkabau yang menggunakan rempah-rempah dan santan, dimasak dalam waktu lama.",
    "Rendang pernah dinobatkan sebagai salah satu makanan terlezat di dunia versi CNN International.",
    "Nasi Goreng Indonesia khas dengan penggunaan kecap manis dan sering disajikan bersama telur ceplok dan kerupuk.",
    "Sate Padang menggunakan kuah kental berbahan dasar tepung beras yang dicampur kaldu dan rempah-rempah khas.",
    "Sate Madura umumnya disajikan dengan bumbu kacang yang gurih dan manis serta irisan bawang merah.",
    "Gudeg adalah makanan khas Yogyakarta yang terbuat dari nangka muda yang dimasak dengan santan dan gula jawa.",
    "Pempek adalah makanan khas Palembang yang terbuat dari olahan daging ikan dan tepung sagu, disajikan dengan kuah cuko yang asam manis pedas.",
    "Ayam Taliwang merupakan kuliner khas Sumbawa Barat, Nusa Tenggara Barat yang terkenal dengan rasa pedas gurihnya.",
    "Soto Lamongan memiliki ciri khas penggunaan koya, yaitu bubuk kerupuk udang dan bawang putih goreng.",
    "Coto Makassar adalah sup tradisonal khas Sulawesi Selatan yang menggunakan rempah-rempah khusus dan jeroan atau daging sapi.",
    "Rawon adalah sup daging sapi hitam khas Jawa Timur yang menggunakan bumbu utama kluwek.",
    "Nasi Liwet Solo dimasak dengan santan dan kaldu ayam, disajikan dengan suwiran ayam, labu siam, dan areh.",
    "Ayam Betutu adalah masakan khas Bali berupa ayam utuh yang diisi bumbu rempah lalu dipanggang atau dikukus dalam waktu lama.",
    "Soto Betawi identik dengan kuah gurih beraroma rempah yang memadukan santan dan susu sapi.",
    "Papeda adalah makanan pokok khas Maluku dan Papua yang terbuat dari sagu bertekstur kenyal, biasa disantap dengan kuah kuning.",
    "Tinutuan atau Bubur Manado adalah bubur khas Sulawesi Utara yang kaya akan sayuran seperti kangkung, bayam, jagung, dan labu kuning.",
    "Nasi Uduk adalah hidangan khas Betawi yang dimasak menggunakan santan, daun salam, serai, dan kayu manis.",
    "Soto Banjar dari Kalimantan Selatan menggunakan rempah-rempah manis seperti kayu manis, cengkeh, dan kapulaga dalam kuahnya.",
    "Nasi Padang disajikan dengan sistem 'hidang', di mana belasan piring kecil berisi aneka lauk ditaruh langsung di atas meja.",
    "Babi Guling adalah kuliner khas Bali yang menggunakan bumbu basa genep dan dipanggang secara utuh.",

    # 2. Jajanan Tradisional & Kue Basah
    "Kue Lupis terbuat dari beras ketan yang disajikan dengan parutan kelapa dan siraman gula merah cair.",
    "Klepon adalah kue basah berbentuk bola-bola kecil berbahan tepung ketan berisi gula merah cair dan dibalur kelapa parut.",
    "Martabak Manis atau Terang Bulan adalah kue dadar tebal bertekstur lembut dengan variasi isian cokelat, keju, dan kacang.",
    "Bika Ambon adalah kue khas Medan yang bertekstur bersarang dan berbahan dasar telur, gula, tepung sagu, serta santan.",
    "Lumpia Semarang diisi dengan rebung (tunas bambu), telur, dan daging cincang, disajikan dengan saus kental manis.",
    "Serabi Solo terbuat dari adonan tepung beras dan santan yang dimasak menggunakan wajan tanah liat kecil.",
    "Kerak Telor adalah makanan khas Betawi yang terbuat dari beras ketan putih, telur ayam atau bebek, ebi, dan serundeng.",
    "Kue Cucur adalah jajanan berserat khas Betawi berbahan tepung beras dan gula jawa yang digoreng.",
    "Onde-onde adalah kue berbentuk bulat berbalur biji wijen yang umumnya berisi adonan kacang hijau manis.",
    "Kue Lapis Legit memiliki tekstur berlapis-lapis tipis yang terinspirasi dari kue spekkek peninggalan era kolonial Belanda.",

    # 3. Minuman & Es Tradisional
    "Es Teler terdiri dari alpukat, nangka, kelapa muda, cincau, dan es serut yang disiram susu kental manis.",
    "Es Cendol atau Dawet terbuat dari tepung beras yang dicetak panjang, disajikan dengan santan, es, dan gula merah cair.",
    "Jamu adalah minuman herbal tradisional Indonesia yang diracik dari bahan alami seperti kunyit, temulawak, jahe, dan kencur.",
    "Stik Es Puter terbuat dari santan kelapa sebagai pengganti susu, menghasilkan tekstur es krim tradisional yang gurih.",
    "Bir Pletok adalah minuman rempah non-alkohol khas Betawi yang terbuat dari jahe, serai, dan kayu secang.",
    "Wedang Ronde adalah minuman hangat berisi bola-bola tepung ketan bertabur kacang dalam kuah jahe manis.",
    "Bajigur adalah minuman hangat khas Sunda berbahan dasar santan dan gula aren yang dicampur sedikit garam dan jahe.",
    "Sekoteng adalah minuman hangat khas Jawa Tengah yang berisi kacang hijau, kacang tanah, pacar cina, dan potongan roti dalam kuah jahe.",

    # 4. Bumbu, Pelengkap, & Produk Kuliner
    "Sambal Terasi adalah kondimen khas Indonesia berbahan cabai dan terasi (udang atau ikan yang difermentasi).",
    "Kecap Manis adalah kecap berbahan kedelai hitam khas Indonesia yang memiliki tekstur kental dan rasa manis legit.",
    "Kluwek adalah biji tanaman pucung yang diolah untuk memberikan warna hitam alami dan rasa khas pada Rawon dan Sup Konro.",
    "Bumbu Basa Genep adalah bumbu dasar khas Bali yang terdiri dari belasan jenis rempah dan akar-akaran.",
    "Tempoyak adalah masakan khas Melayu dan Sumatra berupa hasil fermentasi daging buah durian.",
    "Oncom adalah makanan olahan khas Jawa Barat hasil fermentasi dari bungkil tahu atau bungkil kacang tanah.",
    "Tempe adalah makanan olahan kedelai asli Indonesia yang dihasilkan melalui proses fermentasi oleh jamur Rhizopus.",
    "Tahu Sumedang terkenal karena tekstur luar yang renyah dan bagian dalam yang sangat lembut."
]

# Modifikator variasi agar dataset kaya variasi bahasa dan konteks
variations = [
    "Fakta Kuliner: {f}",
    "Fakta Makanan Indonesia: {f}",
    "Tahukah kamu? {f}",
    "Informasi Kuliner: {f}",
    "Fakta Masakan Nusantara: {f}",
    "Catatan Makanan: {f}",
    "Detail Kuliner: {f}",
    "Dunia Kuliner Indonesia: {f}",
    "Fakta Jajanan Pasar: {f}",
    "Ensiklopedi Kuliner: {f}",
    "Keunikan Makanan Indonesia: {f}",
    "Fakta Bumbu dan Rempah: {f}"
]

dataset = []
seen = set()

# Menghasilkan dataset unik
for fact in food_facts_base:
    # 1. Masukkan bentuk asli
    if fact not in seen:
        seen.add(fact)
        dataset.append({
            "type": "fact",
            "content": fact
        })

    # 2. Masukkan bentuk variasi
    for var in variations:
        formatted = var.format(f=fact)
        if formatted not in seen:
            seen.add(formatted)
            dataset.append({
                "type": "fact",
                "content": formatted
            })

# Mengambil tepat 650 baris unik
final_dataset = dataset[:650]

# Simpan ke berkas JSON
with open("knowledge_base.json", "w", encoding="utf-8") as f:
    json.dump(final_dataset, f, ensure_ascii=False, indent=2)

print(f"Berhasil membuat knowledge_base.json dengan total {len(final_dataset)} baris fakta makanan!")