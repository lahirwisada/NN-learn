from brain_general import GeneralPikoBrain


def main():
    brain = GeneralPikoBrain()

    # --- BAGIAN BARU: PEMBELAJARAN MASIF ---
    # Uncomment baris di bawah ini jika ingin mengisi otak Piko dengan data game/kesehatan
    # brain.mass_learn_from_json("knowledge_base.json")
    # -----------------------------------------

    print("👋 Halo! Saya Piko General. Ketik 'exit' untuk berhenti.")
    print("Tips: Jika saya salah jawab, ketik 'ajar: [pertanyaan] -> [jawaban]'")
    print("Perintah Khusus:")
    print("  - ajar: [pertanyaan] -> [jawaban]  (Ajarkan respon spesifik)")
    print("  - p-bad                              (Beri penalti respon terakhir)")
    print("  - l-kb -> [path_file.json]           (Load knowledge base masif)")

    last_input = ""  # Variabel untuk menyimpan input terakhir user

    while True:
        user_input = input("\nKamu: ")
        if user_input.lower() == "exit":
            break

        if user_input.strip().lower().startswith("l-kb"):
            try:
                # Format: l-kb -> path/to/file.json
                parts = user_input.split("->")
                if len(parts) == 2:
                    filepath = parts[1].strip()
                    print(f"📂 Memuat knowledge base dari: {filepath}")
                    brain.mass_learn_from_json(filepath)
                else:
                    print("⚠️ Format salah. Gunakan: l-kb -> nama_file.json")
            except Exception as e:
                print(f"❌ Gagal memuat file: {e}")
            continue

        # Fitur khusus untuk mengajar
        if user_input.lower().startswith("ajar:"):
            try:
                parts = user_input.split("->")
                q = parts[0].replace("ajar:", "").strip()
                a = parts[1].strip()
                brain.teach_response(q, a)
                continue
            except:
                print("Format salah. Gunakan: ajar: halo -> hai juga")

        if user_input.strip() == "p-bad":
            if last_input:
                print("⚠️ Memberikan penalti untuk respon sebelumnya...")
                # Panggil interact dengan feedback penalty menggunakan input terakhir
                brain.interact(last_input, feedback="penalty")
                print("Piko: Maaf, saya telah melemahkan koneksi yang salah.")
            else:
                print("⚠️ Tidak ada input sebelumnya untuk diberi penalti.")
            continue  # Lewati proses normal

        last_input = user_input

        # AI merespons sekaligus belajar
        response = brain.interact(user_input)
        print(f"Piko: {response}")


if __name__ == "__main__":
    main()
