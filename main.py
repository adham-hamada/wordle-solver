import numpy as np
import math
import json

data = np.load("pattern_matrix.npy")

with open('dictionary_5_letter.json', 'r') as f:
    guess_list = json.load(f)
with open('targets_5_letter.json', 'r') as f:
    target_list = json.load(f)

G = len(guess_list)
A = len(target_list)

def get_pattern_code(word, guess):
    pattern = [0] * 5
    available = {}

    for i in range(5):
        if guess[i] == word[i]:
            pattern[i] = 2
        else:
            available[word[i]] = available.get(word[i],0)+1
    for i in range(5):
        if pattern[i]==0:
            if guess[i] in available and available[guess[i]]>0:
                pattern[i]=1
                available[guess[i]] -= 1
    return (pattern[4] * 81) + (pattern[3] * 27) + (pattern[2] * 9) + (pattern[1] * 3) + (pattern[0] * 1)

def make_pattern_matrix():
    pattern_matrix = np.zeros((G, A), dtype=np.uint8)
    for i, guess in enumerate(guess_list):
        for j, target in enumerate(target_list):
            pattern_matrix[i, j] = get_pattern_code(target, guess)
    np.save('pattern_matrix.npy', pattern_matrix)

guess_index = {word: i for i , word in enumerate(guess_list)}
target_index = {word: j for j , word in enumerate(target_list)}
# feedback encoding an integer [0,242]
def pattern_str_to_code(pattern):
    base = {"r": 0, "y": 1, "g": 2}
    code = 0
    for ind in range(5):
        code += base[pattern[ind]] * (3 ** ind)
    return code

def pattern_code_to_str(code):
    base = {0:"r", 1:"y", 2:"g"}
    pattern =""
    for i in range(5):
        pattern+=base[(code)%3]
        code = int(code/3)
    return "".join(reversed(pattern))


#entropy-based ranking

def get_entropy(guess_i,remaining_i):
    patterns = data[guess_i, remaining_i]  
    _, counts = np.unique(patterns, return_counts=True)
    probs = counts / len(remaining_i)
    return -np.sum(probs * np.log2(probs))

def get_best_guess(remaining_i):
    best_guess = None
    best_entropy = -np.inf
    # Fix: compare words, not indices from different lists
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
            guess in remaining_words and          # Fix: word-level check
            best_guess not in remaining_words     # Fix: word-level check
        )

        if is_better or is_tie_and_preferred:
            best_entropy = entropy
            best_guess = guess

    return best_guess


# def main():
#     remaining_i = np.arange(A)

#     while len(remaining_i) >= 1:
#         best_guess = get_best_guess(remaining_i)
#         print("BEST:",best_guess)
#         feedback = input().strip()
#         feedback_code = pattern_str_to_code(feedback)

#         guess_i = guess_index[best_guess]
#         filter_data = data[guess_i,remaining_i] == feedback_code
#         remaining_i = remaining_i[filter_data]

def main():
    remaining_i = np.arange(A)

    while len(remaining_i) >= 1:  # Fixed: was >= 1
        best_guess = get_best_guess(remaining_i)
        print(f"BEST: {best_guess}  ({len(remaining_i)} candidates remaining)")

        feedback = input().strip()

        # Win condition: correct guess
        if feedback == "ggggg":
            print("Solved:", best_guess)
            return

        feedback_code = pattern_str_to_code(feedback)
        guess_i = guess_index[best_guess]

        filter_data = data[guess_i, remaining_i] == feedback_code
        remaining_i = remaining_i[filter_data]

        # Guard: invalid feedback wiped all candidates
        if len(remaining_i) == 0:
            print("No candidates left — check your feedback input.")
            return

    # Only one candidate left — it must be the answer
    if len(remaining_i) == 1:
        print("Answer:", target_list[remaining_i[0]])
    else:
        print("No solution found.")

main()




