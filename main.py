import numpy as np
import math
import json
import os
from utils import wordlesolver

with open('dictionary_5_letter.json', 'r') as f:
    guess_list = json.load(f)
with open('targets_5_letter.json', 'r') as f:
    target_list = json.load(f)

guess_index  = {word: i for i, word in enumerate(guess_list)}
target_index = {word: j for j, word in enumerate(target_list)}

solver = wordlesolver(
    remaining_i = np.arange(len(target_list)),
    word        = "",          
    guess       = "",          
    data        = None,        
    target_list = target_list,
    guess_list  = guess_list,
    guess_index = guess_index,
)


if not os.path.exists('pattern_matrix.npy'):
    X = solver.build_matrix(guess_list, target_list)
    np.save('pattern_matrix.npy', X)

data = np.load("pattern_matrix.npy")
solver.data = data

def main():
    remaining_i = np.arange(len(target_list))
    while True:
        prior_H = math.log2(len(remaining_i)) if len(remaining_i) > 1 else 0.0

        best_guess, best_H_Y = solver.get_best_guess(remaining_i)

        posterior_H = prior_H - best_H_Y
        info_gain   = best_H_Y

        print(f"Candidates remaining : {len(remaining_i)}")
        print(f"H(W)                 = {prior_H:.4f} bits")
        print(f"H(Y) best guess      = {best_H_Y:.4f} bits  (word: {best_guess})")
        print(f"H(W|Y)               = {posterior_H:.4f} bits")
        print(f"I(W;Y)               = {info_gain:.4f} bits")

        print(f"BEST={best_guess}")

        guess_input = input().strip()

        feedback_str = input().strip()

        if feedback_str == "ggggg":
            print(f"Solved: {guess_input}")
            return

        feedback_code = solver.pattern_str_to_code(feedback_str)

        if guess_input not in guess_index:
            print("Unknown guess word — aborting.")
            return

        guess_i = guess_index[guess_input]
        filter_data = data[guess_i, remaining_i] == feedback_code
        remaining_i = remaining_i[filter_data]

        if len(remaining_i) == 0:
            print("No candidates left — check your feedback input.")
            return

        if len(remaining_i) == 1:
            only_word = target_list[remaining_i[0]]
            print(f"Candidates remaining : 1")
            print(f"H(W)                 = 0.0000 bits")
            print(f"H(Y) best guess      = 0.0000 bits  (word: {only_word})")
            print(f"H(W|Y)               = 0.0000 bits")
            print(f"I(W;Y)               = 0.0000 bits")
            print(f"BEST={only_word}")

            guess_input  = input().strip()
            feedback_str = input().strip()
            print(f"Solved: {guess_input}")
            return
        
if __name__ == "__main__":
    main()