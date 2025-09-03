#!/usr/bin/env python3
"""
Test with a real example using the actual index.html file
"""

import sys
import os
from pathlib import Path

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from groq_client import GroqClient, GroqAPIError
from verbose_logger import enable_verbose_logging

def test_real_html_change():
    """Test with a realistic HTML change"""
    
    enable_verbose_logging()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not set")
        return False
    
    try:
        config = Config()
        client = GroqClient(config)
        
        # Simulate adding a contact button to the existing HTML
        real_diff = """diff --git a/index.html b/index.html
index abc123..def456 100644
--- a/index.html
+++ b/index.html
@@ -15,6 +15,8 @@
     <a href="https://www.youtube.com" target="_blank">Ir a YouTube</a>

     <br><br>
+    
+    <button onclick="showContact()">Contactar</button>

     <button onclick="alert('¡Has pulsado el botón!')">Haz clic aquí</button>
   </main>"""
        
        print("🧪 Testing Real HTML Change")
        print("=" * 50)
        print("Diff:")
        print(real_diff)
        print("\n" + "=" * 50)
        
        message = client.generate_commit_message(real_diff)
        
        print(f"Generated message: '{message}'")
        
        # Check if it's descriptive
        if any(keyword in message.lower() for keyword in ['contactar', 'contact', 'botón', 'button', 'añade', 'agrega']):
            if not any(generic in message.lower() for generic in ['actualiza', 'modifica', 'cambios']):
                print("✅ EXCELLENT - Descriptive and specific!")
                return True
            else:
                print("⚠️  MIXED - Has good keywords but also generic ones")
                return False
        else:
            print("❌ BAD - Too generic")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    success = test_real_html_change()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())