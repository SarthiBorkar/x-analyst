#!/usr/bin/env python3
"""
X-Analyst - Main Entry Point

AI-powered text analysis agent with Masumi payment integration.
Supports sentiment analysis, summarization, statistics, keywords, and Phoenix recommendations.
"""
from masumi import run
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
    # masumi.run() handles everything:
    # - Loads .env automatically
    # - Creates Config from environment variables
    # - Supports --standalone mode for testing
    # - Defaults PAYMENT_SERVICE_URL to https://payment.masumi.network/api/v1
    # - Runs FastAPI server with beautiful logging

    run(
        start_job_handler=process_job,
        input_schema_handler=INPUT_SCHEMA
    )
