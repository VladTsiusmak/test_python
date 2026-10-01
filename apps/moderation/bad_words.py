import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, 'obscene_dictionary.txt')
with open(file_path, 'r', encoding='utf-8') as f:
    BAD_WORDS = [line.strip().lower() for line in f if line.strip()]