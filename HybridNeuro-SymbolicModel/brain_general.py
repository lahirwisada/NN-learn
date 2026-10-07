import json
import os
import random
from collections import defaultdict
from initial_knowledge import INITIAL_KNOWLEDGE  # Import data sheet


class GeneralPikoBrain:
    def __init__(self, save_file="piko_general_memory.json"):
        self.neurons = {}  # Pengetahuan eksplisit (Kamus/Graf)
        self.ngram_model = defaultdict(
            lambda: defaultdict(int)
        )  # Probabilitas kata (Next-token)
        self.conversation_log = {}  # Menyimpan pasangan tanya-jawab yang pernah diajarkan
        self.save_file = save_file
        self.learning_rate = 0.1

        # Cek apakah ini pertama kali dijalankan
        if not os.path.exists(self.save_file):
            print("📚 Membaca Data Sheet Awal...")
            self.load_initial_knowledge()

        self.load_memory()

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
                with open(self.save_file, "r") as f:
                    data = json.load(f)
                    self.neurons = data.get("neurons", {})
                    raw_ngram = data.get("ngram_model", {})
                    for k, v in raw_ngram.items():
                        self.ngram_model[k] = defaultdict(int, v)
                    self.conversation_log = data.get("conversation_log", {})
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
        }
        with open(self.save_file, "w") as f:
            json.dump(data, f, indent=2)

    def mass_learn_from_json(self, filepath):
        """Belajar secara masif dari file JSON"""
        if not os.path.exists(filepath):
            print(f"❌ File {filepath} tidak ditemukan.")
            return

        print(f"📚 Memulai pembelajaran masif dari {filepath}...")
        with open(filepath, "r") as f:
            data = json.load(f)

        count_qa = 0
        count_fact = 0

        for item in data:
            item_type = item.get("type")

            if item_type == "qa":
                # Ajarkan pola percakapan spesifik
                self.conversation_log[item["question"].lower()] = item["answer"]
                # Juga pelajari kata-katanya secara statistik
                self.learn_from_text(item["question"])
                self.learn_from_text(item["answer"])
                count_qa += 1

            elif item_type == "fact":
                # Pelajari hubungan antar kata dalam fakta
                self.learn_from_text(item["content"])
                count_fact += 1

            elif item_type == "conversation":
                self.conversation_log[item["input"].lower()] = item["output"]
                count_qa += 1

        self.save_memory()
        print(f"✅ Selesai! Mempelajari {count_qa} pola QA dan {count_fact} fakta.")

    def add_word(self, word, category="unknown"):
        if word not in self.neurons:
            self.neurons[word] = {"category": category, "connections": {}}
            # Tidak perlu save setiap add_word agar tidak lambat, save di connect/learn saja

    def connect(self, word1, word2, strength=1.0):
        self.add_word(word1)
        self.add_word(word2)
        curr_w1 = self.neurons[word1]["connections"].get(word2, 0)
        self.neurons[word1]["connections"][word2] = curr_w1 + strength
        curr_w2 = self.neurons[word2]["connections"].get(word1, 0)
        self.neurons[word2]["connections"][word1] = curr_w2 + strength
        self.save_memory()

    def learn_from_text(self, text):
        words = text.lower().split()
        # 1. Belajar Asosiasi (Symbolic)
        for i in range(len(words)):
            for j in range(i + 1, min(i + 3, len(words))):
                self.connect(words[i], words[j], strength=self.learning_rate)
        # 2. Belajar Probabilitas (Next-token prediction)
        for i in range(len(words) - 1):
            self.ngram_model[words[i]][words[i + 1]] += 1
        self.save_memory()

    def teach_response(self, question, answer):
        """Mengajarkan respon spesifik untuk sebuah pertanyaan/kalimat"""
        self.conversation_log[question.lower().strip()] = answer
        self.save_memory()
        print(f"💡 Piko belajar: '{question}' -> '{answer}'")

    def handle_conversation(self, prompt):
        """Menangani sapaan dan pertanyaan umum secara interaktif"""
        lower_prompt = prompt.lower().strip()

        # 1. Cek apakah user pernah mengajari respon khusus ini
        if lower_prompt in self.conversation_log:
            return self.conversation_log[lower_prompt]

        # 2. Pola Sapaan Dasar (General Purpose)
        if any(greet in lower_prompt for greet in ["hai", "halo", "hi", "hello"]):
            return "Halo! Senang bertemu denganmu."

        if "apa kabar" in lower_prompt:
            return "Baik, kabar kamu bagaimana?"

        if "siapa namamu" in lower_prompt or "kamu siapa" in lower_prompt:
            return "Saya Piko, asisten AI yang sedang belajar dari kamu."

        return None  # Kembalikan ke generate_response jika tidak ada pola

    def predict_next_token(self, current_word):
        if current_word in self.ngram_model:
            candidates = self.ngram_model[current_word]
            if candidates:
                return max(candidates, key=candidates.get)
        return None

    def generate_response(self, prompt):
        # 1. Cek dulu apakah ini percakapan umum/sapaan
        conversational_reply = self.handle_conversation(prompt)
        if conversational_reply:
            return conversational_reply

        # 2. Jika bukan sapaan, gunakan Next-Token Prediction & Graph
        words = prompt.lower().split()
        if not words:
            return "..."

        last_word = words[-1]
        response_words = []
        current = last_word

        # Generate hingga 8 kata
        for _ in range(8):
            next_word = self.predict_next_token(current)

            # Fallback ke Graph Connections jika tidak ada data statistik
            if not next_word and current in self.neurons:
                connections = self.neurons[current]["connections"]
                if connections:
                    next_word = max(connections, key=connections.get)

            if not next_word or next_word in words:
                break

            response_words.append(next_word)
            current = next_word

        if response_words:
            return " ".join(response_words)

        # 3. Fallback terakhir jika benar-benar tidak tahu
        return f"Saya belum memahami '{prompt}'. Bisa jelaskan maksudnya?"

    def interact(self, user_input, feedback="reward"):
        """Proses interaksi utama: Belajar + Merespons."""
        self.learn_from_text(user_input)

        # Jika feedback penalty, kita kurangi weight koneksi terakhir
        if feedback == "penalty":
            words = user_input.split()
            if len(words) > 1:
                self.connect(words[-2], words[-1], strength=-0.2)

        return self.generate_response(user_input)
