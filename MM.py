import numpy as np
import math
import json


def feedback(s1, s2):
    s2 = list(s2)
    fb = [''] * 5
    for i, (c1, c2) in enumerate(zip(s1, s2)):
        if c1 == c2:
            fb[i] = 'g'
            s2[i] = '#'
    for i, c in enumerate(s1):
        if fb[i] == 'g' or fb[i] == 'y':
            continue
        if c in s2:
            idx = s2.index(c)
            fb[i] = 'y'
            s2[idx] = '#'
        else:
            fb[i] = 'r'
    return ''.join(fb)

def pattern_str_to_code(s1):
    code = 0
    for i, c in enumerate(s1):
        if s1[i] == 'g':
            code = code + 2 * (3 ** i)
        elif s1[i] == 'y':
            code = code + (3 ** i)
    return code

def code_to_pattern_str(n):
    if n == 0:
        return 'rrrrr'
    digits = []
    while n > 0:
        digits.append(n % 3)
        n //= 3
    while len(digits) < 5:
        digits.append(0)
    mapping = {0: 'r', 1: 'y', 2: 'g'}
    return ''.join(mapping[d] for d in digits)


with open('targets_5_letter.json', 'r') as f:
    target_list = json.load(f)

with open('dictionary_5_letter.json', 'r') as f:
    guess_list = json.load(f)

G = len(guess_list)
A = len(target_list)


def build_matrix(guesses, targets):
    G = len(guesses)
    A = len(targets)
    M = np.zeros((G, A), dtype=int)
    for i, guess in enumerate(guesses):
        for j, target in enumerate(targets):
            M[i, j] = pattern_str_to_code(feedback(guess, target))
    return M

import os

if not os.path.exists('pattern_matrix.npy'):
    print("Building pattern matrix, this may take a while...")
    X = build_matrix(guess_list, target_list)
    np.save('pattern_matrix.npy', X)
    print("Pattern matrix saved.")

data = np.load("pattern_matrix.npy") 
guess_index  = {word: i for i, word in enumerate(guess_list)}
target_index = {word: j for j, word in enumerate(target_list)}

def get_entropy(guess_i, remaining_i):
    patterns = data[guess_i, remaining_i]
    _, counts = np.unique(patterns, return_counts=True)
    probs = counts / len(remaining_i)
    return -np.sum(probs * np.log2(probs))

def get_best_guess(remaining_i):
    best_guess = None
    best_entropy = -np.inf
    remaining_words = set(target_list[j] for j in remaining_i)

    candidates_to_search = (
        list(remaining_words)
        if len(remaining_i) <= 2
        else guess_list
    )

    for guess in candidates_to_search:
        i = guess_index[guess]
        entropy = get_entropy(i, remaining_i)

        is_better = entropy > best_entropy
        is_tie_and_preferred = (
            entropy == best_entropy and
            guess in remaining_words and
            best_guess not in remaining_words
        )

        if is_better or is_tie_and_preferred:
            best_entropy = entropy
            best_guess = guess

    return best_guess, best_entropy

def main():
    remaining_i = np.arange(A)

    while True:
        prior_H = math.log2(len(remaining_i)) if len(remaining_i) > 1 else 0.0

        best_guess, best_H_Y = get_best_guess(remaining_i)

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

        feedback_code = pattern_str_to_code(feedback_str)

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

main()