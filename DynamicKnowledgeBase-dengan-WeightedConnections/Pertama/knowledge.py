# Data awal berbasis kata, bukan angka
INITIAL_KNOWLEDGE = {
    "kepala": {"type": "body_part", "related": ["sakit", "pusing"]},
    "sakit": {"type": "condition", "related": ["nyeri", "pegal"]},
    "pusing": {"type": "symptom", "related": ["berkunang-kunang", "mual"]},
    "diagnosa": {"type": "concept", "related": ["penyakit", "kondisi"]},
    "penyakit": {"type": "concept", "related": ["flu", "demam", "migrain"]},
    "migrain": {"type": "disease", "symptoms": ["pusing", "nyeri", "cahaya"]},
    "flu": {"type": "disease", "symptoms": ["demam", "batuk", "pilek"]}
}