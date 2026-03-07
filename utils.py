import numpy as np


class wordlesolver():
    def __init__(self , remaining_i , word , guess, data, target_list, guess_list, guess_index):
        self.remaining_i = remaining_i
        self.word = word
        self.guess = guess
        self.data = data
        self.target_list = target_list
        self.guess_list = guess_list
        self.guess_index = guess_index

    def get_pattern_code(self,word,guess):
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


    def feedback(self ,s1, s2):
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
    
    def pattern_str_to_code(self,s1):
        code = 0
        for i, c in enumerate(s1):
            if s1[i] == 'g':
                code = code + 2 * (3 ** i)
            elif s1[i] == 'y':
                code = code + (3 ** i)
        return code
    
    def pattern_code_to_str(self,code):
        base = {0:"r", 1:"y", 2:"g"}
        pattern =""
        for i in range(5):
            pattern+=base[(code)%3]
            code = int(code/3)
        return "".join(reversed(pattern))

    def get_entropy(self,guess_i,remaining_i):
        patterns = self.data[guess_i, remaining_i]  
        _, counts = np.unique(patterns, return_counts=True)
        probs = counts / len(remaining_i)
        return -np.sum(probs * np.log2(probs))
    
    def get_best_guess(self,remaining_i):
        best_guess = None
        best_entropy = -np.inf
        remaining_words = set(self.target_list[j] for j in remaining_i)

        candidates_to_search = (
            list(remaining_words)
            if len(remaining_i) <= 2
            else self.guess_list
        )

        for guess in candidates_to_search:
            i = self.guess_index[guess]
            entropy = self.get_entropy(i, remaining_i)

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
    
    def build_matrix(self,guess_list, target_list):
        G = len(guess_list)
        A = len(target_list)
        M = np.zeros((G, A), dtype=int)
        for i, guess in enumerate(guess_list):
            for j, target in enumerate(target_list):
                M[i, j] = self.pattern_str_to_code(self.feedback(guess, target))
        return M
