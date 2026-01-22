#!/usr/bin/env python3
"""
X-Analyst - Main Entry Point

AI-powered text analysis agent with Masumi payment integration.
Supports sentiment analysis, summarization, statistics, keywords, and Phoenix recommendations.
"""
import os
import sys

# Try new API first (local dev), fallback to stable API (PyPI)
try:
    from masumi import run
    USE_NEW_API = True
except ImportError:
    from masumi import create_masumi_app, Config
    import uvicorn
    USE_NEW_API = False

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
    if USE_NEW_API:
        # New API (local dev with latest masumi)
        run(
            start_job_handler=process_job,
            input_schema_handler=INPUT_SCHEMA
        )
    else:
        # Stable API (PyPI masumi 0.1.41)
        from dotenv import load_dotenv
        load_dotenv()

        # Get environment variables
        payment_service_url = os.getenv(
            "PAYMENT_SERVICE_URL",
            "https://payment.masumi.network/api/v1"
        )
        payment_api_key = os.getenv("PAYMENT_API_KEY", "")
        agent_identifier = os.getenv("AGENT_IDENTIFIER")
        network = os.getenv("NETWORK", "Preprod")
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8080))
        seller_vkey = os.getenv("SELLER_VKEY")

        # Create config
        config = Config(
            payment_service_url=payment_service_url,
            payment_api_key=payment_api_key
        )

        # Create FastAPI app
        app = create_masumi_app(
            config=config,
            agent_identifier=agent_identifier,
            network=network,
            seller_vkey=seller_vkey,
            start_job_handler=process_job,
            input_schema_handler=INPUT_SCHEMA
        )

        # Display startup info
        print("\n" + "="*70)
        print("🚀 Starting X-Analyst Agent Server...")
        print("="*70)
        print(f"API Documentation:        http://{host}:{port}/docs")
        print(f"Availability Check:       http://{host}:{port}/availability")
        print(f"Input Schema:             http://{host}:{port}/input_schema")
        print(f"Start Job:                http://{host}:{port}/start_job")
        print("="*70 + "\n")

        # Run server
        uvicorn.run(app, host=host, port=port)
