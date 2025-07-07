#!/usr/bin/env python3

import sys
sys.path.append('.')

from utils.gpt.practice_exam import fix_formatting_issues

# Test with problematic formatting
test_input = """
MULTIPLE CHOICE QUESTIONS:
1. What is 2+2?
A) 3
B) 4
C) 5
D) 6

1. What is the capital of France?
A) Berlin
B) Madrid
C) Paris
D) Rome

SHORT ANSWER QUESTIONS:
1. Explain calculus.
2. What is a derivative?

FILL IN THE BLANK QUESTIONS:
1. The capital of France is _____.
1. Calculus deals with _____ change.

ESSAY QUESTIONS:
1. Discuss the importance of calculus.
2. Explain the fundamental theorem.

ANSWER KEY AND SOLUTIONS:
1. B - 4 is correct
1. C - Paris is correct
1. Calculus is a branch of mathematics
2. A derivative measures rate of change
1. Paris
1. continuous
1. Calculus is fundamental to modern science
2. The fundamental theorem connects derivatives and integrals
"""

print("ORIGINAL TEXT:")
print(test_input)
print("\n" + "="*50)
print("FIXED TEXT:")
fixed = fix_formatting_issues(test_input)
print(fixed) 