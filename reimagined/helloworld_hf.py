import os
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

def main():
    model_name = os.getenv('HUGGINGFACE_MODEL')
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    
    if not model_name:
        raise ValueError("HUGGINGFACE_MODEL environment variable not set")
    if not api_key:
        raise ValueError("HUGGINGFACE_API_KEY environment variable not set")
    
    print(f"Using model: {model_name}")
    
    try:
        generator = pipeline("text2text-generation", model=model_name, token=api_key)
        
        prompt = "Hello, world! Please introduce yourself and tell me what you can do."
        
        print(f"Prompt: {prompt}")
        print("Generating response...")
        
        result = generator(prompt, max_length=100, num_return_sequences=1)
        
        print(f"Response: {result[0]['generated_text']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()