import json
import os
import random
from collections import defaultdict
from initial_knowledge import INITIAL_KNOWLEDGE


class GeneralPikoBrain:
    def __init__(self, save_file="piko_general_memory.json"):
        self.neurons = {}  # Pengetahuan eksplisit (Graf/Kamus)
        self.ngram_model = defaultdict(lambda: defaultdict(int))  # Statistik Next-Token
        self.conversation_log = {}  # Hafalan Q&A spesifik
        self.sentence_memory = []  # Memori kalimat utuh untuk sintesis kreatif
        self.save_file = save_file
        self.learning_rate = 0.1

        # Cek apakah ini pertama kali dijalankan
        if not os.path.exists(self.save_file):
            print("📚 Membaca Data Sheet Awal...")
            self.load_initial_knowledge()

        self.load_memory()

    # ------------------------------------------------------------------
    # MEMORY MANAGEMENT
    # ------------------------------------------------------------------
    def load_initial_knowledge(self):
        """Memasukkan data dasar ke dalam otak"""
        for word, info in INITIAL_KNOWLEDGE.items():
            self.add_word(word, info["category"])
            for related_word in info["related"]:
                self.connect(word, related_word, strength=1.5)
        print("✅ Data Sheet Awal berhasil dimuat.")

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
        with open(self.save_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def mass_learn_from_json(self, filepath):
        """Belajar secara masif dari file JSON"""
        if not os.path.exists(filepath):
            print(f"❌ File {filepath} tidak ditemukan.")
            return

        print(f"📚 Memulai pembelajaran masif dari {filepath}...")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        count_qa = 0
        count_fact = 0

        for item in data:
            item_type = item.get("type")

            if item_type == "qa":
                q = item["question"].lower().strip()
                a = item["answer"]
                self.conversation_log[q] = a
                self._learn_text_internal(item["question"])
                self._learn_text_internal(a)
                # Simpan kalimat jawaban ke episodic memory
                if a not in self.sentence_memory:
                    self.sentence_memory.append(a)
                count_qa += 1

            elif item_type == "fact":
                content = item["content"]
                self._learn_text_internal(content)
                if content not in self.sentence_memory:
                    self.sentence_memory.append(content)
                count_fact += 1

            elif item_type == "conversation":
                inp = item["input"].lower().strip()
                out = item["output"]
                self.conversation_log[inp] = out
                self._learn_text_internal(inp)
                self._learn_text_internal(out)
                if out not in self.sentence_memory:
                    self.sentence_memory.append(out)
                count_qa += 1

        # Batasi sentence_memory agar tidak membengkak
        if len(self.sentence_memory) > 1000:
            self.sentence_memory = self.sentence_memory[-1000:]

        self.save_memory()
        print(f"✅ Selesai! Mempelajari {count_qa} pola QA dan {count_fact} fakta.")

    # ------------------------------------------------------------------
    # CORE LEARNING
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
        """Belajar tanpa save_memory (untuk batch processing)"""
        words = text.lower().split()
        # Asosiasi Graf (window 3 kata)
        for i in range(len(words)):
            for j in range(i + 1, min(i + 3, len(words))):
                self.connect(words[i], words[j], strength=self.learning_rate)
        # N-Gram statistik
        for i in range(len(words) - 1):
            self.ngram_model[words[i]][words[i + 1]] += 1

    def learn_from_text(self, text):
        """Belajar dari teks + simpan ke episodic memory + save ke disk"""
        self._learn_text_internal(text)

        # Simpan kalimat utuh ke episodic memory
        cleaned = text.strip()
        if cleaned and cleaned not in self.sentence_memory:
            self.sentence_memory.append(cleaned)
            if len(self.sentence_memory) > 1000:
                self.sentence_memory.pop(0)

        self.save_memory()

    def teach_response(self, question, answer):
        """Mengajarkan respon spesifik"""
        self.conversation_log[question.lower().strip()] = answer
        self._learn_text_internal(question)
        self._learn_text_internal(answer)
        if answer not in self.sentence_memory:
            self.sentence_memory.append(answer)
        self.save_memory()
        print(f"💡 Piko belajar: '{question}' -> '{answer}'")

    # ------------------------------------------------------------------
    # NOVEL SENTENCE GENERATION
    # ------------------------------------------------------------------
    def generate_novel_sentence(self, topic_word=None):
        """
        Menyusun kalimat baru yang benar-benar baru berdasarkan
        pola kalimat yang pernah dilihat + koneksi neuron.
        """
        # Cari kalimat referensi yang mengandung topik
        if topic_word:
            candidates = [s for s in self.sentence_memory if topic_word.lower() in s.lower()]
        else:
            candidates = self.sentence_memory

        if not candidates:
            return "Saya belum punya cukup contoh kalimat untuk disusun."

        # Ambil satu kalimat sebagai template
        template = random.choice(candidates).split()
        new_sentence = []

        for word in template:
            clean_word = word.lower().strip(".,!?;:")
            # 30% kemungkinan mengganti kata dengan kata terkait dari neuron
            if random.random() < 0.3 and clean_word in self.neurons:
                connections = self.neurons[clean_word]["connections"]
                if connections:
                    replacement = max(connections, key=connections.get)
                    new_sentence.append(replacement)
                else:
                    new_sentence.append(word)
            else:
                new_sentence.append(word)

        final_sentence = " ".join(new_sentence)

        # Catat kalimat baru ini juga ke memori
        if final_sentence not in self.sentence_memory:
            self.sentence_memory.append(final_sentence)
            if len(self.sentence_memory) > 1000:
                self.sentence_memory.pop(0)
            self.save_memory()

        return final_sentence.capitalize() + "."

    # ------------------------------------------------------------------
    # CONVERSATION HANDLING
    # ------------------------------------------------------------------
    def handle_conversation(self, prompt):
        """Menangani sapaan dan pola percakapan dasar"""
        lower_prompt = prompt.lower().strip()

        # Cek conversation_log dulu (prioritas tertinggi)
        if lower_prompt in self.conversation_log:
            return self.conversation_log[lower_prompt]

        # Pola sapaan dasar
        if any(greet in lower_prompt for greet in ["hai", "halo", "hi", "hello"]):
            return "Halo! Senang bertemu denganmu."
        if "apa kabar" in lower_prompt:
            return "Baik, kabar kamu bagaimana?"
        if "siapa namamu" in lower_prompt or "kamu siapa" in lower_prompt:
            return "Saya Piko, asisten AI yang sedang belajar dari kamu."

        return None

    # ------------------------------------------------------------------
    # REASONING & RESPONSE
    # ------------------------------------------------------------------
    def reason_and_respond(self, prompt):
        """Menalar berdasarkan kata kunci, kategori, dan konteks"""
        words = prompt.lower().split()

        # Trigger kreativitas / pembuatan kalimat baru
        if any(kw in prompt.lower() for kw in ["buat kalimat", "cerita", "rangkai kata"]):
            topic = words[-1] if len(words) > 2 else None
            return self.generate_novel_sentence(topic)

        # Deteksi kategori dan subjek utama
        detected_categories = []
        key_subject = None

        for word in words:
            clean = word.strip(".,!?;:")
            if clean in self.neurons:
                cat = self.neurons[clean].get("category")
                if cat and cat not in ["kata_tanya", "konfirmasi", "penolakan"]:
                    detected_categories.append(cat)
                    if not key_subject:
                        key_subject = clean

        # A. Respon Empati / Kondisi Fisik / Emosi
        if any(c in detected_categories for c in ["kondisi", "fisik", "emosi"]):
            if key_subject and key_subject in self.neurons:
                related = list(self.neurons[key_subject]["connections"].keys())[:3]
                if related:
                    return (
                        f"Waduh, kamu {key_subject}? "
                        f"Itu biasanya berhubungan dengan {', '.join(related)}. "
                        f"Kamu butuh bantuan apa?"
                    )
                return f"Oh, kamu {key_subject}? Ceritakan lebih lanjut dong."

        # B. Pertanyaan Fakta / Definisi
        if "kata_tanya" in detected_categories or "fakta" in prompt.lower():
            # Cari di conversation_log dengan fuzzy match
            for q, a in self.conversation_log.items():
                if any(w in q for w in words if len(w) > 3):
                    return a
            # Fallback ke definisi neuron
            if key_subject and key_subject in self.neurons:
                cat = self.neurons[key_subject].get("category", "hal")
                return (
                    f"Menurut catatan saya, '{key_subject}' itu termasuk {cat}. "
                    f"Tapi saya masih ingin tahu lebih banyak dari kamu!"
                )

        # C. Respon Mengalir via Graph Connection
        if key_subject and key_subject in self.neurons:
            connections = self.neurons[key_subject]["connections"]
            if connections:
                best_match = max(connections, key=connections.get)
                return (
                    f"Menarik soal '{key_subject}'. "
                    f"Apakah itu ada hubungannya dengan '{best_match}'?"
                )

        # D. Fallback Interaktif
        return (
            f"Hmm, saya belum sering mendengar frasa itu. "
            f"Bisa jelaskan maksud '{prompt}' dengan kata lain?"
        )

    def generate_response(self, prompt):
        """Pipeline respon: Conversation -> Reasoning -> Fallback"""
        conversational_reply = self.handle_conversation(prompt)
        if conversational_reply:
            return conversational_reply
        return self.reason_and_respond(prompt)

    # ------------------------------------------------------------------
    # MAIN INTERACTION
    # ------------------------------------------------------------------
    def interact(self, user_input, feedback="reward"):
        """Proses interaksi utama: Belajar + Merespons"""
        self.learn_from_text(user_input)

        if feedback == "penalty":
            words = user_input.split()
            if len(words) > 1:
                self.connect(words[-2], words[-1], strength=-0.2)
                self.save_memory()

        return self.generate_response(user_input)