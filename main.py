#!/usr/bin/env python3
"""
X-Analyst - Main Entry Point

AI-powered text analysis agent with Masumi payment integration.
Supports sentiment analysis, summarization, statistics, keywords, and Phoenix recommendations.
"""
import os
import sys

# Load environment variables FIRST, before any other imports
# This ensures .env file is loaded before masumi package tries to read env vars
from dotenv import load_dotenv
load_dotenv()

# Ensure Python 3.9+
if sys.version_info < (3, 9):
    print(f"ERROR: Python 3.9+ required, found {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

# Import masumi with detailed error handling
# Try to import the simplified run() API first (available in updated masumi)
try:
    from masumi import run
    print("✓ Successfully imported masumi.run() (simplified API)")
    USE_RUN_API = True
except ImportError:
    # Fallback to MasumiAgentServer if run() is not available
    try:
        from masumi import MasumiAgentServer, Config
        import uvicorn
        print("✓ Successfully imported masumi (using MasumiAgentServer API)")
        USE_RUN_API = False
    except ImportError as e:
        print(f"ERROR: Failed to import masumi: {e}")
        print("\nTroubleshooting:")
        print("1. Verify masumi is installed: pip show masumi")
        print("2. Check version: pip show masumi | grep Version")
        print("3. Reinstall: pip install --no-cache-dir masumi>=0.1.41")
        print("4. Python version: python --version (need 3.9+)")
        sys.exit(1)

from agent import process_job

# Define input schema
# Masumi expects {"input_data": [...]} format for MIP-003 compliance
INPUT_SCHEMA = {
    "input_data": [
        {
            "id": "analysis_type",
            "type": "option",
            "name": "Analysis Type",
            "data": {
                "description": "Type of analysis to perform",
                "values": ["sentiment", "summary", "stats", "keywords", "recommendations", "general"],
                "default": "general"
            },
            "validations": [
                {"validation": "required", "value": "true"}
            ]
        },
        {
            "id": "text",
            "type": "text",
            "name": "Text Input",
            "data": {
                "description": "Text to analyze (required for sentiment, summary, stats, keywords, general)",
                "placeholder": "Enter text to analyze (minimum 10 characters, maximum 100,000 characters)"
            },
            "validations": [
                {"validation": "min", "value": "10"},
                {"validation": "max", "value": "100000"}
            ]
        },
        {
            "id": "user_history",
            "type": "text",
            "name": "User Engagement History",
            "data": {
                "description": "Required for recommendations: JSON array of user's past engagements",
                "placeholder": '[{"post_id": "post1", "action": "like", "timestamp": 1734567890}]'
            },
            "validations": []
        },
        {
            "id": "candidates",
            "type": "text",
            "name": "Candidate Posts",
            "data": {
                "description": "Required for recommendations: JSON array of posts to rank",
                "placeholder": '[{"post_id": "cand1", "text": "Breaking news about AI", "author_id": "user123", "media_type": "text"}]'
            },
            "validations": []
        },
        {
            "id": "max_keywords",
            "type": "number",
            "name": "Maximum Keywords",
            "data": {
                "description": "Maximum number of keywords to extract (1-100, default: 10)"
            },
            "validations": [
                {"validation": "min", "value": "1"},
                {"validation": "max", "value": "100"},
                {"validation": "format", "value": "integer"}
            ]
        },
        {
            "id": "summary_sentences",
            "type": "number",
            "name": "Summary Sentences",
            "data": {
                "description": "Number of sentences in summary (1-20, default: 3)"
            },
            "validations": [
                {"validation": "min", "value": "1"},
                {"validation": "max", "value": "20"},
                {"validation": "format", "value": "integer"}
            ]
        },
        {
            "id": "top_k",
            "type": "number",
            "name": "Top K Recommendations",
            "data": {
                "description": "Number of top recommendations to return (1-100, default: 10)"
            },
            "validations": [
                {"validation": "min", "value": "1"},
                {"validation": "max", "value": "100"},
                {"validation": "format", "value": "integer"}
            ]
        }
    ]
}

# Main entry point
if __name__ == "__main__":
    # Environment variables are already loaded at the top of the file
    # (masumi.run() also loads dotenv internally, but loading early ensures consistency)
    
    if USE_RUN_API:
        # Use the simplified run() API (available in updated masumi)
        # This automatically handles:
        # - Config creation from environment variables
        # - MasumiAgentServer initialization
        # - FastAPI app creation
        # - Server startup with uvicorn
        run(
            start_job_handler=process_job,
            input_schema_handler=INPUT_SCHEMA
            # All other config (host, port, agent_identifier, network, etc.)
            # is automatically loaded from environment variables
        )
    else:
        # Fallback to manual MasumiAgentServer initialization
        # (for older masumi versions that don't have run())
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8080"))
        agent_identifier = os.getenv("AGENT_IDENTIFIER", "x-analyst-demo")
        network = os.getenv("NETWORK", "Preprod")
        seller_vkey = os.getenv("SELLER_VKEY")
        payment_service_url = os.getenv("PAYMENT_SERVICE_URL")
        payment_api_key = os.getenv("PAYMENT_API_KEY")

        # Check if we have payment service configuration
        has_payment_service = payment_service_url and payment_api_key

        if has_payment_service:
            # Full Masumi Mode - with payment verification
            print("\n" + "="*70)
            print("🚀 Starting X-Analyst Agent Server (Full Masumi Mode)...")
            print("="*70)
            print(f"Python Version:           {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
            print(f"Agent Identifier:        {agent_identifier}")
            print(f"Network:                 {network}")
            print(f"API Documentation:        http://{host}:{port}/docs")
            print(f"Availability Check:       http://{host}:{port}/availability")
            print(f"Input Schema:             http://{host}:{port}/input_schema")
            print(f"Start Job:                http://{host}:{port}/start_job")
            print("="*70 + "\n")

            # Create Config with required parameters
            config = Config(
                payment_service_url=payment_service_url,
                payment_api_key=payment_api_key
            )

            # Create MasumiAgentServer with config
            server = MasumiAgentServer(
                config=config,
                agent_identifier=agent_identifier,
                network=network,
                seller_vkey=seller_vkey,
                start_job_handler=process_job,
                input_schema_handler=INPUT_SCHEMA
            )

            # Get FastAPI app and run with uvicorn
            app = server.app
            uvicorn.run(app, host=host, port=port)

        else:
            # Fallback Mode - without payment verification (for testing)
            print("\n" + "="*70)
            print("⚠️  Running in FALLBACK MODE - basic FastAPI without payment verification")
            print("="*70)
            print("To enable full Masumi Mode, set PAYMENT_SERVICE_URL and PAYMENT_API_KEY")
            print(f"Python Version:           {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
            print(f"Agent Identifier:         {agent_identifier}")
            print(f"Network:                  {network}")
            print(f"API Documentation:        http://{host}:{port}/docs")
            print(f"Availability Check:       http://{host}:{port}/availability")
            print(f"Input Schema:             http://{host}:{port}/input_schema")
            print(f"Start Job:                http://{host}:{port}/start_job")
            print("="*70 + "\n")

            # Create a simple FastAPI app for fallback mode
            from fastapi import FastAPI, HTTPException
            from fastapi.responses import JSONResponse

            app = FastAPI(title="X-Analyst Agent (Fallback Mode)")

            @app.get("/availability")
            async def availability():
                return {"status": "available", "mode": "fallback"}

            @app.get("/input_schema")
            async def input_schema():
                return INPUT_SCHEMA

            @app.post("/start_job")
            async def start_job(request: dict):
                try:
                    identifier_from_purchaser = request.get("identifier_from_purchaser", "fallback_user")
                    input_data = request.get("input_data", {})
                    
                    result = await process_job(identifier_from_purchaser, input_data)
                    return result
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

            @app.get("/")
            async def root():
                return {
                    "service": "X-Analyst Agent",
                    "mode": "fallback",
                    "status": "running",
                    "endpoints": {
                        "availability": "/availability",
                        "input_schema": "/input_schema",
                        "start_job": "/start_job (POST)"
                    }
                }

            print("✓ Fallback FastAPI app initialized")
            print(f"🚀 Starting X-Analyst on {host}:{port}\n")
            uvicorn.run(app, host=host, port=port)
