import re

def min_remaining_length(seq: str) -> int:
    a_count = 0
    b_count = 0

    for char in seq:
        if char == 'A':
            a_count += 1
        elif char == 'B':
            if b_count > 0:
                b_count -= 1
            else:
                b_count += 1

    return a_count + b_count
  
seq = "BABAAABABABABBAAABB"

print(min_remaining_length(seq))