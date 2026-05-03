import google.generativeai as genai

GEMINI_KEY = "AIzaSyBq25kH8LZyVsL5_OPEyrLcxgEUYoV45gI"
genai.configure(api_key=GEMINI_KEY)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model: {m.name}")
except Exception as e:
    print(f"Error: {e}")
