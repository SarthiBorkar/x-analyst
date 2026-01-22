#!/usr/bin/env python3
"""
X-Analyst - Main Entry Point

AI-powered text analysis agent with Masumi payment integration.
Supports sentiment analysis, summarization, statistics, keywords, and Phoenix recommendations.
"""
import os
import sys

# Ensure Python 3.9+
if sys.version_info < (3, 9):
    print(f"ERROR: Python 3.9+ required, found {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

# Import masumi with detailed error handling
try:
    from masumi import run, create_masumi_app, Config
    import uvicorn
    print("✓ Successfully imported masumi (version 0.1.41+)")
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
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Get environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))

    # Display startup info
    print("\n" + "="*70)
    print("🚀 Starting X-Analyst Agent Server...")
    print("="*70)
    print(f"Python Version:           {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"API Documentation:        http://{host}:{port}/docs")
    print(f"Availability Check:       http://{host}:{port}/availability")
    print(f"Input Schema:             http://{host}:{port}/input_schema")
    print(f"Start Job:                http://{host}:{port}/start_job")
    print("="*70 + "\n")

    # Use the simplified run() API (available in masumi 0.1.41)
    run(
        start_job_handler=process_job,
        input_schema_handler=INPUT_SCHEMA
    )
