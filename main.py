import numpy as np

import json

with open('dictionary_5_letter.json', 'r') as f:
    guess_list = json.load(f)
with open('targets_5_letter.json', 'r') as f:
    target_list = json.load(f)

G = len(guess_list)
A = len(target_list)

def get_pattern_code(word, guess):
    pattern = [0] * 5
    for i in range(5):
        if guess[i] == word[i]:
            pattern[i] = 2
        elif guess[i] in word:
            pattern[i] = 1
    return pattern[0] * 27 + pattern[1] * 9 + pattern[2] * 3 + pattern[3] * 1 + pattern[4] * 0

pattern_matrix = np.zeros((G, A), dtype=int)
for i, guess in enumerate(guess_list):
    for j, target in enumerate(target_list):
        pattern_matrix[i, j] = get_pattern_code(target, guess)
np.save('pattern_matrix.npy', pattern_matrix)

