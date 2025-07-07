#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from utils.gpt.practice_exam import generate_practice_exam, parse_practice_exam

# Test with a simple text
test_text = """
Calculus is a branch of mathematics that deals with continuous change. The two main branches are differential calculus and integral calculus.

Differential calculus focuses on the rate of change of quantities. The derivative of a function f(x) at a point x is defined as:
f'(x) = lim(h→0) [f(x+h) - f(x)]/h

Integral calculus focuses on accumulation of quantities. The definite integral from a to b is:
∫[a,b] f(x) dx = F(b) - F(a)

The Fundamental Theorem of Calculus connects these two branches: if F'(x) = f(x), then ∫[a,b] f(x) dx = F(b) - F(a).
"""

print("Testing Basic Practice Exam Generation...")
print("=" * 50)

# Test basic level
raw_output_basic = generate_practice_exam(test_text, "Basic")
print("RAW OUTPUT (Basic):")
print(raw_output_basic)
print("\n" + "=" * 50)

# Parse the output
exam_data_basic = parse_practice_exam(raw_output_basic)
print("PARSED DATA (Basic):")
print(exam_data_basic)
print("\n" + "=" * 50)

print("Testing In-Depth Practice Exam Generation...")
print("=" * 50)

# Test in-depth level
raw_output_in_depth = generate_practice_exam(test_text, "In-Depth")
print("RAW OUTPUT (In-Depth):")
print(raw_output_in_depth)
print("\n" + "=" * 50)

# Parse the output
exam_data_in_depth = parse_practice_exam(raw_output_in_depth)
print("PARSED DATA (In-Depth):")
print(exam_data_in_depth) 