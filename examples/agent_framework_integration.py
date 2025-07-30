"""
Agent Framework Integration Example

This example demonstrates how to integrate strategic debate capabilities
into multi-agent systems and frameworks like LangGraph, CrewAI, or custom agent systems.
"""

import sys
import os
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategic_debate import DebateAgent, QuickConfig, DebateSession


# Abstract base classes for agent framework integration
class Agent(ABC):
    """Base agent class for integration with agent frameworks"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output"""
        pass


class AgentFramework:
    """Simple agent framework for demonstration"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.workflow_history: List[Dict[str, Any]] = []
    
    def add_agent(self, agent: Agent):
        """Add an agent to the framework"""
        self.agents[agent.name] = agent
    
    async def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a workflow with multiple agents"""
        results = []
        context = {}
        
        for step in workflow_steps:
            agent_name = step["agent"]
            input_data = step.get("input", {})
            input_data.update(context)  # Add context from previous steps
            
            if agent_name in self.agents:
                result = await self.agents[agent_name].process(input_data)
                results.append(result)
                context.update(result)  # Update context for next steps
        
        return results


# Strategic Debate Agent implementations
class DebateResearchAgent(Agent):
    """Agent that researches topics before debating"""
    
    def __init__(self):
        super().__init__("debate_researcher", "research and analysis")
        self.debate_agent = DebateAgent(QuickConfig.for_research_analysis())
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic")
        stance = input_data.get("stance", "PRO")
        
        # Generate research-based argument
        argument = await self.debate_agent.generate_argument_async(
            topic=topic,
            stance=stance
        )
        
        return {
            "research_argument": argument,
            "topic": topic,
            "stance": stance,
            "agent": self.name
        }


class DebateCounterAgent(Agent):
    """Agent that generates counter-arguments"""
    
    def __init__(self):
        super().__init__("debate_counter", "counter-argumentation")
        self.debate_agent = DebateAgent(QuickConfig.for_educational_use())
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic")
        original_stance = input_data.get("stance", "PRO")
        conversation = input_data.get("conversation", [])
        
        # Generate counter-stance
        counter_stance = "ANTI" if original_stance == "PRO" else "PRO"
        
        counter_argument = await self.debate_agent.generate_argument_async(
            topic=topic,
            stance=counter_stance,
            conversation=conversation
        )
        
        return {
            "counter_argument": counter_argument,
            "counter_stance": counter_stance,
            "topic": topic,
            "agent": self.name
        }


class DebateRefinementAgent(Agent):
    """Agent that refines and improves arguments"""
    
    def __init__(self):
        super().__init__("debate_refiner", "argument refinement")
        self.debate_agent = DebateAgent(QuickConfig.for_content_generation())
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic")
        stance = input_data.get("stance")
        original_argument = input_data.get("research_argument", "")
        counter_argument = input_data.get("counter_argument", "")
        
        # Build conversation context for refinement
        conversation = []
        if original_argument:
            conversation.append(original_argument)
        if counter_argument:
            conversation.append(counter_argument)
        
        refined_argument = await self.debate_agent.generate_argument_async(
            topic=topic,
            stance=stance,
            conversation=conversation
        )
        
        return {
            "refined_argument": refined_argument,
            "original_argument": original_argument,
            "counter_argument": counter_argument,
            "topic": topic,
            "agent": self.name
        }


class DebateAnalysisAgent(Agent):
    """Agent that analyzes debate quality and effectiveness"""
    
    def __init__(self):
        super().__init__("debate_analyzer", "debate analysis")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = input_data.get("topic")
        refined_argument = input_data.get("refined_argument", "")
        counter_argument = input_data.get("counter_argument", "")
        
        # Simple analysis (in a real implementation, this could use 
        # another LLM or specialized evaluation metrics)
        analysis = {
            "topic": topic,
            "argument_length": len(refined_argument.split()),
            "counter_argument_length": len(counter_argument.split()),
            "has_logical_structure": "because" in refined_argument.lower(),
            "addresses_counterpoints": any(word in refined_argument.lower() 
                                         for word in ["however", "although", "while"]),
            "agent": self.name
        }
        
        return analysis


# Multi-agent debate system
class MultiAgentDebateSystem:
    """Complete multi-agent system for strategic debate"""
    
    def __init__(self):
        self.framework = AgentFramework()
        self._setup_agents()
    
    def _setup_agents(self):
        """Initialize and add all agents to the framework"""
        self.framework.add_agent(DebateResearchAgent())
        self.framework.add_agent(DebateCounterAgent())
        self.framework.add_agent(DebateRefinementAgent())
        self.framework.add_agent(DebateAnalysisAgent())
    
    async def generate_comprehensive_argument(self, topic: str, stance: str = "PRO") -> Dict[str, Any]:
        """Generate a comprehensive argument using multiple agents"""
        
        workflow = [
            {
                "agent": "debate_researcher",
                "input": {"topic": topic, "stance": stance}
            },
            {
                "agent": "debate_counter", 
                "input": {"topic": topic, "stance": stance}
            },
            {
                "agent": "debate_refiner",
                "input": {"topic": topic, "stance": stance}
            },
            {
                "agent": "debate_analyzer",
                "input": {"topic": topic}
            }
        ]
        
        results = await self.framework.execute_workflow(workflow)
        
        # Combine results into comprehensive output
        return {
            "topic": topic,
            "stance": stance,
            "research_argument": results[0].get("research_argument"),
            "counter_argument": results[1].get("counter_argument"),
            "refined_argument": results[2].get("refined_argument"),
            "analysis": results[3],
            "workflow_results": results
        }


# Integration with popular agent frameworks (pseudo-code examples)
class LangGraphIntegration:
    """Example integration with LangGraph"""
    
    def __init__(self):
        self.debate_agent = DebateAgent(QuickConfig.for_content_generation())
    
    def create_debate_node(self):
        """Create a LangGraph node for debate functionality"""
        # This would be actual LangGraph code in a real implementation
        def debate_node(state):
            topic = state["topic"]
            stance = state["stance"] 
            conversation = state.get("conversation", [])
            
            argument = self.debate_agent.generate_argument(
                topic=topic,
                stance=stance,
                conversation=conversation
            )
            
            return {"argument": argument, "updated_conversation": conversation + [argument]}
        
        return debate_node


class CrewAIIntegration:
    """Example integration with CrewAI"""
    
    def __init__(self):
        self.debate_agent = DebateAgent(QuickConfig.for_educational_use())
    
    def create_debate_crew_member(self):
        """Create a CrewAI crew member with debate capabilities"""
        # This would be actual CrewAI code in a real implementation
        crew_member_config = {
            "role": "Strategic Debater",
            "goal": "Generate persuasive arguments for given topics",
            "backstory": "An expert in rhetoric and persuasive argumentation",
            "tools": [self._debate_tool],
            "verbose": True
        }
        return crew_member_config
    
    def _debate_tool(self, topic: str, stance: str) -> str:
        """Tool function for CrewAI integration"""
        return self.debate_agent.generate_argument(topic, stance)


# Example usage and demonstrations
async def demonstrate_multi_agent_system():
    """Demonstrate the multi-agent debate system"""
    print("=== Multi-Agent Strategic Debate System ===\n")
    
    system = MultiAgentDebateSystem()
    
    topic = "Space exploration should be prioritized over solving Earth's problems"
    print(f"Topic: {topic}\n")
    
    # Generate comprehensive argument
    result = await system.generate_comprehensive_argument(topic, "PRO")
    
    print("Research Argument:")
    print(result["research_argument"])
    print("\nCounter Argument:")
    print(result["counter_argument"])
    print("\nRefined Argument:")
    print(result["refined_argument"])
    print("\nAnalysis:")
    for key, value in result["analysis"].items():
        if key != "agent":
            print(f"  {key}: {value}")


def demonstrate_framework_integrations():
    """Demonstrate framework integration patterns"""
    print("\n=== Framework Integration Examples ===\n")
    
    print("1. LangGraph Integration Pattern:")
    langgraph_integration = LangGraphIntegration()
    debate_node = langgraph_integration.create_debate_node()
    print("   ✓ Debate node created for LangGraph workflow")
    
    print("\n2. CrewAI Integration Pattern:")
    crewai_integration = CrewAIIntegration()
    crew_member = crewai_integration.create_debate_crew_member()
    print("   ✓ Debate crew member configured for CrewAI")
    print(f"   Role: {crew_member['role']}")
    print(f"   Goal: {crew_member['goal']}")


async def demonstrate_debate_session():
    """Demonstrate multi-turn debate session"""
    print("\n=== Multi-Turn Debate Session ===\n")
    
    # Create agents with different configurations
    pro_agent = DebateAgent(QuickConfig.for_research_analysis())
    con_agent = DebateAgent(QuickConfig.for_educational_use())
    
    # Create debate session
    topic = "Artificial Intelligence development should be paused until safety measures are established"
    session = DebateSession(topic, pro_agent, con_agent)
    
    print(f"Topic: {topic}\n")
    
    # Run 4 turns of debate
    for turn in range(4):
        result = session.next_turn()
        print(f"Turn {result['turn']} ({result['stance']}):")
        print(f"{result['argument']}\n")


if __name__ == "__main__":
    async def main():
        try:
            await demonstrate_multi_agent_system()
            demonstrate_framework_integrations()
            await demonstrate_debate_session()
        except FileNotFoundError:
            print("Error: Please create an 'openai_key.txt' file with your OpenAI API key to run this example.")
        except Exception as e:
            print(f"Error running example: {e}")
            print("Make sure you have set up the environment properly and have a valid OpenAI API key.")
    
    asyncio.run(main())