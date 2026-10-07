from brain import PikoBrain
from knowledge import INITIAL_KNOWLEDGE

def init_brain():
    brain = PikoBrain()
    # Masukkan data awal ke dalam otak
    for word, info in INITIAL_KNOWLEDGE.items():
        brain.add_word(word, info["type"])
        for rel in info.get("related", []):
            brain.connect(word, rel)
        if "symptoms" in info:
            for sym in info["symptoms"]:
                brain.connect(word, sym, strength=2.0) # Koneksi kuat untuk gejala
    return brain

def main():
    brain = init_brain()
    print("👋 Halo! Saya Piko. Saya siap belajar.")
    print("Perintah: 'apa itu [kata]', 'apakah [kata] penyakit?', 'apa diagnosanya? [gejala]', 'kalimat [kata]', atau ketik bebas untuk belajar.")
    
    while True:
        user_input = input("\nKamu: ")
        if user_input.lower() == 'exit': break
        
        parts = user_input.lower().split(maxsplit=2)
        command = parts[0]
        
        # --- Mode Pertanyaan ---
        if command == "apa" and len(parts) > 2 and parts[1] == "itu":
            word = parts[2]
            print(f"Piko: {brain.ask_what_is(word)}")
            
        elif command == "apakah" and len(parts) > 2 and parts[2] == "penyakit?":
            word = parts[1]
            print(f"Piko: {brain.ask_is_disease(word)}")
            
        elif command == "apa" and len(parts) > 1 and parts[1] == "diagnosanya?":
            symptoms = parts[2] if len(parts) > 2 else ""
            print(f"Piko: Diagnosa kemungkinan: {brain.ask_diagnosis(symptoms)}")
            
        elif command == "kalimat":
            word = parts[1] if len(parts) > 1 else "saya"
            print(f"Piko: {brain.generate_sentence(word)}")

        # --- Mode Belajar & Koreksi ---
        else:
            # AI mencoba merespons atau belajar
            print(f"Piko: Saya mencatat '{user_input}'. Apakah ini informasi yang benar? (y/n)")
            feedback_input = input("Koreksi: ")
            
            if feedback_input.lower() == 'y':
                brain.learn_from_interaction(user_input, 'reward')
                print("Piko: Terima kasih! Koneksi saraf saya menguat.")
            else:
                brain.learn_from_interaction(user_input, 'penalty')
                print("Piko: Maaf, saya akan lupa pola itu.")

if __name__ == "__main__":
    main()