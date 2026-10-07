import json
import os
import random
from collections import defaultdict
from initial_knowledge import INITIAL_KNOWLEDGE


class GeneralPikoBrain:
    def __init__(self, save_file="piko_general_memory.json"):
        self.neurons = {}
        self.ngram_model = defaultdict(lambda: defaultdict(int))
        self.conversation_log = {}  # Sekarang akan menyimpan List of Strings untuk variasi
        self.sentence_memory = []  # Episodic Memory untuk sintesis kalimat
        self.save_file = save_file
        self.learning_rate = 0.1

        # Kata-kata yang sebaiknya tidak dijadikan subjek cerita atau koneksi utama
        self.stopwords = [
            "adalah",
            "yang",
            "di",
            "ke",
            "dari",
            "untuk",
            "dengan",
            "ini",
            "itu",
            "dan",
            "atau",
            "pada",
            "dalam",
            "secara",
            "saya",
            "kamu",
            "dia",
            "mereka",
            "kami",
            "kita",
            "anda",
            "nih",
            "dong",
            "lah",
            "kah",
        ]

        if not os.path.exists(self.save_file):
            print("📚 Membaca Data Sheet Awal...")
            self.load_initial_knowledge()

        self.load_memory()

    def parse_spok(self, prompt):
        """
        Menganalisis kalimat menjadi struktur SPOK sederhana.
        Mengembalikan dictionary: {'S': [], 'P': [], 'O': [], 'K': []}
        """
        words = prompt.lower().split()
        structure = {"S": [], "P": [], "O": [], "K": []}
        current_role = "S"  # Mulai dengan asumsi Subjek

        for word in words:
            clean_word = word.strip(".,?!'\"")
            if not clean_word:
                continue

            if clean_word in self.neurons:
                cat = self.neurons[clean_word].get("category", "")

                # Logika sederhana penentuan peran
                if cat == "subjek":
                    structure["S"].append(clean_word)
                    current_role = "P"  # Setelah subjek, biasanya predikat
                elif cat == "predikat":
                    structure["P"].append(clean_word)
                    current_role = "O"  # Setelah predikat, biasanya objek
                elif cat == "objek":
                    structure["O"].append(clean_word)
                elif cat == "preposisi":
                    current_role = "K"  # Preposisi menandakan awal keterangan
                    structure["K"].append(clean_word)
                elif cat == "keterangan" or cat == "tempat":
                    structure["K"].append(clean_word)
                else:
                    # Jika kategori tidak jelas, masukkan ke role saat ini
                    structure[current_role].append(clean_word)
            else:
                # Kata asing dimasukkan ke role saat ini
                structure[current_role].append(clean_word)

        return structure

    # ------------------------------------------------------------------
    # MEMORY MANAGEMENT
    # ------------------------------------------------------------------
    def load_initial_knowledge(self):
        for word, info in INITIAL_KNOWLEDGE.items():
            self.add_word(word, info["category"])
            for related_word in info.get("related", []):
                self.connect(word, related_word, strength=1.5)
        print("✅ Data Sheet Awal berhasil dimuat.")

    def reload_initial_knowledge(self):
        """Memuat ulang data dasar dari initial_knowledge.py"""
        print("🔄 Memuat ulang pengetahuan dasar...")
        for word, info in INITIAL_KNOWLEDGE.items():
            self.add_word(word, info["category"])
            for related_word in info.get("related", []):
                self.connect(word, related_word, strength=1.5)
        print("✅ Pengetahuan dasar berhasil dimuat ulang.")

    def load_memory(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.neurons = data.get("neurons", {})
                    self.conversation_log = data.get("conversation_log", {})
                    self.sentence_memory = data.get("sentence_memory", [])

                    raw_ngram = data.get("ngram_model", {})
                    for k, v in raw_ngram.items():
                        self.ngram_model[k] = defaultdict(int, v)
                print(f"🧠 Memori dimuat dari {self.save_file}")
            except Exception as e:
                print(f"⚠️ Error memuat memori: {e}")
        else:
            print("🆕 Memori baru dibuat.")

    def save_memory(self):
        data = {
            "neurons": self.neurons,
            "ngram_model": dict(self.ngram_model),
            "conversation_log": self.conversation_log,
            "sentence_memory": self.sentence_memory,
        }
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Gagal menyimpan memori: {e}")

    def mass_learn_from_json(self, filepath):
        if not os.path.exists(filepath):
            print(f"❌ File {filepath} tidak ditemukan.")
            return
        print(f"📚 Memulai pembelajaran masif dari {filepath}...")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Gagal membaca file: {e}")
            return

        count_qa = 0
        count_fact = 0
        for item in data:
            item_type = item.get("type")
            if item_type == "qa":
                q = item.get("question", "").lower().strip()
                a = item.get("answer", "")
                if q and a:
                    # Gunakan teach_response_internal agar support list
                    self._add_to_conversation_log(q, a)
                    self._learn_text_internal(q)
                    self._learn_text_internal(a)
                    count_qa += 1
            elif item_type == "fact":
                content = item.get("content", "")
                if content:
                    self._learn_text_internal(content)
                    count_fact += 1
            elif item_type == "conversation":
                inp = item.get("input", "").lower().strip()
                out = item.get("output", "")
                if inp and out:
                    self._add_to_conversation_log(inp, out)
                    count_qa += 1

        self.save_memory()
        print(f"✅ Selesai! Mempelajari {count_qa} pola QA dan {count_fact} fakta.")

    # ------------------------------------------------------------------
    # CORE LEARNING ENGINE
    # ------------------------------------------------------------------
    def add_word(self, word, category="unknown"):
        if word not in self.neurons:
            self.neurons[word] = {"category": category, "connections": {}}

    def connect(self, word1, word2, strength=1.0):
        self.add_word(word1)
        self.add_word(word2)
        curr_w1 = self.neurons[word1]["connections"].get(word2, 0)
        self.neurons[word1]["connections"][word2] = curr_w1 + strength
        curr_w2 = self.neurons[word2]["connections"].get(word1, 0)
        self.neurons[word2]["connections"][word1] = curr_w2 + strength

    def _learn_text_internal(self, text):
        words = text.lower().split()
        # 1. Asosiasi Graf
        for i in range(len(words)):
            for j in range(i + 1, min(i + 3, len(words))):
                self.connect(words[i], words[j], strength=self.learning_rate)
        # 2. Statistik N-gram
        for i in range(len(words) - 1):
            self.ngram_model[words[i]][words[i + 1]] += 1
        # 3. Episodic Memory
        clean_text = text.strip()
        if clean_text and clean_text not in self.sentence_memory:
            self.sentence_memory.append(clean_text)
            if len(self.sentence_memory) > 1000:
                self.sentence_memory.pop(0)

    def learn_from_text(self, text):
        self._learn_text_internal(text)
        self.save_memory()

    def _normalize_key(self, text):
        """Normalisasi teks untuk key dictionary: lowercase, hapus spasi berlebih & tanda baca"""
        import re

        text = text.lower().strip()
        text = re.sub(r"[.,?!\'\";:]", "", text)  # Hapus tanda baca
        text = re.sub(r"\s+", " ", text)  # Hapus spasi berlebih
        return text

    def _add_to_conversation_log(self, question, answer):
        """Helper untuk menambahkan jawaban ke dalam list (mendukung variasi)"""

        key = self._normalize_key(question)
        if key not in self.conversation_log:
            self.conversation_log[key] = []

        # Jika masih format lama (string), konversi ke list
        if isinstance(self.conversation_log[key], str):
            self.conversation_log[key] = [self.conversation_log[key]]

        if answer not in self.conversation_log[key]:
            self.conversation_log[key].append(answer)

    def teach_response(self, question, answer):
        """Mengajarkan respon spesifik dengan dukungan variasi"""
        key = question.lower().strip()
        self._add_to_conversation_log(key, answer)
        self._learn_text_internal(question)
        self._learn_text_internal(answer)
        self.save_memory()
        print(f"Piko belajar variasi jawaban untuk '{question}'")

    # ------------------------------------------------------------------
    # STORYTELLING & GENERATION
    # ------------------------------------------------------------------
    def generate_novel_sentence(self, topic_word=None):
        """Menyusun kalimat baru berdasarkan pola memori episodik"""

        # 1. Filter Kandidat Kalimat
        candidates = []

        # Jika ada topik spesifik, cari kalimat yang mengandung topik tersebut
        if topic_word and topic_word.lower() not in self.stopwords:
            candidates = [
                s for s in self.sentence_memory if topic_word.lower() in s.lower()
            ]

        # Jika tidak ada topik atau tidak ditemukan, ambil kalimat acak yang 'layak'
        if not candidates:
            worthy_sentences = []
            for s in self.sentence_memory:
                words_in_s = s.lower().split()
                # Syarat 1: Panjang kalimat > 4 kata
                if len(words_in_s) < 5:
                    continue

                # Syarat 2: Bukan kalimat perintah user (hindari "buat kalimat", "ajar:", dll)
                command_triggers = [
                    "buat",
                    "ajar",
                    "tolong",
                    "mohon",
                    "ceritakan",
                    "jelaskan",
                ]
                if any(w in words_in_s for w in command_triggers):
                    continue

                # Syarat 3: Harus memiliki setidaknya 2 kata benda/kategori bermakna (bukan stopwords)
                meaningful_count = sum(
                    1
                    for w in words_in_s
                    if w.strip(".,?!'\"") not in self.stopwords
                    and w.strip(".,?!'\"") in self.neurons
                )
                if meaningful_count >= 2:
                    worthy_sentences.append(s)

            candidates = worthy_sentences

        if not candidates:
            return (
                "Maaf, saya belum punya cukup bahan kalimat yang bagus untuk dicontoh."
            )

        # 2. Pilih Template Secara Acak
        template = random.choice(candidates).split()
        new_sentence = []

        # 3. Rakit Kalimat Baru (Modifikasi 30% kata)
        for word in template:
            clean_word = word.strip(".,?!'\"").lower()

            # Jangan ganti kata jika itu kata fungsi/stopword
            if clean_word in self.stopwords:
                new_sentence.append(word)
                continue

            # 30% kemungkinan mengganti kata dengan koneksi terkuat dari neuron
            if random.random() < 0.3 and clean_word in self.neurons:
                connections = self.neurons[clean_word]["connections"]
                if connections:
                    # Ambil kata pengganti yang bukan stopword
                    replacement = max(connections, key=connections.get)
                    if replacement.lower() not in self.stopwords:
                        new_sentence.append(replacement)
                    else:
                        new_sentence.append(word)
                else:
                    new_sentence.append(word)
            else:
                new_sentence.append(word)

        final_sentence = " ".join(new_sentence)

        # Simpan ke memori jika unik
        if final_sentence not in self.sentence_memory:
            self.sentence_memory.append(final_sentence)
            if len(self.sentence_memory) > 1000:
                self.sentence_memory.pop(0)
            self.save_memory()

        return final_sentence.capitalize() + "."

    def try_spontaneous_story(self, subject):
        """
        Mencoba menyisipkan cerita spontan jika subjek diketahui.
        Peluang muncul: 20%
        """
        # Jangan bercerita jika subjeknya kosong atau kata umum
        if not subject or subject.lower() in self.stopwords:
            return ""
        if subject not in self.neurons:
            return ""

        # Cek apakah subject punya koneksi yang bermakna untuk diceritakan
        connections = self.neurons[subject]["connections"]
        meaningful_connections = {
            k: v for k, v in connections.items() if k not in self.stopwords
        }

        if not meaningful_connections:
            return ""

        if random.random() < 0.2:  # 20% chance to tell a story
            story = self.generate_novel_sentence(subject)
            if story:
                return f"\n\nNgomong-ngomong, {story}"
        return ""

    # ------------------------------------------------------------------
    # BABY LEARNING LOGIC
    # ------------------------------------------------------------------
    def analyze_input(self, prompt):
        """Menganalisis input untuk memisahkan kata DIKENAL dan ASING"""
        words = prompt.lower().split()
        known_words = []
        unknown_words = []
        key_subject = None

        # Daftar kata yang JANGAN pernah jadi subjek utama
        ignore_as_subject = [
            "coba",
            "tolong",
            "mohon",
            "bisa",
            "boleh",
            "harus",
            "mau",
            "ingin",
            "akan",
            "sedang",
            "telah",
            "sudah",
            "belum",
        ] + self.stopwords

        clean_words = [w.strip(".,?!'\"") for w in words if w.strip(".,?!'\"")]

        for word in clean_words:
            if word in self.neurons:
                known_words.append(word)
                if not key_subject:
                    cat = self.neurons[word].get("category", "")
                    # Abaikan jika kata ada di daftar abaikan atau kategorinya tidak relevan
                    if word not in ignore_as_subject and cat not in [
                        "kata_tanya",
                        "konfirmasi",
                        "penolakan",
                    ]:
                        key_subject = word
            else:
                unknown_words.append(word)

        return known_words, unknown_words, key_subject

    def baby_respond(self, prompt):
        """Logika utama respon ala bayi: Tanya jika tidak tahu, Jawab jika tahu"""
        normalized_prompt = self._normalize_key(prompt)
        if normalized_prompt in self.conversation_log:
            answers = self.conversation_log[normalized_prompt]
            if isinstance(answers, list):
                return random.choice(answers)
            return answers

        known, unknown, subject = self.analyze_input(prompt)

        # Selalu simpan kalimat utuh ke memori
        if prompt not in self.sentence_memory:
            self.sentence_memory.append(prompt)
            if len(self.sentence_memory) > 1000:
                self.sentence_memory.pop(0)

        # --- TRIGGER KREATIVITAS ---
        # Jika user meminta membuat kalimat, langsung panggil generator
        creative_triggers = [
            "buat kalimat",
            "buatkan kalimat",
            "cerita",
            "karang",
            "susun kata",
        ]
        if any(trigger in prompt.lower() for trigger in creative_triggers):
            story = self.generate_novel_sentence(subject)
            if story:
                return f"Tentu! Ini kalimat buatanku: {story}"
            else:
                return "Maaf, saya belum punya cukup bahan untuk membuat kalimat tentang itu."
        # ---------------------------

        # SKENARIO 1: Ada kata asing (Gap Pengetahuan)
        if unknown:
            questions = unknown[:3]  # Tanyakan max 3 kata asing
            response_parts = []
            if known:
                response_parts.append(", ".join(known[:3]))

            question_str = ", ".join([f"apa itu '{w}'?" for w in questions])

            if response_parts:
                return f"{', '.join(response_parts)}... {question_str}"
            else:
                return f"Saya tidak mengerti. {question_str}"

        # SKENARIO 2: Semua kata dikenal (Full Understanding)
        else:
            main_response = self.reason_and_respond_fully_understood(prompt, subject)

            # Tambahkan cerita spontan di akhir (hanya jika bukan permintaan kreatif eksplisit)
            spontaneous_story = self.try_spontaneous_story(subject)

            return main_response + spontaneous_story

    def get_meaningful_connection(self, word):
        """Mencari koneksi kata yang bermakna (bukan kata fungsional)"""
        if word not in self.neurons:
            return None
        connections = self.neurons[word]["connections"]
        if not connections:
            return None

        meaningful_candidates = {
            k: v
            for k, v in connections.items()
            if k not in self.stopwords and k != word
        }

        if meaningful_candidates:
            return max(meaningful_candidates, key=meaningful_candidates.get)
        elif connections:
            return max(connections, key=connections.get)
        return None

    def reason_and_respond_fully_understood(self, prompt, subject):
        """Logika penalaran jika semua kata sudah dipahami"""
        normalized_prompt = self._normalize_key(prompt)
        if normalized_prompt in self.conversation_log:
            answers = self.conversation_log[normalized_prompt]
            if isinstance(answers, list):
                return random.choice(answers)
            return answers

        lower_prompt = prompt.lower().strip()

        # Cek conversation_log (Support Variasi Jawaban)
        if lower_prompt in self.conversation_log:
            answers = self.conversation_log[lower_prompt]
            if isinstance(answers, list):
                return random.choice(answers)
            return answers

        detected_cats = [
            self.neurons[w]["category"] for w in prompt.split() if w in self.neurons
        ]

        # Empati/Kondisi
        if any(c in ["kondisi", "fisik", "emosi"] for c in detected_cats):
            if subject and subject in self.neurons:
                related = list(self.neurons[subject]["connections"].keys())[:3]
                if related:
                    return f"Waduh, {subject}? Itu berhubungan dengan {', '.join(related)}. Kamu butuh bantuan?"

        # Fakta/Definisi (Diperbaiki agar lebih akurat)
        if (
            "kata_tanya" in detected_cats
            or "apa" in lower_prompt
            or "siapa" in lower_prompt
        ):
            if subject and subject in self.neurons:
                cat = self.neurons[subject].get("category", "hal")

                # Cari definisi spesifik di conversation log yang mengandung "adalah"
                found_def = False
                for q, a_list in self.conversation_log.items():
                    # Pastikan pertanyaan di log mirip dengan input user DAN mengandung subjek
                    if subject in q and ("apa itu" in q or "definisi" in q):
                        answers = a_list if isinstance(a_list, list) else [a_list]
                        # Pilih jawaban yang paling deskriptif (mengandung 'adalah')
                        desc_answers = [a for a in answers if "adalah" in a.lower()]
                        if desc_answers:
                            return random.choice(desc_answers)
                        found_def = True

                if found_def:
                    # Jika ada di log tapi tidak ada yang deskriptif, ambil acak
                    answers = self.conversation_log[
                        [q for q in self.conversation_log.keys() if subject in q][0]
                    ]
                    return (
                        random.choice(answers) if isinstance(answers, list) else answers
                    )

                # Fallback ke kategori neuron
                return f"Menurut catatan saya, '{subject}' itu termasuk {cat}. Tapi saya masih ingin tahu lebih banyak dari kamu!"

        # Fallback Interaktif
        if subject and subject in self.neurons:
            best_match = self.get_meaningful_connection(subject)
            if best_match:
                return f"Ya, saya tahu {subject}. Itu terkait erat dengan {best_match}, kan?"
            else:
                return f"Saya tahu {subject}, tapi saya masih belajar hubungannya dengan hal lain."

        return "Saya paham kata-katanya, tapi bingung maksud kalimatnya. Bisa jelaskan lagi?"

    def generate_response(self, prompt):
        return self.baby_respond(prompt)

    # ------------------------------------------------------------------
    # INTERACTION INTERFACE
    # ------------------------------------------------------------------
    def interact(self, user_input, feedback="reward"):
        self.learn_from_text(user_input)
        if feedback == "penalty":
            words = user_input.split()
            if len(words) > 1:
                self.connect(words[-2], words[-1], strength=-0.2)
                self.save_memory()
        return self.generate_response(user_input)
