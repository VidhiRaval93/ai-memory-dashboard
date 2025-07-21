import os
import json
import pathlib
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import datetime
import openai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('summarizer.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Chat Extractor", version="1.0.0")

# Add middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request and response
class SummarizeRequest(BaseModel):
    text: str = Field(..., description="Full answer body from Perplexity")
    source_links: Optional[List[str]] = Field(default=None, description="List of citation URLs")

class KeyFact(BaseModel):
    fact: str = Field(..., description="A key fact extracted from the text")
    source: Optional[str] = Field(default=None, description="Source URL if available")

class SummarizeResponse(BaseModel):
    topic: str = Field(..., description="Topic label for the content")
    summary: str = Field(..., description="Concise summary of the text")
    key_facts: List[KeyFact] = Field(..., description="3-5 key facts with sources")

class ChatLogRequest(BaseModel):
    question: str = Field(..., description="Question or user message")
    answer: str = Field(..., description="Answer or assistant message")
    timestamp: str = Field(..., description="ISO timestamp")
    source: str = Field(..., description="Source platform (chatgpt or perplexity)")
    tags: Optional[List[str]] = Field(default=[], description="Extracted tags")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Chat Extractor"}

@app.post("/logs")
def receive_logs():
    """Simple endpoint to silence noisy POST requests to /logs"""
    return {"status": "received"}

@app.get("/")
async def root():
    return {
        "message": "AI Chat Extractor API",
        "version": "1.0.0",
        "endpoints": {
            "POST /logs": "Receive chat data from ChatGPT and Perplexity",
            "POST /summarize": "Summarize text and extract key facts",
            "GET /health": "Health check",
            "GET /": "API information"
        }
    }

@app.post("/chat-logs")
async def receive_chat_logs(request: ChatLogRequest):
    """Receive chat logs from both ChatGPT and Perplexity extensions"""
    logger.info(f"=== RECEIVED CHAT LOG FROM {request.source.upper()} ===")
    logger.info(f"Question: {request.question[:100]}...")
    logger.info(f"Answer: {request.answer[:100]}...")
    logger.info(f"Timestamp: {request.timestamp}")
    logger.info(f"Tags: {request.tags}")
    
    try:
        # Create entry for spaces.json
        entry = {
            "id": f"{request.source}-{int(datetime.datetime.now().timestamp())}",
            "timestamp": request.timestamp,
            "source": request.source,
            "request": {
                "text": request.question,
                "source_links": []
            },
            "response": {
                "topic": request.question.split('\n')[0] if '\n' in request.question else request.question[:50],
                "summary": request.answer,
                "key_facts": []
            },
            "tags": request.tags
        }
        
        # Add to spaces.json
        spaces_path = pathlib.Path("spaces.json")
        existing_entries = []
        if spaces_path.exists():
            try:
                with spaces_path.open("r", encoding="utf-8") as f:
                    existing_entries = json.load(f)
            except Exception as e:
                logger.error(f"Error reading spaces.json: {e}")
                existing_entries = []
        
        # Add new entry to the beginning
        existing_entries.insert(0, entry)
        
        # Save back to file
        with spaces_path.open("w", encoding="utf-8") as f:
            json.dump(existing_entries, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully saved {request.source} entry with ID: {entry['id']}")
        
        return {
            "success": True,
            "message": f"Chat log from {request.source} saved successfully",
            "entry_id": entry["id"]
        }
        
    except Exception as e:
        logger.error(f"Error processing chat log: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat log: {str(e)}")

@app.get("/spaces")
async def get_spaces():
    spaces_path = pathlib.Path("spaces.json")
    if not spaces_path.exists():
        return JSONResponse(content=[], status_code=200)
    try:
        with spaces_path.open("r", encoding="utf-8") as f:
            data = f.read()
            return JSONResponse(content=json.loads(data), status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/dashboard-perplexity/data")
async def get_dashboard_data():
    """API endpoint for dashboard data"""
    spaces_path = pathlib.Path("spaces.json")
    if not spaces_path.exists():
        return JSONResponse(content={"raw_entries": []}, status_code=200)
    try:
        with spaces_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return JSONResponse(content={"raw_entries": data}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e), "raw_entries": []}, status_code=500)

@app.post("/spaces")
async def add_space(entry: dict):
    """Add a new research entry to spaces.json"""
    spaces_path = pathlib.Path("spaces.json")
    # Load existing entries
    existing_entries = []
    if spaces_path.exists():
        try:
            with spaces_path.open("r", encoding="utf-8") as f:
                existing_entries = json.load(f)
        except Exception as e:
            logger.error(f"Error reading spaces.json: {e}")
            existing_entries = []
    # Add timestamp if not present
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.datetime.now().isoformat()
    # Add the new entry
    existing_entries.append(entry)
    # Save back to file
    try:
        with spaces_path.open("w", encoding="utf-8") as f:
            json.dump(existing_entries, f, indent=2, ensure_ascii=False)
        logger.info(f"Added new research entry: {entry.get('topic', 'Unknown')}")
        return {"status": "success", "message": "Research entry saved"}
    except Exception as e:
        logger.error(f"Error writing to spaces.json: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save entry: {str(e)}")

# Serve the HTML dashboard at /dashboard
DASHBOARD_PATH = pathlib.Path(__file__).parent / "dashboard-perplexity"
if DASHBOARD_PATH.exists():
    app.mount("/dashboard", StaticFiles(directory=str(DASHBOARD_PATH), html=True), name="dashboard")

    @app.get("/dashboard/{full_path:path}")
    async def dashboard_catchall(full_path: str):
        # Always serve index.html for any subroute
        index_path = DASHBOARD_PATH / "index.html"
        return FileResponse(str(index_path))
    logger.info(f"AI Chat Dashboard available at http://localhost:8003/dashboard")
else:
    logger.warning(f"Dashboard directory not found at {DASHBOARD_PATH}")

# --- Summarization logic (OpenAI integration) ---
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-xxx")

def create_prompt(text: str, source_links: Optional[List[str]] = None) -> str:
    prompt = f"""
You are an expert content analyzer. Please analyze the following text and provide a structured response.

TEXT TO ANALYZE:
{text}
"""
    if source_links:
        prompt += f"""
AVAILABLE SOURCES:
{chr(10).join([f"{i+1}. {link}" for i, link in enumerate(source_links)])}
"""
    prompt += """
Please provide your analysis in the following JSON format:
{
    "topic": "A concise topic label (2-4 words)",
    "summary": "A concise summary of the main points (2-3 sentences)",
    "key_facts": [
        {
            "fact": "A key fact extracted from the text",
            "source": "Source URL if available, otherwise null"
        }
    ]
}
Requirements:
- Extract 3-5 key facts that are most important
- Each fact should be a complete, standalone statement
- If source links are provided, try to map facts to the most relevant source
- The topic should be specific and descriptive
- The summary should capture the main points without being too verbose
- Return only valid JSON, no additional text
JSON Response:
"""
    return prompt

def extract_source_for_fact(fact: str, source_links: List[str]) -> Optional[str]:
    if not source_links:
        return None
    fact_lower = fact.lower()
    for link in source_links:
        domain = link.lower()
        if any(keyword in fact_lower for keyword in domain.split('.') if '.' in domain):
            return link
    return source_links[0] if source_links else None

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    import asyncio
    logger.info("=== POST /summarize REQUEST RECEIVED ===")
    logger.info(f"Request text length: {len(request.text)} characters")
    logger.info(f"Request text preview: {request.text[:200]}...")
    logger.info(f"Source links: {request.source_links}")
    logger.info("=== END REQUEST LOG ===")
    try:
        prompt = create_prompt(request.text, request.source_links)
        client = openai.AsyncOpenAI()
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert content analyzer that provides structured JSON responses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        content = response.choices[0].message.content
        if content is None:
            raise HTTPException(status_code=500, detail="OpenAI returned empty response")
        content = content.strip()
        try:
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            parsed_response = json.loads(content)
            if not all(key in parsed_response for key in ["topic", "summary", "key_facts"]):
                raise ValueError("Invalid response structure")
            processed_facts = []
            for fact_data in parsed_response["key_facts"]:
                fact_text = fact_data.get("fact", "")
                source = fact_data.get("source")
                if not source and request.source_links:
                    source = extract_source_for_fact(fact_text, request.source_links)
                processed_facts.append(KeyFact(fact=fact_text, source=source))
            response = SummarizeResponse(
                topic=parsed_response["topic"],
                summary=parsed_response["summary"],
                key_facts=processed_facts
            )
            logger.info("=== SUCCESSFUL RESPONSE ===")
            logger.info(f"Topic: {response.topic}")
            logger.info(f"Summary: {response.summary}")
            logger.info(f"Number of key facts: {len(response.key_facts)}")
            logger.info("=== END RESPONSE LOG ===")
            return response
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse OpenAI response: {str(e)}")
        except ValueError as e:
            raise HTTPException(status_code=500, detail=f"Invalid response structure: {str(e)}")
    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 