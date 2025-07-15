#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.gpt.diagrams import generate_diagrams, extract_mermaid_diagrams, clean_mermaid_code

def test_diagram_generation():
    """Test the diagram generation process step by step."""
    
    # Test with a simple, clear example
    test_text = """
    Integration Methods:
    
    The trapezoidal rule approximates the definite integral by dividing the area under the curve into trapezoids.
    Simpson's rule uses quadratic polynomials to approximate the function and provides better accuracy.
    Both methods are numerical integration techniques used when analytical integration is difficult.
    
    The process involves:
    1. Dividing the interval into subintervals
    2. Approximating the function on each subinterval
    3. Summing the areas to get the total approximation
    """
    
    print("=" * 60)
    print("TESTING DIAGRAM GENERATION")
    print("=" * 60)
    
    print(f"\n📝 Input text length: {len(test_text)} characters")
    print(f"📝 Input text preview: {test_text[:200]}...")
    
    # Step 1: Generate raw content from GPT
    print(f"\n🔍 Step 1: Generating raw content from GPT...")
    raw_content = generate_diagrams(test_text, "basic", "flowchart")
    print(f"📝 Raw GPT response length: {len(raw_content)} characters")
    print(f"📝 Raw GPT response preview:")
    print("-" * 40)
    print(raw_content[:1000])
    print("-" * 40)
    
    # Step 2: Extract diagrams
    print(f"\n🔍 Step 2: Extracting diagrams...")
    diagrams = extract_mermaid_diagrams(raw_content)
    print(f"📊 Found {len(diagrams)} diagrams")
    
    for i, diagram in enumerate(diagrams, 1):
        print(f"\n📊 Diagram {i}:")
        print(f"   Title: {diagram['title']}")
        print(f"   Description: {diagram['description']}")
        print(f"   Mermaid code length: {len(diagram['mermaid_code'])}")
        print(f"   Mermaid code preview:")
        print("-" * 30)
        print(diagram['mermaid_code'][:500])
        print("-" * 30)
    
    # Step 3: Test cleaning on each diagram
    if diagrams:
        print(f"\n🔍 Step 3: Testing cleaning process...")
        for i, diagram in enumerate(diagrams, 1):
            print(f"\n🧹 Cleaning diagram {i}...")
            original_code = diagram['mermaid_code']
            cleaned_code = clean_mermaid_code(original_code)
            
            print(f"   Original length: {len(original_code)}")
            print(f"   Cleaned length: {len(cleaned_code)}")
            print(f"   Original code:")
            print("-" * 20)
            print(original_code)
            print("-" * 20)
            print(f"   Cleaned code:")
            print("-" * 20)
            print(cleaned_code)
            print("-" * 20)
    else:
        print(f"\n❌ No diagrams found in GPT response!")
        print(f"   This suggests the GPT response format is not what we expect.")
        print(f"   Raw response was: {raw_content}")

if __name__ == "__main__":
    test_diagram_generation() 