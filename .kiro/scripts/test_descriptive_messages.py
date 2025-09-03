#!/usr/bin/env python3
"""
Test script to verify that the AI generates descriptive commit messages
instead of generic ones
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from groq_client import GroqClient, GroqAPIError
from verbose_logger import enable_verbose_logging

def test_descriptive_messages():
    """Test various diff scenarios to ensure descriptive messages"""
    
    # Enable verbose logging to see the API calls
    enable_verbose_logging()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not set")
        return False
    
    try:
        config = Config()
        client = GroqClient(config)
        
        # Test cases with different types of changes
        test_cases = [
            {
                "name": "Adding a button to HTML",
                "diff": """diff --git a/index.html b/index.html
index abc123..def456 100644
--- a/index.html
+++ b/index.html
@@ -10,6 +10,7 @@
   <main>
     <p>Este es un ejemplo de una web básica con HTML.</p>
     <p>Puedes poner aquí tu contenido, imágenes o enlaces.</p>
+    <button onclick="showMenu()">Mostrar menú</button>
   </main>
 </body>""",
                "expected_keywords": ["botón", "button", "menú", "menu", "añade", "agrega"],
                "avoid_keywords": ["actualiza", "modifica", "cambios"]
            },
            {
                "name": "Adding a CSS class",
                "diff": """diff --git a/styles.css b/styles.css
index abc123..def456 100644
--- a/styles.css
+++ b/styles.css
@@ -5,6 +5,10 @@
   margin: 0;
   padding: 0;
 }
+
+.highlight {
+  background-color: yellow;
+  font-weight: bold;
+}""",
                "expected_keywords": ["clase", "class", "highlight", "estilo", "añade", "agrega"],
                "avoid_keywords": ["actualiza", "modifica", "cambios"]
            },
            {
                "name": "Adding a JavaScript function",
                "diff": """diff --git a/script.js b/script.js
index abc123..def456 100644
--- a/script.js
+++ b/script.js
@@ -1,3 +1,8 @@
 function init() {
   console.log("App initialized");
 }
+
+function validateEmail(email) {
+  const regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
+  return regex.test(email);
+}""",
                "expected_keywords": ["función", "function", "validar", "validate", "email", "añade", "agrega"],
                "avoid_keywords": ["actualiza", "modifica", "cambios"]
            },
            {
                "name": "Fixing a bug",
                "diff": """diff --git a/calculator.js b/calculator.js
index abc123..def456 100644
--- a/calculator.js
+++ b/calculator.js
@@ -2,7 +2,7 @@
 function divide(a, b) {
-  return a / b;
+  return b !== 0 ? a / b : 0;
 }""",
                "expected_keywords": ["fix", "corrige", "división", "divide", "cero", "error"],
                "avoid_keywords": ["actualiza", "modifica", "cambios"]
            }
        ]
        
        results = []
        
        print("🧪 Testing Descriptive Message Generation")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['name']}")
            print("-" * 40)
            
            try:
                message = client.generate_commit_message(test_case['diff'])
                print(f"Generated: '{message}'")
                
                # Check if message contains expected keywords
                message_lower = message.lower()
                found_expected = any(keyword.lower() in message_lower for keyword in test_case['expected_keywords'])
                found_avoided = any(keyword.lower() in message_lower for keyword in test_case['avoid_keywords'])
                
                if found_expected and not found_avoided:
                    print("✅ GOOD - Descriptive and specific")
                    results.append(True)
                elif found_expected and found_avoided:
                    print("⚠️  MIXED - Has good keywords but also generic ones")
                    results.append(False)
                else:
                    print("❌ BAD - Too generic or not descriptive")
                    results.append(False)
                
                print(f"Expected keywords: {test_case['expected_keywords']}")
                print(f"Should avoid: {test_case['avoid_keywords']}")
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                results.append(False)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"Descriptive messages: {passed}/{total}")
        
        if passed == total:
            print("🎉 All messages are descriptive and specific!")
            return True
        elif passed >= total * 0.7:
            print("⚠️  Most messages are good, but some could be more descriptive")
            return True
        else:
            print("❌ Messages are too generic. Need to improve the prompt.")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    success = test_descriptive_messages()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())