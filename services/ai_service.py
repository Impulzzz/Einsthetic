import os
from groq import Groq
from dotenv import load_dotenv
import json
import time

load_dotenv()

class AIService:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=groq_api_key)
        # Model selection based on difficulty
        self.hard_model = "llama-3.3-70b-versatile"  # Better reasoning for hard questions
        self.easy_medium_model = "llama-3.1-8b-instant"  # Faster for easy/medium
        
        self.system_instruction = """Role & Persona: You are Einsthetic, a specialized AI GATE Exam Tutor and strict Computer Science Professor. You are designed to assist with GATE (Graduate Aptitude Test in Engineering) preparation only. You behave as a high-stakes competitive exam tutor, emphasizing accuracy, technical precision, and analytical depth over conversational verbosity.

Exam Scope & Subject Constraints:
- Target: GATE Computer Science (India)
- Level: Undergraduate engineering + conceptual analytical reasoning
- Subjects: Generate and evaluate questions ONLY from these officially recognized fields:
  * Engineering Mathematics (Discrete Math, Linear Algebra, Calculus, Probability)
  * Digital Logic
  * Computer Organization and Architecture (COA)
  * Programming in C, Data Structures, and Algorithms
  * Theory of Computation (TOC) & Compiler Design
  * Operating Systems (OS)
  * Database Management Systems (DBMS)
  * Computer Networks
  * General Aptitude
- Scope Guardrail: If a request falls outside this syllabus, respond with: "This assistant is restricted to GATE exam preparation only."

Question Generation & Difficulty Scaling:
- Format: Generate strictly in GATE styles: MCQ (Multiple Choice), MSQ (Multiple Select), or NAT (Numerical Answer Type)
- Difficulty Calibration:
  * Easy: Conceptual 1-mark style; focuses on fundamental properties and direct application
  * Medium: Standard 2-mark style; requires linking two concepts or moderate multi-step calculations
  * Hard: Top-ranker challenge; complex, multi-layered analytical problems requiring deep reasoning
- Avoid: Trivial definitions, rote memorization, or overly theoretical research problems

Evaluation & Feedback Rules:
- Logic First: Prioritize conceptual correctness over exact wording
- Feedback: Provide concise, exam-oriented feedback with step-by-step logic breakdown
- No Spoilers: Do not reveal full solutions during the question phase unless explicitly asked

Operational Constraints:
- Technical Language: Use precise technical terminology (e.g., "Paging," "NP-Complete," "B+ Trees")
- No Hallucinations: Double-verify mathematical steps and formulas before outputting
- Cognitive Focus: Optimize strictly for exam relevance, not creativity

Critical JSON Output Requirements:
1. Response Format: Return ONLY valid JSON, no extra text
2. Double-escape all LaTeX backslashes (e.g., use \\\\frac instead of \\frac) to ensure valid JSON
3. For MCQs: Provide exactly 4 options (A, B, C, D) with one correct answer
4. For MSQs: Provide 4-5 options with multiple correct answers (return as array)
5. For NAT: Provide the correct numerical value or range

JSON Structure:
{
    "question": "The question text, using LaTeX for math formulas (wrapped in $...$)",
    "type": "MCQ" or "MSQ" or "NAT",
    "options": {"A": "...", "B": "...", "C": "...", "D": "..."} (null for NAT),
    "correct_answer": "Option Key (e.g., 'A') or Array for MSQ (e.g., ['A', 'C']) or Numerical Value for NAT",
    "explanation": "Detailed step-by-step solution using LaTeX and precise technical terminology"
}"""

    def generate_question(self, subject, difficulty="Medium", topic=None):
        difficulty_desc = {
            "Easy": "Basic concepts, direct application of formulas (1-mark style).",
            "Medium": "Linking two concepts, moderate calculations (2-mark style).",
            "Hard": "Complex, multi-layered problems that require deep reasoning (Top-ranker style)."
        }
        
        # Select model based on difficulty
        model = self.hard_model if difficulty == "Hard" else self.easy_medium_model
        
        user_message = f"""Generate a {difficulty} level GATE question for the subject: {subject}.
Difficulty Criteria: {difficulty_desc.get(difficulty, difficulty_desc["Medium"])}"""
        
        if topic:
            user_message += f"\nSpecific topic: {topic}."
        
        user_message += "\n\nRespond ONLY with valid JSON. No extra text."
        
        # Try with retry logic (2 attempts)
        for attempt in range(2):
            try:
                print(f"Attempting question generation with Groq ({model}, attempt {attempt + 1})...")
                
                messages = [
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": user_message}
                ]
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.7
                )
                
                # Extract response text
                response_text = response.choices[0].message.content.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith("```"):
                    lines = response_text.split("\n")
                    # Remove first line (```json) and last line (```)
                    response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
                    response_text = response_text.replace("```json", "").replace("```", "").strip()
                
                # Parse JSON
                question_data = json.loads(response_text)
                print(f"[OK] Successfully generated question with Groq ({model})")
                return question_data
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error with Groq: {e}")
                with open("error.log", "a") as f:
                    f.write(f"JSON Error (Groq {model}): {e}\nResponse: {response_text if 'response_text' in locals() else 'None'}\n")
                # Don't retry on JSON errors, might be consistent
                break
                
            except Exception as e:
                error_str = str(e)
                print(f"Error with Groq: {error_str}")
                
                # Check for rate limit
                if ("429" in error_str or "rate" in error_str.lower()) and attempt == 0:
                    print(f"Rate limit hit. Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                
                # Log error
                with open("error.log", "a") as f:
                    f.write(f"Error (Groq {model}): {e}\n")
                break
        
        # All attempts failed - return mock
        print("Groq API failed. Returning MOCK data.")
        return {
            "question": f"MOCK QUESTION: API Unavailable. What is the Time Complexity of {topic or 'Merge Sort'}?",
            "type": "MCQ",
            "options": {
                "A": "O(N log N)",
                "B": "O(N^2)",
                "C": "O(N)",
                "D": "O(1)"
            },
            "correct_answer": "A",
            "explanation": "This is a mock explanation because the AI service was unavailable."
        }

    def evaluate_answer(self, question, user_answer):
        # Placeholder for future AI-powered answer evaluation
        # For now, answers are evaluated client-side against correct_answer
        pass
