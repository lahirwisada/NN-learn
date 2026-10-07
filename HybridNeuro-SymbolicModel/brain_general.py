import json
import os
import random
import re
from html.parser import HTMLParser
from collections import defaultdict
from initial_knowledge import INITIAL_KNOWLEDGE


# --- Helper untuk membersihkan HTML ---
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        # Abaikan script dan style
        if tag in ["script", "style"]:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ["script", "style"]:
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            clean_data = data.strip()
            if clean_data:
                self.text.append(clean_data)

    def get_text(self):
        return " ".join(self.text)


class GeneralPikoBrain:
    def __init__(self, save_file="piko_general_memory.json"):
        self.neurons = {}
        self.ngram_model = defaultdict(lambda: defaultdict(int))
        self.conversation_log = {}
        self.sentence_memory = []
        self.save_file = save_file
        self.learning_rate = 0.1

        # Stopwords untuk filter koneksi bermakna
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
            "sih",
            "ya",
            "oh",
            "ah",
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
    # FILE LEARNING FEATURES (TXT & HTML)
    # ------------------------------------------------------------------
    def learn_from_txt(self, filepath):
        """Belajar dari file teks biasa (.txt)"""
        if not os.path.exists(filepath):
            print(f"❌ File {filepath} tidak ditemukan.")
            return

        print(f"📖 Membaca file teks: {filepath}...")
        count_lines = 0
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and len(line) > 3:  # Abaikan baris kosong/terlalu pendek
                        self._learn_text_internal(line)
                        count_lines += 1
            self.save_memory()
            print(f"✅ Selesai mempelajari {count_lines} baris dari {filepath}.")
        except Exception as e:
            print(f"❌ Gagal membaca file teks: {e}")

    def learn_from_html(self, filepath):
        """Belajar dari file HTML dengan membersihkan tag"""
        if not os.path.exists(filepath):
            print(f"❌ File {filepath} tidak ditemukan.")
            return

        print(f"🌐 Membaca file HTML: {filepath}...")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html_content = f.read()

            parser = TextExtractor()
            parser.feed(html_content)
            clean_text = parser.get_text()

            # Pecah teks panjang menjadi kalimat-kalimat berdasarkan tanda baca
            sentences = re.split(r"[.!?]+", clean_text)

            count_sentences = 0
            for sentence in sentences:
                s = sentence.strip()
                if (
                    s and len(s.split()) > 3
                ):  # Hanya pelajari kalimat yang cukup panjang
                    self._learn_text_internal(s)
                    count_sentences += 1

            self.save_memory()
            print(f"✅ Selesai mempelajari {count_sentences} kalimat dari {filepath}.")

        except Exception as e:
            print(f"❌ Gagal membaca file HTML: {e}")

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
        """Normalisasi teks untuk key dictionary"""
        text = text.lower().strip()
        text = re.sub(r"[.,?!\'\";:]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def _add_to_conversation_log(self, question, answer):
        key = self._normalize_key(question)
        if key not in self.conversation_log:
            self.conversation_log[key] = []
        if isinstance(self.conversation_log[key], str):
            self.conversation_log[key] = [self.conversation_log[key]]
        if answer not in self.conversation_log[key]:
            self.conversation_log[key].append(answer)

    def teach_response(self, question, answer):
        key = question.lower().strip()
        self._add_to_conversation_log(key, answer)
        self._learn_text_internal(question)
        self._learn_text_internal(answer)
        self.save_memory()
        print(f"💡 Piko belajar: '{question}' -> '{answer}'")

    # ------------------------------------------------------------------
    # STORYTELLING & GENERATION
    # ------------------------------------------------------------------
    def generate_novel_sentence(self, topic_word=None):
        candidates = []
        if topic_word and topic_word.lower() not in self.stopwords:
            candidates = [
                s for s in self.sentence_memory if topic_word.lower() in s.lower()
            ]

        if not candidates:
            worthy_sentences = [
                s
                for s in self.sentence_memory
                if len(s.split()) > 4
                and any(w not in self.stopwords for w in s.lower().split())
            ]
            if worthy_sentences:
                candidates = worthy_sentences
            else:
                candidates = self.sentence_memory

        if not candidates:
            return None

        template = random.choice(candidates).split()
        new_sentence = []

        for word in template:
            clean_word = word.strip(".,?!'\"").lower()
            if clean_word in self.stopwords:
                new_sentence.append(word)
                continue

            if random.random() < 0.3 and clean_word in self.neurons:
                connections = self.neurons[clean_word]["connections"]
                if connections:
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
        if not subject or subject.lower() in self.stopwords:
            return ""
        if subject not in self.neurons:
            return ""

        connections = self.neurons[subject]["connections"]
        meaningful_connections = {
            k: v for k, v in connections.items() if k not in self.stopwords
        }

        if not meaningful_connections:
            return ""

        if random.random() < 0.2:
            story = self.generate_novel_sentence(subject)
            if story:
                return f"\n\nNgomong-ngomong, {story}"
        return ""

    # ------------------------------------------------------------------
    # BABY LEARNING LOGIC
    # ------------------------------------------------------------------
    def analyze_input(self, prompt):
        words = prompt.lower().split()
        known_words = []
        unknown_words = []
        key_subject = None

        ignore_as_subject = [
            "ceritakan",
            "cerita",
            "jelaskan",
            "apa",
            "siapa",
            "bagaimana",
            "kenapa",
            "dimana",
            "kapan",
            "tentang",
            "mengenai",
            "soal",
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
        normalized_prompt = self._normalize_key(prompt)
        if normalized_prompt in self.conversation_log:
            answers = self.conversation_log[normalized_prompt]
            if isinstance(answers, list):
                return random.choice(answers)
            return answers

        known, unknown, subject = self.analyze_input(prompt)

        if prompt not in self.sentence_memory:
            self.sentence_memory.append(prompt)
            if len(self.sentence_memory) > 1000:
                self.sentence_memory.pop(0)

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

        if unknown:
            questions = unknown[:3]
            response_parts = []
            if known:
                response_parts.append(", ".join(known[:3]))
            question_str = ", ".join([f"apa itu '{w}'?" for w in questions])
            if response_parts:
                return f"{', '.join(response_parts)}... {question_str}"
            else:
                return f"Saya tidak mengerti. {question_str}"

        else:
            main_response = self.reason_and_respond_fully_understood(prompt, subject)
            spontaneous_story = self.try_spontaneous_story(subject)
            return main_response + spontaneous_story

    def get_meaningful_connection(self, word):
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
        normalized_prompt = self._normalize_key(prompt)
        if normalized_prompt in self.conversation_log:
            answers = self.conversation_log[normalized_prompt]
            if isinstance(answers, list):
                return random.choice(answers)
            return answers

        detected_cats = [
            self.neurons[w]["category"] for w in prompt.split() if w in self.neurons
        ]

        if any(
            c in ["kondisi", "fisik", "emosi", "anggota_tubuh"] for c in detected_cats
        ):
            if subject and subject in self.neurons:
                related = list(self.neurons[subject]["connections"].keys())[:3]
                if related:
                    return f"Waduh, {subject}? Itu berhubungan dengan {', '.join(related)}. Kamu butuh bantuan?"

        if (
            "kata_tanya" in detected_cats
            or "apa" in prompt.lower()
            or "siapa" in prompt.lower()
        ):
            if subject and subject in self.neurons:
                cat = self.neurons[subject].get("category", "hal")
                for q, a_list in self.conversation_log.items():
                    if subject in q and ("apa itu" in q or "definisi" in q):
                        answers = a_list if isinstance(a_list, list) else [a_list]
                        desc_answers = [a for a in answers if "adalah" in a.lower()]
                        if desc_answers:
                            return random.choice(desc_answers)
                return f"Menurut catatan saya, '{subject}' itu termasuk {cat}. Tapi saya masih ingin tahu lebih banyak dari kamu!"

        if subject and subject in self.neurons:
            best_match = self.get_meaningful_connection(subject)
            if best_match:
                responses = [
                    f"Ya, {subject} memang berkaitan erat dengan {best_match}.",
                    f"Menarik! Saya ingat {subject} sering disebut bersama {best_match}.",
                    f"Betul, {subject} dan {best_match} punya hubungan yang kuat di ingatan saya.",
                ]
                return random.choice(responses)
            else:
                return f"Saya tahu '{subject}', tapi saya belum banyak tahu hubungannya dengan hal lain."

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
