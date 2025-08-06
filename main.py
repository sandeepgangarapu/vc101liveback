"""
TSA Item Checker Backend API
A FastAPI backend service that determines if items can be carried in check-in or carry-on luggage
through TSA security using OpenRouter LLM calls.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx
import json
from typing import Optional

# Load environment variables
load_dotenv()

app = FastAPI(
    title="TSA Item Checker API",
    description="Check if items can be carried in check-in or carry-on luggage through TSA security",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ItemCheckRequest(BaseModel):
    item: str
    description: Optional[str] = None

class TSACheckResult(BaseModel):
    item: str
    carry_on_allowed: bool
    checked_baggage_allowed: bool
    description: str
    restrictions: Optional[str] = None
    additional_notes: Optional[str] = None

class OpenRouterService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
    
    async def check_tsa_item(self, item: str, item_description: Optional[str] = None) -> TSACheckResult:
        """
        Use OpenRouter LLM to determine TSA compliance for an item
        """
        
        # Construct the prompt
        prompt = f"""
You are an expert TSA (Transportation Security Administration) assistant. Analyze the following item and determine if it can be carried in carry-on luggage, checked baggage, or both.

Item: {item}
{f"Additional description: {item_description}" if item_description else ""}

Please provide a detailed analysis in the following JSON format:
{{
    "carry_on_allowed": true/false,
    "checked_baggage_allowed": true/false,
    "description": "Clear explanation of TSA rules for this item",
    "restrictions": "Any size, quantity, or packaging restrictions (if applicable)",
    "additional_notes": "Any important safety or regulatory notes"
}}

Base your response on current TSA regulations. Be specific about any size limits, liquid restrictions, or special requirements. If the item is prohibited in both carry-on and checked baggage, explain why.
"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3.5-sonnet",  # Using Claude for better reasoning
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.1,  # Low temperature for consistent, factual responses
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"OpenRouter API error: {response.status_code} - {response.text}"
                    )
                
                result = response.json()
                llm_response = result["choices"][0]["message"]["content"]
                
                # Try to parse the JSON response from the LLM
                try:
                    # Extract JSON from the response (in case it's wrapped in markdown)
                    json_start = llm_response.find('{')
                    json_end = llm_response.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = llm_response[json_start:json_end]
                        parsed_result = json.loads(json_str)
                    else:
                        # If no JSON found, create a structured response from the text
                        parsed_result = {
                            "carry_on_allowed": False,
                            "checked_baggage_allowed": False,
                            "description": llm_response,
                            "restrictions": None,
                            "additional_notes": "Unable to parse structured response from AI"
                        }
                        
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    parsed_result = {
                        "carry_on_allowed": False,
                        "checked_baggage_allowed": False,
                        "description": llm_response,
                        "restrictions": None,
                        "additional_notes": "Response format error - please verify information with official TSA guidelines"
                    }
                
                return TSACheckResult(
                    item=item,
                    carry_on_allowed=parsed_result.get("carry_on_allowed", False),
                    checked_baggage_allowed=parsed_result.get("checked_baggage_allowed", False),
                    description=parsed_result.get("description", "No description available"),
                    restrictions=parsed_result.get("restrictions"),
                    additional_notes=parsed_result.get("additional_notes")
                )
                
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request to LLM service timed out")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Initialize the OpenRouter service
openrouter_service = OpenRouterService()

@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {
        "message": "TSA Item Checker API is running!",
        "version": "1.0.0",
        "endpoints": {
            "check_item": "/check-item",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {"status": "healthy", "service": "tsa-item-checker"}

@app.post("/check-item", response_model=TSACheckResult)
async def check_item(request: ItemCheckRequest):
    """
    Check if an item can be carried in carry-on or checked baggage through TSA security
    
    Args:
        request: ItemCheckRequest containing the item name and optional description
        
    Returns:
        TSACheckResult with carry-on/checked baggage allowance and detailed information
    """
    
    if not request.item or not request.item.strip():
        raise HTTPException(status_code=400, detail="Item name is required")
    
    try:
        result = await openrouter_service.check_tsa_item(
            item=request.item.strip(),
            item_description=request.description
        )
        return result
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check item: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)