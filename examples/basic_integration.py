"""
Basic Integration Example

This example shows the simplest way to integrate strategic debate 
capabilities into your application or workflow.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategic_debate import DebateAgent, QuickConfig, generate_quick_argument


def basic_usage_example():
    """Demonstrates basic usage of the strategic debate library"""
    print("=== Basic Strategic Debate Integration Example ===\n")
    
    # Example 1: Quick argument generation
    print("1. Quick Argument Generation:")
    topic = "Remote work should be the default for office jobs"
    
    # Generate arguments for both sides quickly
    pro_argument = generate_quick_argument(topic, "PRO", use_case="fast")
    con_argument = generate_quick_argument(topic, "ANTI", use_case="fast")
    
    print(f"Topic: {topic}")
    print(f"PRO Argument: {pro_argument}")
    print(f"ANTI Argument: {con_argument}")
    print()
    
    # Example 2: Using configured agent
    print("2. Using Configured Debate Agent:")
    
    # Use predefined configuration for educational use
    config = QuickConfig.for_educational_use()
    agent = DebateAgent(config)
    
    # Generate a more detailed argument
    detailed_topic = "Social media platforms should be regulated like public utilities"
    detailed_argument = agent.generate_argument(
        topic=detailed_topic,
        stance="PRO"
    )
    
    print(f"Topic: {detailed_topic}")
    print(f"Detailed Argument: {detailed_argument}")
    print()
    
    # Example 3: Multi-turn conversation
    print("3. Multi-turn Conversation:")
    
    conversation_topic = "Universal Basic Income should be implemented globally"
    conversation = []
    
    # First argument
    first_arg = agent.generate_argument(
        topic=conversation_topic,
        stance="PRO",
        conversation=conversation
    )
    conversation.append(first_arg)
    print(f"First Argument (PRO): {first_arg}")
    
    # Response argument
    response_arg = agent.generate_argument(
        topic=conversation_topic,
        stance="ANTI", 
        conversation=conversation
    )
    conversation.append(response_arg)
    print(f"Response Argument (ANTI): {response_arg}")
    
    # Counter-response
    counter_response = agent.generate_argument(
        topic=conversation_topic,
        stance="PRO",
        conversation=conversation
    )
    print(f"Counter-response (PRO): {counter_response}")


def integration_in_application():
    """Shows how to integrate into a larger application"""
    print("\n=== Application Integration Example ===\n")
    
    class SimpleDebateApp:
        """Example application that uses strategic debate capabilities"""
        
        def __init__(self):
            # Use content generation config for marketing/content apps
            self.debate_agent = DebateAgent(QuickConfig.for_content_generation())
            self.debate_history = {}
        
        def generate_marketing_copy(self, product, benefit):
            """Generate persuasive marketing copy"""
            topic = f"{product} provides {benefit}"
            return self.debate_agent.generate_argument(topic, "PRO")
        
        def analyze_position(self, statement):
            """Analyze both sides of a position"""
            pro_arg = self.debate_agent.generate_argument(statement, "PRO")
            con_arg = self.debate_agent.generate_argument(statement, "ANTI")
            
            return {
                "statement": statement,
                "supporting_argument": pro_arg,
                "opposing_argument": con_arg
            }
        
        def debate_session(self, topic, turns=3):
            """Run a debate session"""
            if topic not in self.debate_history:
                self.debate_history[topic] = []
            
            for turn in range(turns):
                stance = "PRO" if turn % 2 == 0 else "ANTI"
                argument = self.debate_agent.generate_argument(
                    topic=topic,
                    stance=stance,
                    conversation=self.debate_history[topic]
                )
                
                self.debate_history[topic].append(argument)
                print(f"Turn {turn + 1} ({stance}): {argument}")
    
    # Demo the application
    app = SimpleDebateApp()
    
    # Marketing copy generation
    print("Marketing Copy Generation:")
    copy = app.generate_marketing_copy(
        "our new AI assistant", 
        "increased productivity"
    )
    print(f"Generated copy: {copy}\n")
    
    # Position analysis
    print("Position Analysis:")
    analysis = app.analyze_position("Companies should adopt 4-day work weeks")
    print(f"Statement: {analysis['statement']}")
    print(f"Supporting: {analysis['supporting_argument']}")
    print(f"Opposing: {analysis['opposing_argument']}\n")
    
    # Debate session
    print("Debate Session:")
    app.debate_session("Artificial Intelligence will replace most jobs", turns=2)


if __name__ == "__main__":
    # Note: You'll need to have an OpenAI API key in openai_key.txt to run this
    try:
        basic_usage_example()
        integration_in_application()
    except FileNotFoundError:
        print("Error: Please create an 'openai_key.txt' file with your OpenAI API key to run this example.")
    except Exception as e:
        print(f"Error running example: {e}")
        print("Make sure you have set up the environment properly and have a valid OpenAI API key.")