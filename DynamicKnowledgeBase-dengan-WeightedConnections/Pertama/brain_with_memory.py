import json
import os

class PikoBrain:
    def __init__(self, save_file="piko_memory.json"):
        self.neurons = {} 
        self.save_file = save_file
        self.learning_rate = 0.1
        self.load_memory() # Muat ingatan lama saat dimulai

    def load_memory(self):
        """Memuat ingatan dari file jika ada"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    self.neurons = json.load(f)
                print(f"🧠 Memori dimuat dari {self.save_file}")
            except:
                print("⚠️ Gagal memuat memori, memulai dari nol.")
        else:
            print("🆕 Memori baru dibuat.")

    def save_memory(self):
        """Menyimpan ingatan ke file secara otomatis"""
        with open(self.save_file, 'w') as f:
            json.dump(self.neurons, f, indent=2)
        # print("💾 Memori disimpan.") # Bisa di-comment agar tidak spam

    def add_word(self, word, category="unknown"):
        if word not in self.neurons:
            self.neurons[word] = {"category": category, "connections": {}}
            self.save_memory() # Simpan segera setelah ada neuron baru
            print(f"🧠 Neuron baru terbentuk: '{word}'")

    def connect(self, word1, word2, strength=1.0):
        self.add_word(word1)
        self.add_word(word2)
        
        # Update koneksi
        curr_w1 = self.neurons[word1]["connections"].get(word2, 0)
        self.neurons[word1]["connections"][word2] = curr_w1 + strength
        
        curr_w2 = self.neurons[word2]["connections"].get(word1, 0)
        self.neurons[word2]["connections"][word1] = curr_w2 + strength
        
        self.save_memory() # Simpan setiap ada koneksi baru

    # ... (fungsi ask_what_is, learn_from_interaction, dll tetap sama) ...
    def learn_from_interaction(self, user_input, feedback):
        words = user_input.lower().split()
        multiplier = 1.0 if feedback == 'reward' else -1.0
        for i in range(len(words)):
            for j in range(i+1, len(words)):
                self.connect(words[i], words[j], strength=self.learning_rate * multiplier)