#!/usr/bin/env python3
"""
Test script to verify the detailed commit message fix.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from message_generator import MessageGenerator

def test_detailed_fix():
    """Test that the detailed parameter works correctly."""
    
    # Sample diff content
    sample_diff = """diff --git a/index.html b/index.html
index 1234567..abcdefg 100644
--- a/index.html
+++ b/index.html
@@ -10,6 +10,7 @@
     <div class="header">
         <h1>My Website</h1>
+        <button class="contact-btn">Contact Us</button>
     </div>
 
diff --git a/styles.css b/styles.css
index 2345678..bcdefgh 100644
--- a/styles.css
+++ b/styles.css
@@ -15,6 +15,12 @@
     color: #333;
 }
 
+.contact-btn {
+    background: #007bff;
+    color: white;
+    padding: 10px 20px;
+}
+
 .footer {
     margin-top: 50px;
"""
    
    files = ['index.html', 'styles.css']
    
    print("Testing detailed commit message fix...")
    print("=" * 50)
    
    config = Config()
    generator = MessageGenerator(config)
    
    # Test standard message
    print("\n1. STANDARD MESSAGE:")
    print("-" * 30)
    try:
        standard_msg = generator.generate_message(sample_diff, files, detailed=False)
        print(f"✅ Standard: {standard_msg}")
    except Exception as e:
        print(f"❌ Standard failed: {e}")
    
    # Test detailed message
    print("\n2. DETAILED MESSAGE:")
    print("-" * 30)
    try:
        detailed_msg = generator.generate_message(sample_diff, files, detailed=True)
        print(f"✅ Detailed: {detailed_msg}")
    except Exception as e:
        print(f"❌ Detailed failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_detailed_fix()