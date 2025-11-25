import google.generativeai as genai
import os

print(f"GenAI Version: {genai.__version__}")

try:
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    print("\nHarmCategory members:")
    for member in HarmCategory:
        print(f"  {member.name}: {member.value}")
        
    print("\nHarmBlockThreshold members:")
    for member in HarmBlockThreshold:
        print(f"  {member.name}: {member.value}")

except ImportError:
    print("Could not import types directly.")
    print(dir(genai))
