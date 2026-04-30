import os
import json
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from supabase import create_client, Client

load_dotenv()

def generate_25_questions():
    print("--- GENERATING 25 ENTERPRISE TEST CASES ---")
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)
    
    # Fetch more chunks for diversity
    res = supabase.table("documents").select("content").limit(15).execute()
    context = "\n\n".join([r['content'] for r in res.data])
    
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
    
    prompt = f"""Based on the following legal text from the Bharatiya Nyaya Sanhita, 2023, generate exactly 25 professional, complex legal questions.
    Questions should cover:
    1. Definitions and Preliminary matters.
    2. Specific Section references.
    3. Procedural timelines.
    4. Jurisdictional nuances.
    
    Legal Text:
    {context}
    
    Return ONLY a JSON list of strings.
    """
    
    print("Requesting 25 questions from Groq...")
    response = llm.invoke(prompt)
    
    try:
        clean_content = response.content.strip().replace("```json", "").replace("```", "")
        questions = json.loads(clean_content)
        
        # Ensure exactly 25 or close to it
        questions = questions[:25]
        
        with open("data/batch_25_questions.json", "w") as f:
            json.dump(questions, f, indent=4)
            
        print(f"Successfully generated {len(questions)} test cases.")
        return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    generate_25_questions()
