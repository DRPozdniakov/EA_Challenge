"""
Simple Performance Test for WebSocket Voice Answer Service
-------------------------------------------------------
Basic performance test that measures:
- Response time
- Memory usage
- Basic error handling
- Concurrent request handling
"""

import asyncio
import time
import websockets
import psutil
import logging
import json
import pytest
from typing import List, Dict, Optional
from websockets.exceptions import WebSocketException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RESPONSE_TIME_THRESHOLD = 10.0
MEMORY_USAGE_THRESHOLD = 500

# Constants
CONNECTION_TIMEOUT = 10  # seconds
REQUEST_TIMEOUT = 30     # seconds
MAX_RETRIES = 3         # maximum number of retries for failed requests

class RequestResult:
    """Class to store request results and status."""
    def __init__(self, question: str, response_time: float = 0, error: Optional[str] = None):
        self.question = question
        self.response_time = response_time
        self.error = error
        self.success = error is None

@pytest.mark.asyncio
async def test_single_request():
    """Test a single request to the WebSocket server."""
    uri = "ws://localhost:8888"
    question = "What is the weather like?"
    
    try:
        # Measure connection time
        start_time = time.time()
        async with websockets.connect(uri) as websocket:
            connection_time = time.time() - start_time
            logger.info(f"Connection time: {connection_time:.2f} seconds")
            
            # Measure response time
            start_time = time.time()
            await websocket.send(json.dumps({"question": question}))
            response = await websocket.recv()
            response_time = time.time() - start_time
            
            # Get memory usage
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # Convert to MB
            
            # Print results
            print("\nTest Results:")
            print(f"Response time: {response_time:.2f} seconds")
            print(f"Memory usage: {memory_usage:.2f} MB")
            
            # Basic assertions
            assert response_time < RESPONSE_TIME_THRESHOLD, f"Response time should be under {RESPONSE_TIME_THRESHOLD} seconds"
            assert memory_usage < MEMORY_USAGE_THRESHOLD, f"Memory usage should be under {MEMORY_USAGE_THRESHOLD}MB"
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_multiple_requests():
    """Test multiple sequential requests."""
    uri = "ws://localhost:8888"
    questions = [
        "What is the date today",
        "Your name is Lora",
        "What time is it?"
    ]
    
    total_time = 0
    total_memory = 0
    
    for question in questions:
        try:
            async with websockets.connect(uri) as websocket:
                # Measure response time
                start_time = time.time()
                await websocket.send(json.dumps({"question": question}))
                response = await websocket.recv()
                response_time = time.time() - start_time
                total_time += response_time
                
                # Get memory usage
                process = psutil.Process()
                memory_usage = process.memory_info().rss / 1024 / 1024
                total_memory = max(total_memory, memory_usage)
                
                logger.info(f"Question: {question}")
                logger.info(f"Response time: {response_time:.2f} seconds")
                
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    # Print summary
    print("\nMultiple Requests Summary:")
    print(f"Average response time: {total_time/len(questions):.2f} seconds")
    print(f"Peak memory usage: {total_memory:.2f} MB")
    
    # Basic assertions
    assert total_time/len(questions) < RESPONSE_TIME_THRESHOLD, f"Average response time should be under {RESPONSE_TIME_THRESHOLD} seconds"
    assert total_memory < MEMORY_USAGE_THRESHOLD, f"Memory usage should be under {MEMORY_USAGE_THRESHOLD}MB"

async def make_request(uri: str, question: str, retry_count: int = 0) -> RequestResult:
    """Helper function to make a single request with timeout and retry logic."""
    try:
        start_time = time.time()
        async with websockets.connect(uri, close_timeout=CONNECTION_TIMEOUT) as websocket:
            # Set a timeout for the entire request
            async with asyncio.timeout(REQUEST_TIMEOUT):
                await websocket.send(json.dumps({"question": question}))
                response = await websocket.recv()
                end_time = time.time()
                return RequestResult(question, end_time - start_time)
                
    except asyncio.TimeoutError:
        error_msg = f"Request timed out after {REQUEST_TIMEOUT} seconds"
        logger.error(f"Timeout for question '{question}': {error_msg}")
        if retry_count < MAX_RETRIES:
            logger.info(f"Retrying request for '{question}' (attempt {retry_count + 1}/{MAX_RETRIES})")
            return await make_request(uri, question, retry_count + 1)
        return RequestResult(question, error=error_msg)
        
    except WebSocketException as e:
        error_msg = f"WebSocket error: {str(e)}"
        logger.error(f"WebSocket error for question '{question}': {error_msg}")
        if retry_count < MAX_RETRIES:
            logger.info(f"Retrying request for '{question}' (attempt {retry_count + 1}/{MAX_RETRIES})")
            return await make_request(uri, question, retry_count + 1)
        return RequestResult(question, error=error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Error for question '{question}': {error_msg}")
        return RequestResult(question, error=error_msg)

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test multiple concurrent requests to check simultaneous handling."""
    uri = "ws://localhost:8888"
    questions = [
        "What is the date today",
        "Your name is Lora",
        "What time is it?",
        "What is the weather like?",
        "Tell me a joke"
    ]
    
    # Start all requests concurrently
    start_time = time.time()
    tasks = [make_request(uri, question) for question in questions]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    # Process results
    successful_requests = [r for r in results if isinstance(r, RequestResult) and r.success]
    failed_requests = [r for r in results if isinstance(r, RequestResult) and not r.success]
    
    if successful_requests:
        response_times = [r.response_time for r in successful_requests]
        max_time = max(response_times)
        avg_time = sum(response_times) / len(response_times)
    else:
        max_time = avg_time = 0
    
    # Get peak memory usage
    process = psutil.Process()
    memory_usage = process.memory_info().rss / 1024 / 1024
    
    # Print detailed results
    print("\nConcurrent Requests Results:")
    print(f"Total time for all requests: {total_time:.2f} seconds")
    print(f"Number of concurrent requests: {len(questions)}")
    print(f"Successful requests: {len(successful_requests)}")
    print(f"Failed requests: {len(failed_requests)}")
    
    if successful_requests:
        print(f"Average response time: {avg_time:.2f} seconds")
        print(f"Maximum response time: {max_time:.2f} seconds")
    
    print(f"Peak memory usage: {memory_usage:.2f} MB")
    
    # Print individual request results
    print("\nIndividual Request Results:")
    for result in results:
        if isinstance(result, RequestResult):
            if result.success:
                print(f"{result.question}: {result.response_time:.2f} seconds")
            else:
                print(f"{result.question}: FAILED - {result.error}")
        else:
            print(f"Request failed with unexpected error: {str(result)}")
    
    # Print summary of failures
    if failed_requests:
        print("\nFailure Summary:")
        for result in failed_requests:
            print(f"- {result.question}: {result.error}")
    
    # Assertions
    if successful_requests:
        assert max_time < RESPONSE_TIME_THRESHOLD*2, f"Maximum response time should be under {RESPONSE_TIME_THRESHOLD*2} seconds"
        assert avg_time < RESPONSE_TIME_THRESHOLD*2, f"Average response time should be under {RESPONSE_TIME_THRESHOLD} seconds"
    assert memory_usage < MEMORY_USAGE_THRESHOLD, f"Memory usage should be under {MEMORY_USAGE_THRESHOLD}MB"
    assert len(failed_requests) < len(questions), "Too many failed requests"

# Keep the main block for direct script execution
if __name__ == "__main__":
    async def main():
        print("Running single request test...")
        await test_single_request()
        
        print("\nRunning multiple requests test...")
        await test_multiple_requests()
        
        print("\nRunning concurrent requests test...")
        await test_concurrent_requests()
    
    asyncio.run(main()) 