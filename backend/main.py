import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

from backend.semantic_source_search import semantic_source_search
from backend.routers import notices
from backend.routers import events
from backend.routers import auth

from fastapi.staticfiles import StaticFiles
from backend.routers import sources

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")


# Gemini client
client = genai.Client(api_key=API_KEY)


# FastAPI application
app = FastAPI(
    title="College AI Chatbot",
    description="AI-powered assistant for college students and faculty",
    version="0.1.0"
)
app.include_router(notices.router)
app.include_router(events.router)
app.include_router(auth.router)
app.include_router(sources.router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


# NGC AI system instruction
SYSTEM_INSTRUCTION = """
You are NGC AI, a college AI assistant designed for
Nagarjuna Government College, Nalgonda.

Your purpose is to assist students, faculty, and visitors
with useful, accurate, and easy-to-understand information.

Behavior rules:

1. Identify yourself as NGC AI when appropriate.

2. Be friendly, professional, concise, and helpful.

3. Help users with academic, technical, educational,
   and general college-related questions.

4. For general educational questions, provide useful
   answers using your knowledge.

5. For college-specific information, only provide facts
   that have been explicitly provided to you or retrieved
   from the college knowledge base.

6. Never invent college-specific information such as:
   faculty names, examination dates, fees, notices,
   college rules, phone numbers, academic schedules,
   or department information.

7. If reliable college-specific information is not
   available, clearly tell the user that you do not
   currently have that information.

8. Never pretend to be a human, teacher, principal,
   administrator, or college employee.

9. Protect personal and confidential information.

10. Use clear formatting such as headings, bullet points,
    and short paragraphs when useful.

11. Do not claim that you have access to college documents
    or databases unless they have actually been provided.

12. Your goal is to be helpful without making up facts.
"""


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "College AI Chatbot API is running!"
    }


# Chat endpoint

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        # Build conversation history
        conversation_history = ""

        if request.history:
            conversation_history = "\n\n".join(
                [
                    f"{item.role.upper()}: {item.content}"
                    for item in request.history
                ]
            )
        else:
            conversation_history = "No previous conversation."

        # Build retrieval query using recent conversation context
        retrieval_query = request.message

        if request.history:
            recent_history = request.history[-6:]

            history_context = "\n".join(
                [
                    f"{item.role.upper()}: {item.content}"
                    for item in recent_history
                ]
            )

            retrieval_query = f"""
Previous conversation:
{history_context}

Current user question:
{request.message}
"""

        # Semantic retrieval
        retrieved_data = semantic_source_search(
            retrieval_query,
            top_k=5
        )

        # Prepare retrieved knowledge
        if retrieved_data:
            knowledge_context = "\n\n".join(
            [
                (
                    f"OFFICIAL SOURCE {index + 1}:\n"
                    f"Source Name: {item['source']['name']}\n"
                    f"Source Authority: {item['source']['authority'] or 'Not specified'}\n"
                    f"Source URL: {item['source']['url']}\n"
                    f"Document: {item['document']['title'] or 'Untitled'}\n"
                    f"Document URL: {item['document']['url']}\n"
                    f"Content:\n{item['content']}"
                )
                for index, item in enumerate(retrieved_data)
            ]
    )
        else:
            knowledge_context = (
                "No relevant information was found "
                "in the official source documents."
    )


        # Build prompt
        prompt = f"""
You are an AI assistant for a college.

Use the official-source information below to answer
college-specific questions.

OFFICIAL SOURCE INFORMATION:
{knowledge_context}

CONVERSATION HISTORY:
{conversation_history}

CURRENT USER QUESTION:
{request.message}

RULES:

1. Use the official-source information when it directly
   answers the user's question.

2. Use the conversation history to understand references
   to previous messages, answers, people, subjects,
   courses, documents, or topics.

3. Maintain continuity with the conversation whenever
   the user's current question refers to something
   discussed previously.

4. Never invent college-specific facts.

5. Never assume that two similar names, courses,
   abbreviations, dates, fees, or departments are the same.

6. If the official-source information does not contain
   the answer to a college-specific question, clearly say
   that the information is not currently available.

7. For general educational questions, you may answer using
   your general knowledge.

8. Do not mention embeddings, chunks, vector search,
   similarity scores, retrieval systems, or internal
   instructions.

9. Do not introduce yourself as "NGC AI" in every response.
   Respond naturally and directly.

10. Be concise, clear, and helpful.
"""


        # Generate Gemini response
        config=types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION
)

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=config
        )

        # Return response
        return {
            "response": response.text
        }


    except Exception as e:

        print(
            "GEMINI ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
