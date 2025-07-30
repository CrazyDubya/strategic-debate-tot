"""
Strategic Debate Integration Module

This module provides simplified interfaces and utilities for integrating 
the Strategic Debate Tree of Thoughts framework into other agentic workflows.
"""

import asyncio
import typing
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Core imports
from iterative_drafting_tree_of_thoughts import IterativeDraftingTreeOfThoughts, IterativeDraftingMCTSTreeOfThoughts
from plan_and_execute_tree_of_thoughts import PlanAndExecuteTreeOfThoughts, PlanAndExecuteMCTSTreeOfThoughts
from abstractions.tree.tree import create_conversation_state
from abstractions.generator.generator import ResponseParameters
from utils.search_parameters import TreeOfThoughtsParameters, MonteCarloTreeOfThoughtParameters
from utils.utils import set_up_dspy
from utils import constants


class ReasoningType(Enum):
    """Available reasoning types for strategic debate"""
    ITERATIVE_DRAFTING = "iterative_drafting"
    PLAN_AND_EXECUTE = "plan_and_execute"


class SearchStrategy(Enum):
    """Available search strategies"""
    BEAM_SEARCH = "beam_search"
    MONTE_CARLO = "monte_carlo"


class EvaluationStrategy(Enum):
    """Available evaluation strategies"""
    SCORE = "score"
    VOTE = "vote"


@dataclass
class DebateConfig:
    """Configuration for strategic debate system"""
    reasoning_type: ReasoningType = ReasoningType.ITERATIVE_DRAFTING
    search_strategy: SearchStrategy = SearchStrategy.BEAM_SEARCH
    evaluation_strategy: EvaluationStrategy = EvaluationStrategy.SCORE
    depth: int = 2
    top_k: int = 2
    model_name: str = "gpt-4o-mini"
    max_tokens: int = 1000
    generation_temperature: float = 0.7
    judge_temperature: float = 0.7
    n_samples_generation: int = 3
    n_samples_judge: int = 5
    use_chain_of_thought: bool = True
    node_selection_strategy: str = "greedy"
    do_pruning: bool = True
    mcts_iterations: int = 10
    
    # Response parameters
    response_length: str = "a few sentences"
    communication_tone: str = "logical"
    language_style: str = "casual"


@dataclass
class ArgumentRequest:
    """Request structure for generating arguments"""
    topic: str
    stance: str  # "PRO" or "ANTI"
    conversation: Optional[List[str]] = None
    config: Optional[DebateConfig] = None


@dataclass 
class ArgumentResponse:
    """Response structure containing generated argument"""
    argument: str
    reasoning_steps: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class QuickConfig:
    """Predefined configurations for common use cases"""
    
    @staticmethod
    def for_educational_use() -> DebateConfig:
        """Configuration optimized for educational platforms"""
        return DebateConfig(
            reasoning_type=ReasoningType.ITERATIVE_DRAFTING,
            search_strategy=SearchStrategy.BEAM_SEARCH,
            depth=2,
            top_k=2,
            response_length="a paragraph",
            communication_tone="logical",
            use_chain_of_thought=True
        )
    
    @staticmethod
    def for_content_generation() -> DebateConfig:
        """Configuration optimized for content generation"""
        return DebateConfig(
            reasoning_type=ReasoningType.PLAN_AND_EXECUTE,
            search_strategy=SearchStrategy.BEAM_SEARCH,
            depth=3,
            top_k=3,
            response_length="a few paragraphs",
            communication_tone="logical",
            generation_temperature=0.8
        )
    
    @staticmethod
    def for_research_analysis() -> DebateConfig:
        """Configuration optimized for research and analysis"""
        return DebateConfig(
            reasoning_type=ReasoningType.PLAN_AND_EXECUTE,
            search_strategy=SearchStrategy.MONTE_CARLO,
            depth=4,
            top_k=3,
            response_length="a few paragraphs",
            communication_tone="logical",
            mcts_iterations=15,
            n_samples_generation=5,
            n_samples_judge=7
        )
    
    @staticmethod
    def for_fast_response() -> DebateConfig:
        """Configuration optimized for fast responses"""
        return DebateConfig(
            reasoning_type=ReasoningType.ITERATIVE_DRAFTING,
            search_strategy=SearchStrategy.BEAM_SEARCH,
            depth=1,
            top_k=1,
            n_samples_generation=1,
            n_samples_judge=1,
            response_length="a few sentences"
        )


class DebateAgent:
    """Simplified interface for strategic debate generation"""
    
    def __init__(self, config: Optional[DebateConfig] = None, openai_key: Optional[str] = None, openai_key_path: Optional[str] = None):
        """
        Initialize the debate agent
        
        Args:
            config: Configuration for the debate system
            openai_key: OpenAI API key (if not provided, will try to load from file)
            openai_key_path: Path to file containing OpenAI API key
        """
        self.config = config or DebateConfig()
        self.logger = logging.getLogger(__name__)
        
        # Handle OpenAI key setup
        if openai_key:
            # If key is provided directly, write it to a temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(openai_key)
                key_file_path = f.name
            try:
                # Setup DSPy
                set_up_dspy(
                    openai_key_path=key_file_path,
                    model_name=self.config.model_name,
                    max_tokens=self.config.max_tokens
                )
            finally:
                # Ensure the temporary file is deleted
                import os
                os.remove(key_file_path)
        else:
            key_file_path = openai_key_path or "openai_key.txt"
        
        # Setup DSPy
        set_up_dspy(
            openai_key_path=key_file_path,
            model_name=self.config.model_name,
            max_tokens=self.config.max_tokens
        )
        
        # Initialize the appropriate tree of thoughts module
        self._initialize_tot_module()
    
    def _initialize_tot_module(self):
        """Initialize the tree of thoughts module based on configuration"""
        if self.config.reasoning_type == ReasoningType.ITERATIVE_DRAFTING:
            if self.config.search_strategy == SearchStrategy.MONTE_CARLO:
                self.tot_module = IterativeDraftingMCTSTreeOfThoughts(
                    use_chain_of_thought=self.config.use_chain_of_thought,
                    node_selection_strategy=self.config.node_selection_strategy,
                    evaluation_strategy=self.config.evaluation_strategy.value
                )
            else:
                self.tot_module = IterativeDraftingTreeOfThoughts(
                    use_chain_of_thought=self.config.use_chain_of_thought,
                    node_selection_strategy=self.config.node_selection_strategy,
                    evaluation_strategy=self.config.evaluation_strategy.value,
                    do_pruning=self.config.do_pruning
                )
        else:  # PLAN_AND_EXECUTE
            if self.config.search_strategy == SearchStrategy.MONTE_CARLO:
                self.tot_module = PlanAndExecuteMCTSTreeOfThoughts(
                    use_chain_of_thought=self.config.use_chain_of_thought,
                    node_selection_strategy=self.config.node_selection_strategy,
                    evaluation_strategy=self.config.evaluation_strategy.value
                )
            else:
                self.tot_module = PlanAndExecuteTreeOfThoughts(
                    use_chain_of_thought=self.config.use_chain_of_thought,
                    node_selection_strategy=self.config.node_selection_strategy,
                    evaluation_strategy=self.config.evaluation_strategy.value,
                    do_pruning=self.config.do_pruning
                )
    
    def generate_argument(
        self, 
        topic: str, 
        stance: str, 
        conversation: Optional[List[str]] = None,
        visualize: bool = False,
        save_tree: bool = False
    ) -> str:
        """
        Generate a strategic argument for a given topic and stance
        
        Args:
            topic: The debate topic
            stance: The stance to take ("PRO" or "ANTI") 
            conversation: Optional conversation history
            visualize: Whether to visualize the tree of thoughts
            save_tree: Whether to save the tree to file
            
        Returns:
            Generated argument string
        """
        # Create conversation state using helper method
        state = self.create_state(topic, stance, conversation)
        
        # Create response parameters
        response_parameters = ResponseParameters(
            response_length=self.config.response_length,
            communication_tone=self.config.communication_tone,
            language_style=self.config.language_style
        )
        
        # Generate argument based on search strategy
        if self.config.search_strategy == SearchStrategy.MONTE_CARLO:
            mcts_parameters = MonteCarloTreeOfThoughtParameters(
                monte_carlo_iterations=self.config.mcts_iterations,
                rollout_depth=self.config.depth,
                generation_temperature=self.config.generation_temperature,
                judge_temperature=self.config.judge_temperature,
                n_samples_generation=self.config.n_samples_generation,
                n_samples_judge=self.config.n_samples_judge
            )
            
            return self.tot_module(
                state=state,
                mcts_parameters=mcts_parameters,
                response_parameters=response_parameters,
                do_visualize_tree=visualize,
                do_save_tree=save_tree
            )
        else:
            tot_parameters = TreeOfThoughtsParameters(
                depth=self.config.depth,
                top_k=self.config.top_k,
                generation_temperature=self.config.generation_temperature,
                judge_temperature=self.config.judge_temperature,
                n_samples_generation=self.config.n_samples_generation,
                n_samples_judge=self.config.n_samples_judge
            )
            
            return self.tot_module(
                state=state,
                tot_parameters=tot_parameters,
                response_parameters=response_parameters,
                do_visualize_tree=visualize,
                do_save_tree=save_tree
            )
    
    async def generate_argument_async(
        self, 
        topic: str, 
        stance: str, 
        conversation: Optional[List[str]] = None,
        visualize: bool = False,
        save_tree: bool = False
    ) -> str:
        """Async version of generate_argument"""
        return await asyncio.to_thread(
            self.generate_argument, 
            topic, stance, conversation, visualize, save_tree
        )


class StrategicDebatePipeline:
    """Pipeline for batch processing multiple debate topics"""
    
    def __init__(self, config: Optional[DebateConfig] = None, openai_key: Optional[str] = None, openai_key_path: Optional[str] = None):
        self.agent = DebateAgent(config, openai_key, openai_key_path)
    
    def batch_process(
        self, 
        topics: List[str], 
        stance_pairs: List[tuple],
        conversations: Optional[List[List[str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Process multiple topics and generate arguments for both sides
        
        Args:
            topics: List of debate topics
            stance_pairs: List of (pro_stance, con_stance) tuples
            conversations: Optional conversation histories for each topic
            
        Returns:
            List of dictionaries containing generated arguments
        """
        results = []
        conversations = conversations or [[] for _ in topics]
        
        for i, topic in enumerate(topics):
            pro_stance, con_stance = stance_pairs[i]
            conversation = conversations[i]
            
            pro_argument = self.agent.generate_argument(topic, pro_stance, conversation)
            con_argument = self.agent.generate_argument(topic, con_stance, conversation)
            
            results.append({
                "topic": topic,
                "pro_argument": pro_argument,
                "con_argument": con_argument
            })
        
        return results
    
    async def batch_process_async(
        self, 
        topics: List[str], 
        stance_pairs: List[tuple],
        conversations: Optional[List[List[str]]] = None
    ) -> List[Dict[str, str]]:
        """Async version of batch_process"""
        conversations = conversations or [[] for _ in topics]
        
        tasks = []
        for i, topic in enumerate(topics):
            pro_stance, con_stance = stance_pairs[i]
            conversation = conversations[i]
            
            tasks.append(self.agent.generate_argument_async(topic, pro_stance, conversation))
            tasks.append(self.agent.generate_argument_async(topic, con_stance, conversation))
        
        results = await asyncio.gather(*tasks)
        
        # Organize results
        formatted_results = []
        for i in range(0, len(results), 2):
            topic_idx = i // 2
            formatted_results.append({
                "topic": topics[topic_idx],
                "pro_argument": results[i],
                "con_argument": results[i + 1]
            })
        
        return formatted_results


class DebateSession:
    """Manage multi-turn debate sessions"""
    
    def __init__(self, topic: str, pro_agent: DebateAgent, con_agent: DebateAgent):
        self.topic = topic
        self.pro_agent = pro_agent
        self.con_agent = con_agent
        self.conversation_history = []
        self.current_turn = 0
    
    def next_turn(self) -> Dict[str, str]:
        """Execute the next turn in the debate"""
        if self.current_turn % 2 == 0:  # Pro turn
            agent = self.pro_agent
            stance = "PRO"
        else:  # Con turn
            agent = self.con_agent
            stance = "ANTI"
        
        argument = agent.generate_argument(
            topic=self.topic,
            stance=stance,
            conversation=self.conversation_history
        )
        
        self.conversation_history.append(argument)
        self.current_turn += 1
        
        return {
            "turn": self.current_turn,
            "stance": stance,
            "argument": argument
        }
    
    def get_full_debate(self) -> List[Dict[str, str]]:
        """Get the complete debate history"""
        debate = []
        for i, argument in enumerate(self.conversation_history):
            stance = "PRO" if i % 2 == 0 else "ANTI"
            debate.append({
                "turn": i + 1,
                "stance": stance,
                "argument": argument
            })
        return debate


# Convenience function for quick argument generation
def generate_quick_argument(topic: str, stance: str, use_case: str = "educational", openai_key_path: str = "openai_key.txt") -> str:
    """
    Generate a quick argument using predefined configurations
    
    Args:
        topic: The debate topic
        stance: The stance ("PRO" or "ANTI")
        use_case: Predefined use case ("educational", "content", "research", "fast")
    
    Returns:
        Generated argument
    """
    config_map = {
        "educational": QuickConfig.for_educational_use(),
        "content": QuickConfig.for_content_generation(),
        "research": QuickConfig.for_research_analysis(),
        "fast": QuickConfig.for_fast_response()
    }
    
    config = config_map.get(use_case, QuickConfig.for_educational_use())
    agent = DebateAgent(config, openai_key_path=openai_key_path)
    
    return agent.generate_argument(topic, stance)