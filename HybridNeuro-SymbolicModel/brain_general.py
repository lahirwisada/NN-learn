import json
import os
import random
from collections import defaultdict
from initial_knowledge import INITIAL_KNOWLEDGE


class GeneralPikoBrain:
    def __init__(self, save_file="piko_general_memory.json"):
        self.neurons = {}
        self.ngram_model = defaultdict(lambda: defaultdict(int))
        self.conversation_log = {}
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
        ]

        if not os.path.exists(self.save_file):
            print("📚 Membaca Data Sheet Awal...")
            self.load_initial_knowledge()

        self.load_memory()

    # ------------------------------------------------------------------
    # MEMORY MANAGEMENT
    # ------------------------------------------------------------------
    def load_initial_knowledge(self):
        for word, info in INITIAL_KNOWLEDGE.items():
            self.add_word(word, info["category"])
            for related_word in info.get("related", []):
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
                    self.conversation_log[q] = a
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
                    self.conversation_log[inp] = out
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

    def teach_response(self, question, answer):
        key = question.lower().strip()
        self.conversation_log[key] = answer
        self._learn_text_internal(question)
        self._learn_text_internal(answer)
        self.save_memory()
        print(f"💡 Piko belajar: '{question}' -> '{answer}'")

    # ------------------------------------------------------------------
    # STORYTELLING & GENERATION
    # ------------------------------------------------------------------
    def generate_novel_sentence(self, topic_word=None):
        """Menyusun kalimat baru berdasarkan pola memori episodik"""
        # Filter kandidat kalimat
        if topic_word and topic_word.lower() not in self.stopwords:
            candidates = [
                s for s in self.sentence_memory if topic_word.lower() in s.lower()
            ]
        else:
            candidates = [s for s in self.sentence_memory if len(s.split()) > 3]

        if not candidates:
            return None

        template = random.choice(candidates).split()
        new_sentence = []

        for word in template:
            clean_word = word.strip(".,?!'\"").lower()
            # Jangan ganti kata jika itu kata fungsi/stopword
            if clean_word in self.stopwords:
                new_sentence.append(word)
                continue

            # 30% kemungkinan mengganti kata dengan koneksi terkuat
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
        # Jangan bercerita jika subjeknya adalah kata fungsi/kata ganti umum
        if not subject or subject.lower() in self.stopwords:
            return ""
        if subject not in self.neurons:
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

        clean_words = [w.strip(".,?!'\"") for w in words if w.strip(".,?!'\"")]

        for word in clean_words:
            if word in self.neurons:
                known_words.append(word)
                if not key_subject:
                    cat = self.neurons[word].get("category", "")
                    # Abaikan kata tanya/fungsional sebagai subjek utama
                    if (
                        cat not in ["kata_tanya", "konfirmasi", "penolakan"]
                        and word not in self.stopwords
                    ):
                        key_subject = word
            else:
                unknown_words.append(word)

        return known_words, unknown_words, key_subject

    def baby_respond(self, prompt):
        """Logika utama respon ala bayi: Tanya jika tidak tahu, Jawab jika tahu"""
        known, unknown, subject = self.analyze_input(prompt)

        # Selalu simpan kalimat utuh ke memori
        if prompt not in self.sentence_memory:
            self.sentence_memory.append(prompt)
            if len(self.sentence_memory) > 1000:
                self.sentence_memory.pop(0)

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

            # Tambahkan cerita spontan di akhir
            spontaneous_story = self.try_spontaneous_story(subject)

            return main_response + spontaneous_story

    def get_meaningful_connection(self, word):
        """Mencari koneksi kata yang bermakna (bukan kata fungsional)"""
        if word not in self.neurons:
            return None

        connections = self.neurons[word]["connections"]
        if not connections:
            return None

        # Filter kata-kata yang tidak bermakna untuk respon
        meaningful_candidates = {
            k: v
            for k, v in connections.items()
            if k not in self.stopwords and k != word
        }

        if meaningful_candidates:
            return max(meaningful_candidates, key=meaningful_candidates.get)
        elif connections:
            # Fallback ke semua koneksi jika tidak ada yang bermakna
            return max(connections, key=connections.get)

        return None

    def reason_and_respond_fully_understood(self, prompt, subject):
        """Logika penalaran jika semua kata sudah dipahami"""
        lower_prompt = prompt.lower().strip()
        if lower_prompt in self.conversation_log:
            return self.conversation_log[lower_prompt]

        detected_cats = [
            self.neurons[w]["category"] for w in prompt.split() if w in self.neurons
        ]

        # Empati/Kondisi
        if any(c in ["kondisi", "fisik", "emosi"] for c in detected_cats):
            if subject and subject in self.neurons:
                related = list(self.neurons[subject]["connections"].keys())[:3]
                if related:
                    return f"Waduh, {subject}? Itu berhubungan dengan {', '.join(related)}. Kamu butuh bantuan?"

        # Fakta/Definisi
        if "kata_tanya" in detected_cats or "apa" in prompt.lower():
            if subject and subject in self.neurons:
                cat = self.neurons[subject].get("category", "hal")
                # Cek apakah ada definisi spesifik di conversation log
                for q, a in self.conversation_log.items():
                    if subject in q and ("apa itu" in q or "adalah" in a):
                        return a
                return f"'{subject}' adalah sebuah {cat}. Saya sudah paham itu!"

        # Fallback Interaktif (Menggunakan koneksi bermakna)
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
