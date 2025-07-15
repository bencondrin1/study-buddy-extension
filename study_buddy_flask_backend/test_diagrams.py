#!/usr/bin/env python3
"""
Test script for the diagrams feature.
This script tests the diagram generation without requiring an OpenAI API key.
"""

import os
import sys
sys.path.append('.')

from utils.gpt.diagrams import extract_mermaid_diagrams, convert_mermaid_to_svg

def test_mermaid_extraction():
    """Test extracting Mermaid diagrams from markdown content."""
    print("🧪 Testing Mermaid diagram extraction...")
    
    test_content = """
## Test Flowchart
This is a simple test flowchart.
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```

## Test Mind Map
This is a test mind map.
```mermaid
mindmap
  root((Main Concept))
    Sub Concept 1
      Detail 1
      Detail 2
    Sub Concept 2
      Detail 3
```

## Empty Diagram
This should be skipped.
```mermaid

```

## Invalid Diagram
This should be skipped.
```mermaid
just some text without diagram syntax
```
"""
    
    diagrams = extract_mermaid_diagrams(test_content)
    
    if len(diagrams) == 2:
        print("✅ Successfully extracted 2 valid diagrams (skipped 2 invalid ones)")
        for i, diagram in enumerate(diagrams, 1):
            print(f"   Diagram {i}: {diagram['title']}")
            print(f"   Description: {diagram['description']}")
            print(f"   Code length: {len(diagram['mermaid_code'])} characters")
    else:
        print(f"❌ Expected 2 diagrams, got {len(diagrams)}")
        return False
    
    return True

def test_mermaid_conversion():
    """Test converting Mermaid code to SVG."""
    print("\n🧪 Testing Mermaid to SVG conversion...")
    
    # Check if mermaid-cli is installed
    try:
        import subprocess
        result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ mermaid-cli is installed")
        else:
            print("❌ mermaid-cli is not working properly")
            return False
    except FileNotFoundError:
        print("❌ mermaid-cli is not installed")
        print("   Install it with: npm install -g @mermaid-js/mermaid-cli")
        return False
    
    # Test simple flowchart
    test_mermaid = """
graph TD
    A[Start] --> B[Process]
    B --> C[End]
"""
    
    svg_content = convert_mermaid_to_svg(test_mermaid)
    
    if svg_content and '<svg' in svg_content:
        print("✅ Successfully converted Mermaid to SVG")
        print(f"   SVG length: {len(svg_content)} characters")
        return True
    else:
        print("❌ Failed to convert Mermaid to SVG")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Diagrams Feature\n")
    
    success = True
    
    # Test diagram extraction
    if not test_mermaid_extraction():
        success = False
    
    # Test SVG conversion
    if not test_mermaid_conversion():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("✅ All tests passed! Diagrams feature is ready.")
    else:
        print("❌ Some tests failed. Please check the setup.")
    
    return success

if __name__ == "__main__":
    main() 