"""
Pipeline Integration Example

This example demonstrates how to integrate strategic debate capabilities
into data processing pipelines and batch workflows.
"""

import sys
import os
import asyncio
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategic_debate import (
    DebateAgent, QuickConfig, StrategicDebatePipeline,
    DebateConfig, ReasoningType, SearchStrategy
)


@dataclass
class PipelineInput:
    """Input structure for pipeline processing"""
    topic: str
    stance: Optional[str] = None
    context: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PipelineOutput:
    """Output structure for pipeline processing"""
    topic: str
    stance: str
    argument: str
    processing_time: float
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class DebatePipelineProcessor:
    """Pipeline processor for strategic debate tasks"""
    
    def __init__(self, config: Optional[DebateConfig] = None, batch_size: int = 10):
        self.config = config or QuickConfig.for_content_generation()
        self.batch_size = batch_size
        self.agent = DebateAgent(self.config)
        self.processed_count = 0
        self.total_processing_time = 0.0
    
    def process_single(self, input_item: PipelineInput) -> PipelineOutput:
        """Process a single input item"""
        start_time = time.time()
        
        stance = input_item.stance or "PRO"
        argument = self.agent.generate_argument(
            topic=input_item.topic,
            stance=stance,
            conversation=input_item.context or []
        )
        
        processing_time = time.time() - start_time
        self.total_processing_time += processing_time
        self.processed_count += 1
        
        return PipelineOutput(
            topic=input_item.topic,
            stance=stance,
            argument=argument,
            processing_time=processing_time,
            metadata=input_item.metadata
        )
    
    def process_batch(self, inputs: List[PipelineInput]) -> List[PipelineOutput]:
        """Process a batch of inputs"""
        results = []
        for input_item in inputs:
            result = self.process_single(input_item)
            results.append(result)
        return results
    
    async def process_batch_async(self, inputs: List[PipelineInput]) -> List[PipelineOutput]:
        """Process a batch of inputs asynchronously"""
        tasks = []
        for input_item in inputs:
            task = asyncio.create_task(self._process_single_async(input_item))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def _process_single_async(self, input_item: PipelineInput) -> PipelineOutput:
        """Async version of process_single"""
        start_time = time.time()
        
        stance = input_item.stance or "PRO"
        argument = await self.agent.generate_argument_async(
            topic=input_item.topic,
            stance=stance,
            conversation=input_item.context or []
        )
        
        processing_time = time.time() - start_time
        self.total_processing_time += processing_time
        self.processed_count += 1
        
        return PipelineOutput(
            topic=input_item.topic,
            stance=stance,
            argument=argument,
            processing_time=processing_time,
            metadata=input_item.metadata
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        avg_time = self.total_processing_time / self.processed_count if self.processed_count > 0 else 0
        return {
            "processed_count": self.processed_count,
            "total_processing_time": self.total_processing_time,
            "average_processing_time": avg_time,
            "throughput_per_second": 1.0 / avg_time if avg_time > 0 else 0
        }


class DebateDataPipeline:
    """Complete data pipeline for debate processing"""
    
    def __init__(self, config: Optional[DebateConfig] = None):
        self.processor = DebatePipelineProcessor(config)
        self.results_store = []
        self.error_log = []
    
    def load_data(self, source: str) -> Iterator[PipelineInput]:
        """Load data from various sources"""
        if source.endswith('.json'):
            return self._load_from_json(source)
        elif source.endswith('.csv'):
            return self._load_from_csv(source)
        else:
            return self._load_from_list(source)
    
    def _load_from_json(self, filepath: str) -> Iterator[PipelineInput]:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                for item in data:
                    yield PipelineInput(**item)
        except Exception as e:
            self.error_log.append(f"Error loading JSON: {e}")
    
    def _load_from_csv(self, filepath: str) -> Iterator[PipelineInput]:
        """Load data from CSV file"""
        try:
            import csv
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield PipelineInput(
                        topic=row.get('topic', ''),
                        stance=row.get('stance'),
                        context=row.get('context', '').split('|') if row.get('context') else None,
                        metadata={"row_id": row.get('id')}
                    )
        except Exception as e:
            self.error_log.append(f"Error loading CSV: {e}")
    
    def _load_from_list(self, topic_list: List[str]) -> Iterator[PipelineInput]:
        """Load data from list of topics"""
        for i, topic in enumerate(topic_list):
            yield PipelineInput(
                topic=topic,
                metadata={"index": i}
            )
    
    def transform_data(self, inputs: Iterator[PipelineInput]) -> Iterator[PipelineInput]:
        """Transform data before processing"""
        for input_item in inputs:
            # Add any transformations here
            # For example, clean topic text, validate stance, etc.
            transformed_input = PipelineInput(
                topic=input_item.topic.strip(),
                stance=input_item.stance,
                context=input_item.context,
                metadata=input_item.metadata
            )
            yield transformed_input
    
    def process_pipeline(self, source: str, output_file: Optional[str] = None) -> List[PipelineOutput]:
        """Run the complete pipeline"""
        print(f"Starting pipeline processing from: {source}")
        
        # Load and transform data
        raw_data = list(self.load_data(source))
        transformed_data = list(self.transform_data(iter(raw_data)))
        
        print(f"Loaded {len(transformed_data)} items for processing")
        
        # Process in batches
        results = []
        batch_size = self.processor.batch_size
        
        for i in range(0, len(transformed_data), batch_size):
            batch = transformed_data[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(transformed_data) + batch_size - 1)//batch_size}")
            
            try:
                batch_results = self.processor.process_batch(batch)
                results.extend(batch_results)
            except Exception as e:
                self.error_log.append(f"Error processing batch {i//batch_size + 1}: {e}")
        
        # Store results
        self.results_store.extend(results)
        
        # Save to file if specified
        if output_file:
            self.save_results(results, output_file)
        
        print(f"Pipeline completed. Processed {len(results)} items.")
        print(f"Processing stats: {self.processor.get_stats()}")
        
        return results
    
    async def process_pipeline_async(self, source: str, output_file: Optional[str] = None) -> List[PipelineOutput]:
        """Run the complete pipeline asynchronously"""
        print(f"Starting async pipeline processing from: {source}")
        
        # Load and transform data
        raw_data = list(self.load_data(source))
        transformed_data = list(self.transform_data(iter(raw_data)))
        
        print(f"Loaded {len(transformed_data)} items for processing")
        
        # Process in batches asynchronously
        results = []
        batch_size = self.processor.batch_size
        
        tasks = []
        for i in range(0, len(transformed_data), batch_size):
            batch = transformed_data[i:i + batch_size]
            task = asyncio.create_task(self.processor.process_batch_async(batch))
            tasks.append(task)
        
        print(f"Processing {len(tasks)} batches concurrently...")
        
        try:
            batch_results = await asyncio.gather(*tasks)
            for batch_result in batch_results:
                results.extend(batch_result)
        except Exception as e:
            self.error_log.append(f"Error in async processing: {e}")
        
        # Store results
        self.results_store.extend(results)
        
        # Save to file if specified
        if output_file:
            self.save_results(results, output_file)
        
        print(f"Async pipeline completed. Processed {len(results)} items.")
        print(f"Processing stats: {self.processor.get_stats()}")
        
        return results
    
    def save_results(self, results: List[PipelineOutput], filepath: str):
        """Save results to file"""
        try:
            if filepath.endswith('.json'):
                with open(filepath, 'w') as f:
                    json.dump([asdict(result) for result in results], f, indent=2)
            elif filepath.endswith('.csv'):
                import csv
                with open(filepath, 'w', newline='') as f:
                    if results:
                        fieldnames = asdict(results[0]).keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for result in results:
                            writer.writerow(asdict(result))
            print(f"Results saved to: {filepath}")
        except Exception as e:
            self.error_log.append(f"Error saving results: {e}")


class ParallelDebatePipeline:
    """Pipeline with parallel processing capabilities"""
    
    def __init__(self, config: Optional[DebateConfig] = None, max_workers: int = 4):
        self.config = config or QuickConfig.for_fast_response()
        self.max_workers = max_workers
        self.results = []
        self.errors = []
    
    def process_parallel(self, inputs: List[PipelineInput]) -> List[PipelineOutput]:
        """Process inputs in parallel using ThreadPoolExecutor"""
        print(f"Processing {len(inputs)} items with {self.max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create separate agent for each worker to avoid conflicts
            future_to_input = {}
            
            for input_item in inputs:
                agent = DebateAgent(self.config)
                future = executor.submit(self._process_with_agent, agent, input_item)
                future_to_input[future] = input_item
            
            results = []
            for future in as_completed(future_to_input):
                input_item = future_to_input[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✓ Processed: {input_item.topic[:50]}...")
                except Exception as e:
                    self.errors.append(f"Error processing {input_item.topic}: {e}")
                    print(f"✗ Error: {input_item.topic[:50]}...")
        
        return results
    
    def _process_with_agent(self, agent: DebateAgent, input_item: PipelineInput) -> PipelineOutput:
        """Process single item with given agent"""
        start_time = time.time()
        
        stance = input_item.stance or "PRO"
        argument = agent.generate_argument(
            topic=input_item.topic,
            stance=stance,
            conversation=input_item.context or []
        )
        
        processing_time = time.time() - start_time
        
        return PipelineOutput(
            topic=input_item.topic,
            stance=stance,
            argument=argument,
            processing_time=processing_time,
            metadata=input_item.metadata
        )


# Example usage and demonstrations
def create_sample_data():
    """Create sample data for testing"""
    topics = [
        "Remote work improves work-life balance",
        "Electric vehicles are better for the environment",
        "Social media has a positive impact on society",
        "Artificial intelligence will create more jobs than it destroys",
        "Renewable energy is more cost-effective than fossil fuels",
        "Online education is as effective as in-person learning",
        "Universal healthcare improves overall public health",
        "Space exploration is a worthwhile investment",
        "Automation will lead to better working conditions",
        "Cryptocurrency will replace traditional banking"
    ]
    
    # Create sample JSON data
    sample_data = [
        {
            "topic": topic,
            "stance": "PRO" if i % 2 == 0 else "ANTI",
            "metadata": {"category": "technology" if "AI" in topic or "electric" in topic else "society"}
        }
        for i, topic in enumerate(topics)
    ]
    
    with open('/tmp/sample_debate_topics.json', 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print("Sample data created at: /tmp/sample_debate_topics.json")
    return "/tmp/sample_debate_topics.json"


def demonstrate_basic_pipeline():
    """Demonstrate basic pipeline functionality"""
    print("=== Basic Pipeline Integration ===\n")
    
    # Create sample data
    sample_file = create_sample_data()
    
    # Create and run pipeline
    pipeline = DebateDataPipeline(QuickConfig.for_fast_response())
    
    print("Running synchronous pipeline...")
    results = pipeline.process_pipeline(
        source=sample_file,
        output_file="/tmp/debate_results.json"
    )
    
    print(f"\nProcessed {len(results)} items")
    print("Sample result:")
    if results:
        sample = results[0]
        print(f"  Topic: {sample.topic}")
        print(f"  Stance: {sample.stance}")
        print(f"  Argument: {sample.argument[:100]}...")
        print(f"  Processing time: {sample.processing_time:.2f}s")


async def demonstrate_async_pipeline():
    """Demonstrate async pipeline functionality"""
    print("\n=== Async Pipeline Integration ===\n")
    
    # Create sample data
    topics = [
        "Climate change requires immediate action",
        "Nuclear energy is safe and clean",
        "Genetic engineering should be regulated",
        "Virtual reality will transform education",
        "Blockchain technology ensures data privacy"
    ]
    
    # Create pipeline inputs
    inputs = [PipelineInput(topic=topic, metadata={"batch": "async_demo"}) for topic in topics]
    
    # Create processor and run async
    processor = DebatePipelineProcessor(QuickConfig.for_educational_use())
    
    print(f"Processing {len(inputs)} items asynchronously...")
    start_time = time.time()
    results = await processor.process_batch_async(inputs)
    total_time = time.time() - start_time
    
    print(f"Async processing completed in {total_time:.2f}s")
    print(f"Average time per item: {total_time/len(results):.2f}s")
    print(f"Throughput: {len(results)/total_time:.2f} items/second")


def demonstrate_parallel_pipeline():
    """Demonstrate parallel pipeline functionality"""
    print("\n=== Parallel Pipeline Integration ===\n")
    
    # Create test inputs
    topics = [
        "Flexible work schedules increase productivity",
        "Electric cars will dominate the automotive market",
        "Social media algorithms should be transparent",
        "Telemedicine improves healthcare accessibility",
        "Renewable energy creates sustainable economic growth",
        "Distance learning democratizes education",
        "Digital privacy is a fundamental right",
        "Automation enhances human creativity"
    ]
    
    inputs = [
        PipelineInput(
            topic=topic,
            stance="PRO" if i % 2 == 0 else "ANTI",
            metadata={"priority": "high" if i < 4 else "medium"}
        )
        for i, topic in enumerate(topics)
    ]
    
    # Run parallel processing
    parallel_pipeline = ParallelDebatePipeline(
        config=QuickConfig.for_fast_response(),
        max_workers=3
    )
    
    print(f"Processing {len(inputs)} items in parallel...")
    start_time = time.time()
    results = parallel_pipeline.process_parallel(inputs)
    total_time = time.time() - start_time
    
    print(f"\nParallel processing completed in {total_time:.2f}s")
    print(f"Successfully processed: {len(results)}/{len(inputs)} items")
    print(f"Errors: {len(parallel_pipeline.errors)}")
    
    if parallel_pipeline.errors:
        print("Errors encountered:")
        for error in parallel_pipeline.errors:
            print(f"  - {error}")


def demonstrate_integration_patterns():
    """Demonstrate various integration patterns"""
    print("\n=== Integration Patterns ===\n")
    
    print("1. ETL Pipeline Integration:")
    print("   - Extract: Load topics from databases, APIs, or files")
    print("   - Transform: Clean and validate topic data")
    print("   - Load: Generate arguments and store results")
    print()
    
    print("2. Stream Processing Integration:")
    print("   - Real-time topic streams (Kafka, RabbitMQ)")
    print("   - Async processing with queue management")
    print("   - Backpressure handling for rate limiting")
    print()
    
    print("3. Batch Job Integration:")
    print("   - Scheduled argument generation jobs")
    print("   - Large-scale dataset processing")
    print("   - Results aggregation and reporting")
    print()
    
    print("4. Microservice Integration:")
    print("   - Containerized pipeline components")
    print("   - Scalable processing workers")
    print("   - Health monitoring and error recovery")


if __name__ == "__main__":
    async def main():
        try:
            demonstrate_basic_pipeline()
            await demonstrate_async_pipeline()
            demonstrate_parallel_pipeline()
            demonstrate_integration_patterns()
        except FileNotFoundError:
            print("Error: Please create an 'openai_key.txt' file with your OpenAI API key to run this example.")
        except Exception as e:
            print(f"Error running example: {e}")
            print("Make sure you have set up the environment properly and have a valid OpenAI API key.")
    
    asyncio.run(main())