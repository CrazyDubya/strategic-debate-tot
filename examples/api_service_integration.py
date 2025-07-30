"""
API Service Integration Example

This example shows how to deploy the strategic debate library as a 
microservice using FastAPI for integration into larger systems.
"""

import sys
import os
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    print("FastAPI not available. This is a demonstration of the integration pattern.")
    print("To run this example, install FastAPI: pip install fastapi uvicorn")
    FastAPI = None

from strategic_debate import (
    DebateAgent, QuickConfig, StrategicDebatePipeline, 
    DebateConfig, ReasoningType, SearchStrategy, EvaluationStrategy
)


# Pydantic models for API requests/responses
class ArgumentRequest(BaseModel):
    """Request model for generating arguments"""
    topic: str = Field(..., description="The debate topic")
    stance: str = Field(..., description="The stance to take (PRO or ANTI)")
    conversation: Optional[List[str]] = Field(default=None, description="Optional conversation history")
    reasoning_type: Optional[str] = Field(default="iterative_drafting", description="Reasoning type")
    search_strategy: Optional[str] = Field(default="beam_search", description="Search strategy")
    depth: Optional[int] = Field(default=2, description="Reasoning depth")
    response_length: Optional[str] = Field(default="a few sentences", description="Response length")
    use_case: Optional[str] = Field(default="educational", description="Predefined use case configuration")


class ArgumentResponse(BaseModel):
    """Response model for generated arguments"""
    argument: str
    topic: str
    stance: str
    config_used: Dict[str, Any]
    generation_time: float
    timestamp: str


class BatchArgumentRequest(BaseModel):
    """Request model for batch argument generation"""
    topics: List[str]
    stance_pairs: List[List[str]]  # List of [pro_stance, con_stance] pairs
    conversations: Optional[List[List[str]]] = None
    use_case: Optional[str] = Field(default="educational")


class BatchArgumentResponse(BaseModel):
    """Response model for batch generated arguments"""
    results: List[Dict[str, str]]
    total_topics: int
    generation_time: float
    timestamp: str


class DebateSessionRequest(BaseModel):
    """Request model for starting a debate session"""
    topic: str
    turns: Optional[int] = Field(default=4, description="Number of turns in the debate")
    pro_config: Optional[str] = Field(default="research", description="Configuration for PRO agent")
    con_config: Optional[str] = Field(default="educational", description="Configuration for CON agent")


class DebateSessionResponse(BaseModel):
    """Response model for debate session"""
    topic: str
    turns: List[Dict[str, str]]
    total_turns: int
    generation_time: float
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    capabilities: List[str]
    timestamp: str


# Strategic Debate API Service
class StrategicDebateAPI:
    """API service for strategic debate functionality"""
    
    def __init__(self):
        self.agents = {}
        self.pipeline = None
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agents with different configurations"""
        self.agents = {
            "educational": DebateAgent(QuickConfig.for_educational_use()),
            "content": DebateAgent(QuickConfig.for_content_generation()),
            "research": DebateAgent(QuickConfig.for_research_analysis()),
            "fast": DebateAgent(QuickConfig.for_fast_response())
        }
        self.pipeline = StrategicDebatePipeline(QuickConfig.for_educational_use())
    
    def _get_agent(self, use_case: str) -> DebateAgent:
        """Get agent for specific use case"""
        return self.agents.get(use_case, self.agents["educational"])
    
    def _create_custom_agent(self, request: ArgumentRequest) -> DebateAgent:
        """Create a custom agent based on request parameters"""
        config = DebateConfig(
            reasoning_type=ReasoningType(request.reasoning_type),
            search_strategy=SearchStrategy(request.search_strategy),
            depth=request.depth,
            response_length=request.response_length
        )
        return DebateAgent(config)


if FastAPI:
    # Create FastAPI application
    app = FastAPI(
        title="Strategic Debate API",
        description="API for generating strategic arguments using Tree of Thoughts",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize the API service
    debate_api = StrategicDebateAPI()
    
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            capabilities=[
                "argument_generation",
                "batch_processing", 
                "debate_sessions",
                "multiple_reasoning_types"
            ],
            timestamp=datetime.now().isoformat()
        )
    
    
    @app.post("/generate-argument", response_model=ArgumentResponse)
    async def generate_argument(request: ArgumentRequest):
        """Generate a strategic argument"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate stance
            if request.stance not in ["PRO", "ANTI"]:
                raise HTTPException(status_code=400, detail="Stance must be 'PRO' or 'ANTI'")
            
            # Get or create agent
            if request.use_case in debate_api.agents:
                agent = debate_api._get_agent(request.use_case)
                config_used = {"use_case": request.use_case}
            else:
                agent = debate_api._create_custom_agent(request)
                config_used = {
                    "reasoning_type": request.reasoning_type,
                    "search_strategy": request.search_strategy,
                    "depth": request.depth,
                    "response_length": request.response_length
                }
            
            # Generate argument
            argument = await agent.generate_argument_async(
                topic=request.topic,
                stance=request.stance,
                conversation=request.conversation or []
            )
            
            generation_time = asyncio.get_event_loop().time() - start_time
            
            return ArgumentResponse(
                argument=argument,
                topic=request.topic,
                stance=request.stance,
                config_used=config_used,
                generation_time=generation_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.post("/batch-generate", response_model=BatchArgumentResponse)
    async def batch_generate_arguments(request: BatchArgumentRequest):
        """Generate arguments for multiple topics in batch"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate input
            if len(request.topics) != len(request.stance_pairs):
                raise HTTPException(
                    status_code=400, 
                    detail="Number of topics must match number of stance pairs"
                )
            
            # Use pipeline for batch processing
            pipeline = StrategicDebatePipeline(
                config=getattr(QuickConfig, f"for_{request.use_case}_use")()
                if hasattr(QuickConfig, f"for_{request.use_case}_use") 
                else QuickConfig.for_educational_use()
            )
            
            # Convert stance pairs to tuples
            stance_tuples = [tuple(pair) for pair in request.stance_pairs]
            
            # Process batch
            results = await pipeline.batch_process_async(
                topics=request.topics,
                stance_pairs=stance_tuples,
                conversations=request.conversations
            )
            
            generation_time = asyncio.get_event_loop().time() - start_time
            
            return BatchArgumentResponse(
                results=results,
                total_topics=len(request.topics),
                generation_time=generation_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.post("/debate-session", response_model=DebateSessionResponse)
    async def create_debate_session(request: DebateSessionRequest):
        """Create a multi-turn debate session"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create agents with specified configurations
            pro_agent = debate_api._get_agent(request.pro_config)
            con_agent = debate_api._get_agent(request.con_config)
            
            # Simulate debate session
            conversation = []
            turns = []
            
            for turn in range(request.turns):
                stance = "PRO" if turn % 2 == 0 else "ANTI"
                agent = pro_agent if stance == "PRO" else con_agent
                
                argument = await agent.generate_argument_async(
                    topic=request.topic,
                    stance=stance,
                    conversation=conversation
                )
                
                conversation.append(argument)
                turns.append({
                    "turn": turn + 1,
                    "stance": stance,
                    "argument": argument
                })
            
            generation_time = asyncio.get_event_loop().time() - start_time
            
            return DebateSessionResponse(
                topic=request.topic,
                turns=turns,
                total_turns=len(turns),
                generation_time=generation_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @app.get("/configurations")
    async def get_available_configurations():
        """Get available predefined configurations"""
        return {
            "configurations": [
                {
                    "name": "educational",
                    "description": "Optimized for educational platforms",
                    "features": ["logical tone", "moderate depth", "clear explanations"]
                },
                {
                    "name": "content",
                    "description": "Optimized for content generation",
                    "features": ["creative approach", "persuasive language", "longer responses"]
                },
                {
                    "name": "research",
                    "description": "Optimized for research and analysis",
                    "features": ["thorough analysis", "evidence-based", "comprehensive reasoning"]
                },
                {
                    "name": "fast",
                    "description": "Optimized for quick responses",
                    "features": ["minimal processing", "fast generation", "concise arguments"]
                }
            ]
        }


# Client usage examples
class StrategicDebateClient:
    """Client for interacting with the Strategic Debate API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def generate_argument(self, topic: str, stance: str, **kwargs) -> Dict[str, Any]:
        """Generate argument via API"""
        # In a real implementation, this would use httpx or requests
        # This is a demonstration of the client interface
        request_data = {
            "topic": topic,
            "stance": stance,
            **kwargs
        }
        
        # Simulated API call
        print(f"API Call: POST {self.base_url}/generate-argument")
        print(f"Request: {request_data}")
        
        return {
            "argument": f"Generated argument for '{topic}' with stance '{stance}'",
            "topic": topic,
            "stance": stance
        }
    
    async def batch_generate(self, topics: List[str], stance_pairs: List[List[str]]) -> Dict[str, Any]:
        """Batch generate arguments via API"""
        request_data = {
            "topics": topics,
            "stance_pairs": stance_pairs
        }
        
        print(f"API Call: POST {self.base_url}/batch-generate")
        print(f"Request: {request_data}")
        
        return {
            "results": [
                {"topic": topic, "pro_argument": "...", "con_argument": "..."}
                for topic in topics
            ]
        }


# Example usage and integration patterns
def demonstrate_api_integration():
    """Demonstrate API integration patterns"""
    print("=== Strategic Debate API Integration ===\n")
    
    if not FastAPI:
        print("FastAPI not installed. This demonstrates the integration pattern.")
        print("Install FastAPI to run the actual API: pip install fastapi uvicorn")
        print()
    
    # Show client usage
    print("1. Client Usage Example:")
    async def client_example():
        client = StrategicDebateClient()
        
        # Single argument generation
        result = await client.generate_argument(
            topic="Remote work increases productivity",
            stance="PRO",
            use_case="content"
        )
        print(f"   Generated: {result['argument']}")
        
        # Batch processing
        topics = ["AI ethics", "Climate policy", "Space exploration"]
        stance_pairs = [["PRO", "ANTI"], ["PRO", "ANTI"], ["PRO", "ANTI"]]
        
        batch_result = await client.batch_generate(topics, stance_pairs)
        print(f"   Batch processed {len(batch_result['results'])} topics")
    
    asyncio.run(client_example())
    
    print("\n2. Integration Scenarios:")
    scenarios = [
        "E-learning platforms requesting debate exercises",
        "Content management systems generating marketing copy",
        "Research tools analyzing multiple perspectives",
        "Chatbot systems with argumentation capabilities"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"   {i}. {scenario}")
    
    print("\n3. API Endpoints:")
    endpoints = [
        "POST /generate-argument - Generate single argument",
        "POST /batch-generate - Process multiple topics",
        "POST /debate-session - Multi-turn debate simulation",
        "GET /health - Service health check",
        "GET /configurations - Available configurations"
    ]
    
    for endpoint in endpoints:
        print(f"   {endpoint}")


if __name__ == "__main__":
    if FastAPI:
        print("Starting Strategic Debate API server...")
        print("API will be available at: http://localhost:8000")
        print("Interactive docs at: http://localhost:8000/docs")
        print("\nTo start the server, run:")
        print("uvicorn api_service_integration:app --reload")
    else:
        demonstrate_api_integration()