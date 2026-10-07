import random
import json

class PikoBrain:
    def __init__(self):
        # Neuron disimpan sebagai dictionary: {kata: {kata_terkait: weight}}
        self.neurons = {} 
        self.learning_rate = 0.1

    def add_word(self, word, category="unknown"):
        """Menambahkan neuron baru jika kata belum ada"""
        if word not in self.neurons:
            self.neurons[word] = {"category": category, "connections": {}}
            print(f"🧠 Neuron baru terbentuk untuk kata: '{word}'")

    def connect(self, word1, word2, strength=1.0):
        """Menghubungkan dua kata (belajar asosiasi)"""
        self.add_word(word1)
        self.add_word(word2)
        
        # Update koneksi dua arah
        self.neurons[word1]["connections"][word2] = \
            self.neurons[word1]["connections"].get(word2, 0) + strength
        self.neurons[word2]["connections"][word1] = \
            self.neurons[word2]["connections"].get(word1, 0) + strength

    def learn_from_interaction(self, user_input, feedback):
        """
        Belajar dari koreksi manusia.
        feedback: 'reward' (benar) atau 'penalty' (salah)
        """
        words = user_input.lower().split()
        multiplier = 1.0 if feedback == 'reward' else -1.0
        
        # Perkuat koneksi antar kata dalam kalimat yang sama
        for i in range(len(words)):
            for j in range(i+1, len(words)):
                self.connect(words[i], words[j], strength=self.learning_rate * multiplier)

    def ask_what_is(self, word):
        """Menjawab 'Apa itu X?'"""
        if word in self.neurons:
            cats = self.neurons[word].get("category", "tidak diketahui")
            related = list(self.neurons[word]["connections"].keys())[:3]
            return f"'{word}' adalah sebuah {cats}. Terkait dengan: {', '.join(related)}."
        return f"Saya belum tahu apa itu '{word}'. Boleh ajari saya?"

    def ask_is_disease(self, word):
        """Menjawab 'Apakah X penyakit?'"""
        if word in self.neurons:
            cat = self.neurons[word].get("category", "")
            return "Ya" if cat == "disease" else "Bukan"
        return "Saya belum punya data tentang itu."

    def ask_diagnosis(self, symptoms_input):
        """Mencoba mendiagnosa berdasarkan gejala"""
        symptoms = [s.strip() for s in symptoms_input.split(",")]
        scores = {}
        
        for word, data in self.neurons.items():
            if data["category"] == "disease":
                score = 0
                disease_syms = data.get("symptoms", []) # Jika ada data gejala spesifik
                connections = data["connections"]
                
                for sym in symptoms:
                    if sym in connections:
                        score += connections[sym]
                    elif sym in disease_syms:
                        score += 2.0 # Bonus jika cocok dengan definisi gejala
                
                if score > 0:
                    scores[word] = score
        
        if scores:
            best_match = max(scores, key=scores.get)
            return best_match
        return "Tidak terdeteksi, coba tanya dokter."

    def generate_sentence(self, start_word):
        """Kemampuan dasar berbicara: merangkai kata berdasarkan koneksi terkuat"""
        sentence = [start_word]
        current = start_word
        for _ in range(5): # Maksimal 5 kata tambahan
            if current not in self.neurons: break
            connections = self.neurons[current]["connections"]
            if not connections: break
            
            # Pilih kata berikutnya berdasarkan weight tertinggi
            next_word = max(connections, key=connections.get)
            if next_word in sentence: break # Hindari loop
            
            sentence.append(next_word)
            current = next_word
            
        return " ".join(sentence)