# Strategic Debate ToT Integration Guide

This guide shows how to integrate the Strategic Debate Tree of Thoughts library into other agentic workflows and AI systems.

## Overview

The Strategic Debate library provides a powerful Tree of Thoughts framework for generating persuasive arguments through structured reasoning. It can be integrated into various agentic workflows to enhance debate capabilities, argument generation, and persuasive communication.

## Core Integration Patterns

### 1. Agent Workflow Integration

Integrate strategic debate capabilities into multi-agent systems:

```python
from strategic_debate import DebateAgent, create_conversation_state
from your_agent_framework import Agent, Workflow

class PersuasiveAgent(Agent):
    def __init__(self):
        super().__init__()
        self.debate_module = DebateAgent()
    
    def generate_argument(self, topic, stance, context=None):
        return self.debate_module.generate_response(
            topic=topic,
            stance=stance,
            conversation=context or []
        )

# In your workflow
workflow = Workflow()
persuasive_agent = PersuasiveAgent()
argument = persuasive_agent.generate_argument(
    topic="AI should be regulated",
    stance="PRO"
)
```

### 2. Pipeline Integration

Use as a component in data processing pipelines:

```python
from strategic_debate import StrategicDebatePipeline

pipeline = StrategicDebatePipeline()

# Process multiple debate topics
topics = ["Climate change policy", "Universal healthcare", "AI ethics"]
results = pipeline.batch_process(
    topics=topics,
    stance_pairs=[("PRO", "ANTI"), ("PRO", "ANTI"), ("PRO", "ANTI")]
)
```

### 3. API Service Integration

Deploy as a microservice for other applications:

```python
from fastapi import FastAPI
from strategic_debate import DebateAPI

app = FastAPI()
debate_api = DebateAPI()

@app.post("/generate-argument")
async def generate_argument(request: ArgumentRequest):
    return await debate_api.generate_argument(
        topic=request.topic,
        stance=request.stance,
        reasoning_type=request.reasoning_type,
        depth=request.depth
    )
```

## Integration Scenarios

### Educational Platforms
- Debate training systems
- Argument analysis tools
- Critical thinking applications

### Content Generation
- Marketing copy generation
- Editorial writing assistance
- Policy document drafting

### Research & Analysis
- Opinion mining systems
- Argument mapping tools
- Persuasion analysis platforms

### Conversational AI
- Chatbots with debate capabilities
- Virtual debate partners
- Argumentative dialogue systems

## Configuration Examples

### Quick Start Configuration
```python
from strategic_debate import QuickConfig

config = QuickConfig.for_educational_use()
# or
config = QuickConfig.for_content_generation()
# or  
config = QuickConfig.for_research_analysis()
```

### Custom Configuration
```python
from strategic_debate import StrategicDebateConfig

config = StrategicDebateConfig(
    reasoning_type="iterative_drafting",
    search_strategy="beam_search",
    depth=3,
    top_k=3,
    evaluation_strategy="score",
    model_name="gpt-4o",
    temperature=0.7
)
```

## Advanced Integration Features

### 1. Custom Evaluators
```python
from strategic_debate import CustomEvaluator

class DomainSpecificEvaluator(CustomEvaluator):
    def evaluate_argument(self, argument, context):
        # Your custom evaluation logic
        return score, reasoning

debate_system.set_evaluator(DomainSpecificEvaluator())
```

### 2. Workflow Orchestration
```python
from strategic_debate import DebateOrchestrator

orchestrator = DebateOrchestrator()
orchestrator.add_stage("research", research_agent)
orchestrator.add_stage("argue", debate_agent)
orchestrator.add_stage("refine", refinement_agent)

result = orchestrator.execute(topic="AI ethics")
```

### 3. Multi-Turn Debate Management
```python
from strategic_debate import DebateSession

session = DebateSession(
    topic="Universal Basic Income",
    participants=["pro_agent", "con_agent"]
)

# Manage turn-based argumentation
for turn in range(5):
    response = session.next_turn()
    # Process response, update context
```

## Best Practices

### Performance Optimization
- Use async/await for concurrent processing
- Implement caching for repeated arguments
- Batch process multiple topics when possible

### Error Handling
- Implement retry logic for LLM failures
- Validate argument quality before returning
- Provide fallback responses for edge cases

### Monitoring & Logging
- Track argument quality metrics
- Monitor response times and costs
- Log debate progressions for analysis

### Security Considerations
- Sanitize input topics and stances
- Implement rate limiting for API endpoints
- Validate and filter generated content

## Integration Examples

See the `examples/` directory for complete integration examples:
- `examples/agent_framework_integration.py` - Multi-agent system integration
- `examples/pipeline_integration.py` - Data processing pipeline integration  
- `examples/api_service_integration.py` - Microservice deployment
- `examples/educational_platform_integration.py` - Educational use case
- `examples/content_generation_integration.py` - Content creation workflow

## Support & Community

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share use cases
- Contributing: See CONTRIBUTING.md for guidelines

For additional integration support, please refer to the API documentation and example implementations.