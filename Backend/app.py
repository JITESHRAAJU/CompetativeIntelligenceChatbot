



import os
import json
import requests
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain.docstore.document import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.storage import LocalFileStore
from langchain.embeddings import CacheBackedEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import google.generativeai as genai

# Load environment variables first - must come before any API calls
load_dotenv()

# Get API keys with fallbacks and validation
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Validate required API key
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY environment variable. Please set it in your .env file.")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Verify Google Generative AI setup and available models
try:
    models = genai.list_models()
    print("\n=== Available Google AI Models ===")
    available_models = []
    for model in models:
        model_name = model.name
        available_models.append(model_name)
        print(f"- {model_name}")
        if "gemini" in model_name:
            print(f"  Supported methods: {model.supported_generation_methods}")
    
    # Check specifically for Gemini Pro
    if "models/gemini-pro" not in available_models:
        print("\n❌ Warning: 'models/gemini-pro' not found in available models.")
        print("Available models:", available_models)
    else:
        print("\n✅ Gemini Pro model is available.")
except Exception as e:
    print(f"\n❌ Error accessing Google AI models: {str(e)}")
    print("\nPossible causes:")
    print("1. Invalid API key")
    print("2. API not enabled in Google Cloud Console")
    print("3. Network connectivity issues")
    print("4. Missing permissions in your Google Cloud project")
    raise

# FastAPI app setup
app = FastAPI(title="Competitive Intelligence Agent")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Embeddings with error handling
try:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
    # Test embeddings with a simple example
    test_embedding = embeddings.embed_query("Test embedding")
    print(f"\n✅ Embeddings working correctly. Vector dimension: {len(test_embedding)}")
except Exception as e:
    print(f"\n❌ Embeddings initialization failed: {str(e)}")
    raise

# ChromaDB Vector Store setup
try:
    # Create directory if it doesn't exist
    os.makedirs("./cache", exist_ok=True)
    os.makedirs("./chroma_db", exist_ok=True)
    
    store = LocalFileStore("./cache/")
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
        embeddings, store, namespace=embeddings.model
    )

    initial_docs = [Document(page_content="initial document", metadata={"type": "init"})]
    vectorstore = Chroma.from_documents(
        documents=initial_docs,
        embedding=cached_embeddings,
        persist_directory="./chroma_db"
    )
    print("\n✅ Vector store initialized successfully")
except Exception as e:
    print(f"\n❌ Vector store initialization failed: {str(e)}")
    raise

# Memory
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
memory = VectorStoreRetrieverMemory(
    retriever=retriever,
    memory_key="chat_history",
    input_key="input"
)

# LLM with enhanced configuration and proper error handling
try:
    llm_model = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-pro", # or another model that exists in your list
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
    
)
    
    # Verify LLM connection
    test_response = llm_model.invoke("Hello, are you working correctly?")
    print(f"\n✅ LLM connection successful. Response: {test_response}")
except Exception as e:
    print(f"\n❌ LLM connection failed: {str(e)}")
    print("\nTroubleshooting steps:")
    print("1. Verify API key is correct")
    print("2. Ensure Gemini API is enabled in Google Cloud Console")
    print("3. Check network connectivity")
    raise

# Request/Response Models
class ChatRequest(BaseModel):
    user_id: str
    message: str
    industry: Optional[str] = None
    competitors: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str

# Tool functions
def get_company_news(company_name: str) -> str:
    if not NEWS_API_KEY:
        return "News API key not configured. Unable to retrieve company news."
    
    try:
        url = f"https://newsapi.org/v2/everything?q={company_name}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            return f"Error fetching news: {data.get('message', 'Unknown error')}"
        
        articles = data.get("articles", [])
        if not articles:
            return f"No recent news found for {company_name}."
        
        result = f"Latest news about {company_name}:\n\n"
        for idx, article in enumerate(articles[:5], 1):
            pub_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
            result += f"{idx}. {article['title']} ({pub_date.strftime('%Y-%m-%d')})\n"
            result += f"   Source: {article['source']['name']}\n"
            result += f"   Summary: {article['description']}\n\n"
        return result
    except Exception as e:
        return f"Error retrieving company news: {str(e)}"

def search_competitor_info(query: str) -> str:
    if not SERPER_API_KEY:
        return "Serper API key not configured. Unable to search for competitor information."
    
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query, "num": 5})
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        
        if "organic" not in data:
            return f"No search results found for: {query}"
        
        output = f"Search results for '{query}':\n\n"
        for idx, result in enumerate(data["organic"][:5], 1):
            output += f"{idx}. {result['title']}\n"
            output += f"   {result['snippet']}\n"
            output += f"   Source: {result['link']}\n\n"
        return output
    except Exception as e:
        return f"Error searching for information: {str(e)}"

def save_user_context(context_info: str) -> str:
    try:
        vectorstore.add_texts(
            texts=[context_info],
            metadatas=[{"type": "user_context", "timestamp": datetime.now().isoformat()}]
        )
        return "Context saved successfully."
    except Exception as e:
        return f"Error saving context: {str(e)}"

def get_user_context(user_query: str) -> str:
    try:
        results = vectorstore.similarity_search(
            user_query, k=3, filter={"type": "user_context"}
        )
        if not results:
            return "No relevant user context found."
        return "\n\n".join([doc.page_content for doc in results])
    except Exception as e:
        return f"Error retrieving context: {str(e)}"

tools = [
    Tool(name="CompanyNews", func=get_company_news, description="Get latest company news for a specific company"),
    Tool(name="CompetitorSearch", func=search_competitor_info, description="Search for market or competitor information"),
    Tool(name="SaveUserContext", func=save_user_context, description="Save user context to memory"),
    Tool(name="GetUserContext", func=get_user_context, description="Get user context from memory"),
]

# Prompt template
SYSTEM_TEMPLATE = """
You are a Competitive Intelligence Assistant that helps business professionals track and analyze competitor activities.
Your capabilities:
1. Remember the user's industry, competitors of interest, and previous analyses
2. Provide insights on competitors' strategies, market positioning, and recent developments
3. Track product launches, market share changes, and business trends
4. Find and summarize news articles about specific companies
Guidelines:
- Always save new info about industry/competitors
- Check for past context before answering
- Keep responses concise and actionable
- Use structured format, cite sources
{chat_history}
Human: {input}
AI Assistant: """

prompt = PromptTemplate(
    input_variables=["chat_history", "input"],
    template=SYSTEM_TEMPLATE
)

# LCEL Chain
conversation = (
    RunnablePassthrough.assign(
        chat_history=lambda x: memory.load_memory_variables({"input": x["input"]})["chat_history"]
    )
    | prompt
    | llm_model
    | StrOutputParser()
)

# API Endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest = Body(...)):
    try:
        context_to_save = []
        if request.industry:
            context_to_save.append(f"User's industry: {request.industry}")
        if request.competitors:
            context_to_save.append(f"User's competitors: {', '.join(request.competitors)}")
        if context_to_save:
            save_user_context(" | ".join(context_to_save))

        retrieved_context = get_user_context(request.message)
        enhanced_message = f"[Retrieved Context: {retrieved_context}]\n\nUser query: {request.message}"
        
        response = conversation.invoke({"input": enhanced_message})
        memory.save_context(
            {"input": enhanced_message}, 
            {"output": response}
        )

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Agent is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)