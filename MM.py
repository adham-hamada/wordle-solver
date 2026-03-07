def feedback(s1,s2):
  s2 = list(s2)
  feedback=['']*5
  for i, (c1, c2) in enumerate(zip(s1, s2)):
    if c1 == c2:
      feedback[i]='g'
      s2[i]='#'
  for i, c in enumerate(s1):
    if (feedback[i]=='g' or feedback[i]=='y'):
      continue
    if c in s2:
      idx = s2.index(c)
      feedback[i]='y'
      s2[idx]='#'
    else:
      feedback[i]='r'
  return ''.join(feedback)

def pattern_str_to_code(s1):
  code = 0
  for i, c in enumerate(s1):
    if (s1[i]=='g'):
      code = code + 2*(3**i)
    elif (s1[i]=='y'):
      code = code + (3**i)
  return code

def code_to_pattern_str(n):
  if n == 0:
        return [0, 0, 0, 0, 0]

  digits = []
  while n > 0:
      digits.append(n % 3)
      n //= 3

  while len(digits) < 5:
      digits.append(0)

  feedback=['']*5
  for i, d in enumerate(digits):
    if d == 0:
        feedback[i] = 'r'
    elif d == 1:
        feedback[i] = 'y'
    elif d == 2:
        feedback[i] = 'g'
  return ''.join(feedback)

import json

with open('targets_5_letter.json', 'r') as f:
    targets = json.load(f)

with open('dictionary_5_letter.json', 'r') as f:
    guesses = json.load(f)

import numpy as np

def build_matrix(guesses, targets):
    G = len(guesses)
    A = len(targets)
    M = np.zeros((G, A), dtype=int)

    for i, guess in enumerate(guesses):
        for j, target in enumerate(targets):
            M[i, j] = pattern_str_to_code(feedback(guess, target))

    return M

X = build_matrix(guesses, targets)
np.save('pattern_matrix.npy', X)

M = np.load('pattern_matrix.npy')
print(M.shape)
print(M)