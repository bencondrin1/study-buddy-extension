#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.gpt.diagrams import generate_diagrams, extract_mermaid_diagrams, clean_mermaid_code

def test_complex_diagram():
    """Test with more complex mathematical content that might cause issues."""
    
    # Test with complex mathematical content
    test_text = """
    Advanced Integration Methods:
    
    The definite integral ∫[a,b] f(x)dx can be approximated using various numerical methods.
    
    Trapezoidal Rule: T = (h/2)[f(x₀) + 2f(x₁) + 2f(x₂) + ... + 2f(xₙ₋₁) + f(xₙ)]
    where h = (b-a)/n and xᵢ = a + ih for i = 0,1,2,...,n
    
    Simpson's Rule: S = (h/3)[f(x₀) + 4f(x₁) + 2f(x₂) + 4f(x₃) + 2f(x₄) + ... + 4f(xₙ₋₁) + f(xₙ)]
    where n must be even and h = (b-a)/n
    
    Error Analysis:
    - Trapezoidal Rule error: |E_T| ≤ (b-a)³M₂/(12n²) where M₂ = max|f''(x)| on [a,b]
    - Simpson's Rule error: |E_S| ≤ (b-a)⁵M₄/(180n⁴) where M₄ = max|f⁽⁴⁾(x)| on [a,b]
    
    The process involves:
    1. Choosing the number of subintervals n
    2. Calculating the step size h = (b-a)/n
    3. Evaluating the function at the required points
    4. Applying the appropriate formula
    5. Computing the error bounds
    """
    
    print("=" * 60)
    print("TESTING COMPLEX DIAGRAM GENERATION")
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
            
            if len(cleaned_code.strip()) == 0:
                print(f"   ❌ WARNING: Cleaning removed ALL content!")
            elif len(cleaned_code.strip()) < 10:
                print(f"   ⚠️ WARNING: Cleaning removed most content!")
    else:
        print(f"\n❌ No diagrams found in GPT response!")
        print(f"   This suggests the GPT response format is not what we expect.")
        print(f"   Raw response was: {raw_content}")

if __name__ == "__main__":
    test_complex_diagram() 