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
try:
    from masumi import create_masumi_app, Config
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    print("✓ Successfully imported masumi")
except ImportError as e:
    print(f"ERROR: Failed to import required packages: {e}")
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
            "validations": []
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
                "description": "Optional: Required only for recommendations analysis. JSON array of user's past engagements",
                "placeholder": '[{"post_id": "post1", "action": "like", "timestamp": 1734567890}]'
            },
            "validations": [
                {"validation": "optional", "value": "true"}
            ]
        },
        {
            "id": "candidates",
            "type": "text",
            "name": "Candidate Posts",
            "data": {
                "description": "Optional: Required only for recommendations analysis. JSON array of posts to rank",
                "placeholder": '[{"post_id": "cand1", "text": "Breaking news about AI", "author_id": "user123", "media_type": "text"}]'
            },
            "validations": [
                {"validation": "optional", "value": "true"}
            ]
        },
        {
            "id": "max_keywords",
            "type": "number",
            "name": "Maximum Keywords",
            "data": {
                "description": "Optional: Maximum number of keywords to extract (1-100, default: 10)"
            },
            "validations": [
                {"validation": "optional", "value": "true"},
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
                "description": "Optional: Number of sentences in summary (1-20, default: 3)"
            },
            "validations": [
                {"validation": "optional", "value": "true"},
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
                "description": "Optional: Number of top recommendations to return (1-100, default: 10)"
            },
            "validations": [
                {"validation": "optional", "value": "true"},
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

    # Load configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    agent_identifier = os.getenv("AGENT_IDENTIFIER")
    network = os.getenv("NETWORK", "Preprod")
    seller_vkey = os.getenv("SELLER_VKEY")
    payment_service_url = os.getenv("PAYMENT_SERVICE_URL", "https://payment-service.preprod.masumi.network/api/v1")
    payment_api_key = os.getenv("PAYMENT_API_KEY", "")

    # Create masumi config
    config = Config(
        payment_service_url=payment_service_url,
        payment_api_key=payment_api_key
    )

    # Create FastAPI app with Masumi integration
    app = create_masumi_app(
        config=config,
        agent_identifier=agent_identifier,
        network=network,
        seller_vkey=seller_vkey,
        start_job_handler=process_job,
        input_schema_handler=INPUT_SCHEMA
    )

    # *** ADD CORS MIDDLEWARE ***
    # This is required for Sokosumi (browser-based UI) to fetch the schema
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (Sokosumi needs this)
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )

    # Display startup information
    print("\n" + "="*70)
    print("🚀 Starting X-Analyst Agent Server...")
    print("="*70)
    print(f"Python Version:           {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"Agent Identifier:         {agent_identifier}")
    print(f"Network:                  {network}")
    print(f"API Documentation:        http://127.0.0.1:{port}/docs")
    print(f"Availability Check:       http://127.0.0.1:{port}/availability")
    print(f"Input Schema:             http://127.0.0.1:{port}/input_schema")
    print(f"Start Job:                http://127.0.0.1:{port}/start_job")
    print("="*70 + "\n")

    # Run server
    uvicorn.run(app, host=host, port=port)


# OLD FALLBACK CODE (no longer used, but kept for reference)
if False:
        # Fallback to manual MasumiAgentServer initialization
        # (for older masumi versions that don't have run())
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8080"))
        agent_identifier = os.getenv("AGENT_IDENTIFIER")  # Optional - will warn if not set
        network = os.getenv("NETWORK", "Preprod")
        seller_vkey = os.getenv("SELLER_VKEY")  # REQUIRED in updated masumi
        payment_service_url = os.getenv("PAYMENT_SERVICE_URL")
        payment_api_key = os.getenv("PAYMENT_API_KEY")

        # Check if we have payment service configuration
        has_payment_service = payment_service_url and payment_api_key and seller_vkey

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
            # Note: Updated masumi requires SELLER_VKEY even for fallback mode
            # If SELLER_VKEY is missing, we'll run a basic FastAPI without MasumiAgentServer
            print("\n" + "="*70)
            print("⚠️  Running in FALLBACK MODE - basic FastAPI without payment verification")
            print("="*70)
            if not seller_vkey:
                print("⚠️  WARNING: SELLER_VKEY not set - MasumiAgentServer requires it")
                print("   Running basic FastAPI without Masumi integration")
            else:
                print("⚠️  Missing PAYMENT_SERVICE_URL or PAYMENT_API_KEY")
                print("   Running basic FastAPI without payment verification")
            print(f"Python Version:           {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
            print(f"Agent Identifier:         {agent_identifier or 'unregistered-agent'}")
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
