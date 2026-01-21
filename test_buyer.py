#!/usr/bin/env python3
"""
Test Buyer Script - Simulate purchasing agent services

This script demonstrates how to:
1. Discover agents in registry
2. Create payment requests
3. Start jobs with payments
4. Monitor job status
5. Receive results

Usage:
    python test_buyer.py
"""
import asyncio
import os
from dotenv import load_dotenv
from masumi import Config, Purchase, Agent
from masumi.helper_functions import create_masumi_input_hash
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


async def discover_agent():
    """
    Step 1: Discover available agents in registry
    """
    logger.info("=== Step 1: Discovering Agents ===")

    config = Config(
        registry_service_url=os.getenv("REGISTRY_SERVICE_URL", "https://registry.masumi.network/api/v1"),
        registry_api_key=os.getenv("REGISTRY_API_KEY", "")
    )

    # Search for agents by identifier
    agent_identifier = os.getenv("AGENT_IDENTIFIER", "")

    if not agent_identifier:
        logger.error("AGENT_IDENTIFIER not set in .env file")
        return None

    try:
        agent = Agent(agent_identifier=agent_identifier, config=config)
        agent_info = await agent.get_agent_info()

        logger.info(f"Found agent: {agent_info.get('name', 'Unknown')}")
        logger.info(f"Description: {agent_info.get('description', 'N/A')}")
        logger.info(f"Status: {agent_info.get('status', 'Unknown')}")

        return agent

    except Exception as e:
        logger.error(f"Error discovering agent: {str(e)}")
        return None


async def check_availability(agent_identifier: str):
    """
    Step 2: Check if agent is available
    """
    logger.info("\n=== Step 2: Checking Availability ===")

    config = Config(
        registry_service_url=os.getenv("REGISTRY_SERVICE_URL", "https://registry.masumi.network/api/v1"),
        registry_api_key=os.getenv("REGISTRY_API_KEY", "")
    )

    try:
        agent = Agent(agent_identifier=agent_identifier, config=config)
        availability = await agent.check_availability()

        logger.info(f"Agent availability: {availability.get('status', 'Unknown')}")
        return availability.get('status') == 'available'

    except Exception as e:
        logger.error(f"Error checking availability: {str(e)}")
        return False


async def test_payment_flow():
    """
    Step 3: Complete payment flow - create payment, start job, monitor status
    """
    logger.info("\n=== Step 3: Starting Payment Flow ===")

    # Configuration
    config = Config(
        payment_service_url=os.getenv("PAYMENT_SERVICE_URL", "http://localhost:3001/api/v1"),
        payment_api_key=os.getenv("PAYMENT_API_KEY", ""),
        registry_service_url=os.getenv("REGISTRY_SERVICE_URL", "https://registry.masumi.network/api/v1"),
        registry_api_key=os.getenv("REGISTRY_API_KEY", "")
    )

    agent_identifier = os.getenv("AGENT_IDENTIFIER", "")

    # Create purchase instance
    purchase = Purchase(
        agent_identifier=agent_identifier,
        config=config
    )

    # Define job input
    input_data = {
        "text": "This AI agent platform is incredible! The payment integration works flawlessly. Highly recommended for developers building autonomous agents. The documentation could be more detailed though.",
        "analysis_type": "sentiment"
    }

    logger.info(f"Input data: {json.dumps(input_data, indent=2)}")

    try:
        # Start job with payment
        logger.info("\n--- Creating Payment and Starting Job ---")

        result = await purchase.start_job_with_payment(
            input_data=input_data,
            payment_amount=10000000,  # 10 ADA in lovelace (1 ADA = 1,000,000 lovelace)
            payment_unit="lovelace",
            pay_by_time=int((asyncio.get_event_loop().time() + 300) * 1000),  # 5 minutes from now
            submit_result_time=int((asyncio.get_event_loop().time() + 600) * 1000),  # 10 minutes from now
        )

        logger.info(f"Job started successfully!")
        logger.info(f"Job ID: {result.get('job_id', 'N/A')}")
        logger.info(f"Blockchain ID: {result.get('blockchain_identifier', 'N/A')}")

        job_id = result.get('job_id')
        blockchain_id = result.get('blockchain_identifier')

        # Monitor job status
        logger.info("\n--- Monitoring Job Status ---")

        max_attempts = 30
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            await asyncio.sleep(10)  # Check every 10 seconds

            status_result = await purchase.get_job_status(job_id)

            logger.info(f"Attempt {attempt}: Status = {status_result.get('status', 'Unknown')}")

            if status_result.get('status') == 'completed':
                logger.info("\n=== Job Completed Successfully! ===")
                logger.info(f"Results:\n{json.dumps(status_result.get('result', {}), indent=2)}")

                # Payment is automatically completed by the agent
                logger.info("\nPayment released to agent automatically")
                break

            elif status_result.get('status') == 'failed':
                logger.error(f"Job failed: {status_result.get('error', 'Unknown error')}")
                break

            elif status_result.get('status') in ['processing', 'pending']:
                logger.info("Job still processing...")
                continue

            else:
                logger.warning(f"Unknown status: {status_result.get('status')}")

        if attempt >= max_attempts:
            logger.warning("Job monitoring timed out after 5 minutes")

    except Exception as e:
        logger.error(f"Error in payment flow: {str(e)}", exc_info=True)


async def test_multiple_analysis_types():
    """
    Test different analysis types
    """
    logger.info("\n=== Testing Multiple Analysis Types ===")

    config = Config(
        payment_service_url=os.getenv("PAYMENT_SERVICE_URL", "http://localhost:3001/api/v1"),
        payment_api_key=os.getenv("PAYMENT_API_KEY", ""),
        registry_service_url=os.getenv("REGISTRY_SERVICE_URL", "https://registry.masumi.network/api/v1"),
        registry_api_key=os.getenv("REGISTRY_API_KEY", "")
    )

    agent_identifier = os.getenv("AGENT_IDENTIFIER", "")
    purchase = Purchase(agent_identifier=agent_identifier, config=config)

    # Test cases
    test_cases = [
        {
            "name": "Sentiment Analysis",
            "input": {
                "text": "Amazing product! Love the features. Best purchase ever!",
                "analysis_type": "sentiment"
            }
        },
        {
            "name": "Text Summary",
            "input": {
                "text": "Artificial intelligence is transforming industries worldwide. Machine learning algorithms enable computers to learn from vast amounts of data. Deep learning, a subset of machine learning, uses neural networks to solve complex problems. Natural language processing helps computers understand and generate human language. Computer vision allows machines to interpret and analyze visual information from the world.",
                "analysis_type": "summary"
            }
        },
        {
            "name": "Text Statistics",
            "input": {
                "text": "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.",
                "analysis_type": "stats"
            }
        },
        {
            "name": "Keyword Extraction",
            "input": {
                "text": "Blockchain technology enables decentralized applications. Smart contracts automate transactions. Cryptocurrency provides digital payment systems. Decentralization increases security and transparency.",
                "analysis_type": "keywords"
            }
        }
    ]

    for test_case in test_cases:
        logger.info(f"\n--- Testing: {test_case['name']} ---")

        try:
            result = await purchase.start_job_with_payment(
                input_data=test_case['input'],
                payment_amount=5000000,  # 5 ADA
                payment_unit="lovelace"
            )

            job_id = result.get('job_id')

            # Wait for completion
            await asyncio.sleep(5)

            status = await purchase.get_job_status(job_id)
            logger.info(f"Result: {json.dumps(status.get('result', {}), indent=2)}")

        except Exception as e:
            logger.error(f"Error in test case '{test_case['name']}': {str(e)}")


async def main():
    """
    Main test flow
    """
    logger.info("=== Masumi Agent Test Buyer ===\n")

    # Check required environment variables
    required_vars = ["AGENT_IDENTIFIER", "PAYMENT_API_KEY", "PAYMENT_SERVICE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please create .env file with required variables")
        logger.error("See .env.example for template")
        return

    # Step 1: Discover agent
    agent = await discover_agent()
    if not agent:
        logger.error("Failed to discover agent - check AGENT_IDENTIFIER and registry connection")
        return

    # Step 2: Check availability
    agent_identifier = os.getenv("AGENT_IDENTIFIER")
    is_available = await check_availability(agent_identifier)

    if not is_available:
        logger.warning("Agent is not currently available - continuing anyway for testing")

    # Step 3: Test payment flow
    await test_payment_flow()

    # Optional: Test multiple analysis types
    # Uncomment to run additional tests
    # await test_multiple_analysis_types()

    logger.info("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
