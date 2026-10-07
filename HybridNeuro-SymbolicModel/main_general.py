from brain_general import GeneralPikoBrain


def print_help():
    print("\n--- 📜 DAFTAR PERINTAH KHUSUS ---")
    print(" 1. exit                  : Keluar dari program.")
    print(" 2. ajar: [Q] -> [A]     : Ajarkan respon spesifik.")
    print(" 3. p-bad                 : Beri penalti pada respon terakhir Piko.")
    print(" 4. l-kb -> [path.json]   : Load knowledge base masif dari JSON.")
    print(" 5. l-txt -> [path.txt]   : Belajar dari file teks (.txt).")
    print(" 6. l-html -> [path.html] : Belajar dari file HTML lokal.")
    print(" 7. l-url-other -> [link] : Kunjungi website umum dan belajar isinya.")
    print(" 8. l-url-kbbi -> [kata]  : Cari arti kata di KBBI.co.id dan ajarkan.")
    print(" 9. l-kbbi-loop -> [file] : Loop belajar KBBI dari file daftar kata.")
    print(" 9. reload-dasar          : Muat ulang pengetahuan dasar.")
    print(" 10. show-help            : Tampilkan bantuan ini lagi.")
    print("----------------------------------\n")


def main():
    brain = GeneralPikoBrain()

    print("👋 Halo! Saya Piko General. Ketik 'exit' untuk berhenti.")
    print("Tips: Jika saya salah jawab, ketik 'ajar: [pertanyaan] -> [jawaban]'")
    print("Ketik 'show-help' untuk melihat daftar perintah lengkap.")

    last_input = ""

    while True:
        user_input = input("\nKamu: ")

        if user_input.lower() == "exit":
            break

        if user_input.strip().lower() == "show-help":
            print_help()
            continue

        # --- FITUR BARU: LOAD TXT ---
        if user_input.strip().lower().startswith("l-txt"):
            try:
                parts = user_input.split("->")
                if len(parts) == 2:
                    filepath = parts[1].strip()
                    print(f"📂 Memuat file teks dari: {filepath}")
                    brain.learn_from_txt(filepath)
                else:
                    print("⚠️ Format salah. Gunakan: l-txt -> nama_file.txt")
            except Exception as e:
                print(f"❌ Gagal memuat file: {e}")
            continue
        # ----------------------------

        # --- FITUR BARU: LOAD HTML ---
        if user_input.strip().lower().startswith("l-html"):
            try:
                parts = user_input.split("->")
                if len(parts) == 2:
                    filepath = parts[1].strip()
                    print(f"📂 Memuat file HTML dari: {filepath}")
                    brain.learn_from_html(filepath)
                else:
                    print("⚠️ Format salah. Gunakan: l-html -> nama_file.html")
            except Exception as e:
                print(f"❌ Gagal memuat file: {e}")
            continue
        # -----------------------------

        if user_input.strip().lower().startswith("l-url-other"):
            try:
                parts = user_input.split("->")
                if len(parts) == 2:
                    url = parts[1].strip()
                    # Validasi sederhana apakah itu URL
                    if url.startswith("http"):
                        print(f"📂 Memproses URL: {url}")
                        brain.learn_from_url(url)
                    else:
                        print(
                            "⚠️ Format URL salah. Pastikan diawali dengan http:// atau https://"
                        )
                else:
                    print("⚠️ Format salah. Gunakan: l-url -> https://contoh.com")
            except Exception as e:
                print(f"❌ Error: {e}")
            continue

        if user_input.strip().lower().startswith("l-kbbi-loop"):
            try:
                parts = user_input.split("->")
                if len(parts) == 2:
                    filepath = parts[1].strip()
                    print(f"📂 Memulai proses loop KBBI dari: {filepath}")
                    brain.learn_kbbi_from_file(filepath)
                else:
                    print("⚠️ Format salah. Gunakan: l-kbbi-loop -> nama_file.txt")
            except Exception as e:
                print(f"❌ Error: {e}")
            continue

        if user_input.strip().lower().startswith("l-url-kbbi"):
            try:
                parts = user_input.split("->")
                if len(parts) == 2:
                    word = parts[1].strip()
                    # Validasi kata sederhana (hanya huruf)
                    if word.isalpha():
                        brain.learn_kbbi_word(word)
                    else:
                        print("⚠️ Masukkan satu kata saja tanpa spasi atau tanda baca.")
                else:
                    print("⚠️ Format salah. Gunakan: l-url-kbbi -> kata")
            except Exception as e:
                print(f"❌ Error: {e}")
            continue

        if user_input.strip().lower().startswith("l-kb"):
            try:
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

        if user_input.strip().lower() == "reload-dasar":
            brain.reload_initial_knowledge()
            continue

        if user_input.strip() == "p-bad":
            if last_input:
                print("⚠️ Memberikan penalti untuk respon sebelumnya...")
                brain.interact(last_input, feedback="penalty")
                print("Piko: Maaf, saya telah melemahkan koneksi yang salah.")
            else:
                print("⚠️ Tidak ada input sebelumnya untuk diberi penalti.")
            continue

        if user_input.lower().startswith("ajar:"):
            try:
                parts = user_input.split("->")
                q = parts[0].replace("ajar:", "").strip()
                a = parts[1].strip()
                brain.teach_response(q, a)
                continue
            except IndexError:
                print("⚠️ Format salah. Gunakan: ajar: pertanyaan -> jawaban")
                continue

        last_input = user_input
        response = brain.interact(user_input)
        print(f"Piko: {response}")


if __name__ == "__main__":
    main()
