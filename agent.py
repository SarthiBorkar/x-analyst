#!/usr/bin/env python3
"""
X-Analyst - Production AI Agent with Masumi Integration

A sophisticated analysis agent powered by X's Phoenix recommendation system:
- Sentiment analysis (positive/negative/neutral/mixed)
- Text summarization (extractive)
- Statistical analysis
- Keyword extraction with relevance scoring
- **Content Recommendations** (Phoenix Grok-based model)
- Multi-language support preparation

This agent uses Masumi for automated payment verification on Cardano blockchain.
No manual blockchain integration needed - Masumi handles everything!
"""
import logging
from datetime import datetime
import json
from typing import Dict, Any, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)

# Optional: Import Phoenix model service
try:
    from model_service import get_model_service
    PHOENIX_AVAILABLE = True
except ImportError:
    PHOENIX_AVAILABLE = False
    logger.warning("Phoenix model service not available - recommendations disabled")

# Configuration
MAX_TEXT_LENGTH = 100000  # Maximum text length to process
MIN_TEXT_LENGTH = 10      # Minimum text length required
DEFAULT_SUMMARY_SENTENCES = 3
DEFAULT_TOP_KEYWORDS = 10

async def process_job(identifier_from_purchaser: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    X-Analyst: Production-ready text analysis agent

    Payment verification is handled automatically by Masumi before this function executes.
    You only implement the business logic - Masumi handles all blockchain complexity!

    Supported Analysis Types:
    - sentiment: Detect positive/negative/neutral/mixed sentiment
    - summary: Generate extractive text summary
    - stats: Calculate comprehensive text statistics
    - keywords: Extract relevant keywords with frequency
    - recommendations: Phoenix-powered content recommendations (ML-based)
    - general: Combined analysis (sentiment + stats + keywords)

    Args:
        identifier_from_purchaser: 26-character hex identifier from buyer's wallet
        input_data: {
            "text": str,                           # Required: Text to analyze
            "analysis_type": str,                  # Optional: Type of analysis (default: "general")
            "max_keywords": int,                   # Optional: Max keywords to extract (default: 10)
            "summary_sentences": int               # Optional: Summary length (default: 3)
        }

    Returns:
        {
            "result": {...},                       # Analysis results
            "metadata": {...},                     # Processing metadata
            "status": "completed" | "failed"
        }

    Note: Masumi automatically:
    - Verifies payment on Cardano blockchain
    - Manages job lifecycle
    - Handles deadline enforcement
    - Provides audit trail
    """
    start_time = datetime.utcnow()

    try:
        # Extract and validate inputs
        text = input_data.get("text", "")

        # Handle analysis_type - can be string value or array index from UI
        analysis_type_raw = input_data.get("analysis_type", "general")
        valid_types = ["sentiment", "summary", "stats", "keywords", "recommendations", "general"]

        logger.debug(f"Raw analysis_type value: {repr(analysis_type_raw)} (type: {type(analysis_type_raw).__name__})")

        # If it's a number or numeric string (array index from option type), convert to value
        if isinstance(analysis_type_raw, int):
            # It's an index
            analysis_type = valid_types[analysis_type_raw] if 0 <= analysis_type_raw < len(valid_types) else "general"
        elif isinstance(analysis_type_raw, str) and analysis_type_raw.isdigit():
            # It's a numeric string
            idx = int(analysis_type_raw)
            analysis_type = valid_types[idx] if 0 <= idx < len(valid_types) else "general"
        elif isinstance(analysis_type_raw, str) and analysis_type_raw.startswith('[') and analysis_type_raw.endswith(']'):
            # It's array notation like "[0]" - extract the index
            try:
                idx = int(analysis_type_raw.strip('[]'))
                analysis_type = valid_types[idx] if 0 <= idx < len(valid_types) else "general"
            except (ValueError, IndexError):
                analysis_type = "general"
        else:
            # It's the actual string value
            analysis_type = analysis_type_raw if analysis_type_raw in valid_types else "general"

        logger.info(f"Converted analysis_type to: {analysis_type}")

        max_keywords = input_data.get("max_keywords", DEFAULT_TOP_KEYWORDS)
        summary_sentences = input_data.get("summary_sentences", DEFAULT_SUMMARY_SENTENCES)

        # Parse JSON strings for recommendations (they come as text fields but need to be lists)
        if analysis_type == "recommendations":
            user_history_str = input_data.get("user_history")
            candidates_str = input_data.get("candidates")
            
            # Parse JSON strings if they're strings
            if isinstance(user_history_str, str):
                try:
                    input_data["user_history"] = json.loads(user_history_str)
                except json.JSONDecodeError:
                    return {
                        "error": "Invalid JSON in 'user_history' field",
                        "status": "failed",
                        "purchaser": identifier_from_purchaser
                    }
            
            if isinstance(candidates_str, str):
                try:
                    input_data["candidates"] = json.loads(candidates_str)
                except json.JSONDecodeError:
                    return {
                        "error": "Invalid JSON in 'candidates' field",
                        "status": "failed",
                        "purchaser": identifier_from_purchaser
                    }

        logger.info(f"Processing {analysis_type} analysis for purchaser: {identifier_from_purchaser[:8]}...")
        logger.info(f"Text length: {len(text)} characters")

        # Input validation
        validation_error = validate_input(input_data, analysis_type, max_keywords, summary_sentences)
        if validation_error:
            return {
                "error": validation_error,
                "status": "failed",
                "purchaser": identifier_from_purchaser
            }

        # Perform analysis based on type
        result = {}

        if analysis_type == "sentiment":
            result = analyze_sentiment(text)
        elif analysis_type == "summary":
            result = summarize_text(text, max_sentences=summary_sentences)
        elif analysis_type == "stats":
            result = calculate_statistics(text)
        elif analysis_type == "keywords":
            result = extract_keywords(text, top_n=max_keywords)
        elif analysis_type == "recommendations":
            # Phoenix-powered recommendations
            result = generate_recommendations(input_data, max_keywords)
        else:
            # General analysis combines multiple insights
            result = {
                "sentiment": analyze_sentiment(text),
                "stats": calculate_statistics(text),
                "keywords": extract_keywords(text, top_n=min(5, max_keywords))
            }

        logger.info(f"Analysis completed successfully for {identifier_from_purchaser[:8]}...")

        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        # Return comprehensive result
        return {
            "result": result,
            "metadata": {
                "purchaser": identifier_from_purchaser,
                "analysis_type": analysis_type,
                "processing_time_seconds": processing_time,
                "timestamp": end_time.isoformat(),
                "text_length": len(text)
            },
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Error in process_job: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "status": "failed",
            "purchaser": identifier_from_purchaser
        }


def validate_input(
    input_data: Dict[str, Any],
    analysis_type: str,
    max_keywords: int,
    summary_sentences: int
) -> Optional[str]:
    """
    Validate input parameters based on analysis type

    Args:
        input_data: Full input data dictionary
        analysis_type: Type of analysis requested (already processed from raw value)
        max_keywords: Maximum number of keywords
        summary_sentences: Number of summary sentences

    Returns:
        Error message if validation fails, None if valid
    """
    # Validate analysis type (note: analysis_type is already processed in process_job)
    # This validation is redundant but kept for safety
    valid_types = ["sentiment", "summary", "stats", "keywords", "recommendations", "general"]
    if analysis_type not in valid_types:
        return f"Invalid analysis_type '{analysis_type}'. Must be one of: {', '.join(valid_types)}"

    # Validate based on analysis type
    if analysis_type == "recommendations":
        # Recommendations require user_history and candidates, NOT text
        user_history = input_data.get("user_history")
        candidates = input_data.get("candidates")

        if not user_history:
            return "Missing 'user_history' field - required for recommendations"

        if not candidates:
            return "Missing 'candidates' field - required for recommendations"

        if not isinstance(user_history, list) or not isinstance(candidates, list):
            return "'user_history' and 'candidates' must be arrays"

        if len(candidates) > 1000:
            return "Too many candidates - maximum 1000 allowed"

    else:
        # All other analysis types require text
        text = input_data.get("text", "")

        if not text or not isinstance(text, str):
            return "Missing or invalid 'text' field - must be a non-empty string"

        if len(text) < MIN_TEXT_LENGTH:
            return f"Text too short - minimum {MIN_TEXT_LENGTH} characters required"

        if len(text) > MAX_TEXT_LENGTH:
            return f"Text too long - maximum {MAX_TEXT_LENGTH} characters allowed"

    # Validate numeric parameters
    if not isinstance(max_keywords, int) or max_keywords < 1 or max_keywords > 100:
        return "max_keywords must be an integer between 1 and 100"

    if not isinstance(summary_sentences, int) or summary_sentences < 1 or summary_sentences > 20:
        return "summary_sentences must be an integer between 1 and 20"

    return None


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of text using keyword-based approach

    Production alternatives:
    - transformers: Use BERT, RoBERTa, or DistilBERT for sentiment
    - TextBlob/VADER: Simple rule-based sentiment
    - OpenAI/Anthropic: LLM-based sentiment with reasoning
    - Custom fine-tuned models: Domain-specific sentiment

    Args:
        text: Input text to analyze

    Returns:
        Sentiment analysis with confidence score and insights
    """
    text_lower = text.lower()

    # Extended sentiment lexicon
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'love', 'best', 'perfect', 'happy', 'awesome', 'brilliant',
        'superb', 'outstanding', 'exceptional', 'impressive', 'beautiful',
        'delightful', 'fabulous', 'incredible', 'magnificent', 'marvelous',
        'phenomenal', 'splendid', 'terrific', 'positive', 'success'
    ]
    negative_words = [
        'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'poor',
        'disappointing', 'sad', 'angry', 'ugly', 'dreadful', 'pathetic',
        'disgusting', 'abysmal', 'atrocious', 'inferior', 'nasty',
        'offensive', 'repulsive', 'useless', 'worthless', 'negative',
        'failure', 'disaster', 'frustrating', 'annoying'
    ]

    # Count with word boundary awareness
    positive_count = sum(1 for word in positive_words if re.search(r'\b' + word + r'\b', text_lower))
    negative_count = sum(1 for word in negative_words if re.search(r'\b' + word + r'\b', text_lower))

    total_sentiment_words = positive_count + negative_count

    if total_sentiment_words == 0:
        sentiment = "neutral"
        confidence = 0.5
    elif positive_count > negative_count:
        sentiment = "positive"
        confidence = min(0.95, 0.6 + (positive_count / max(total_sentiment_words, 1)) * 0.35)
    elif negative_count > positive_count:
        sentiment = "negative"
        confidence = min(0.95, 0.6 + (negative_count / max(total_sentiment_words, 1)) * 0.35)
    else:
        sentiment = "mixed"
        confidence = 0.5

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "positive_indicators": positive_count,
        "negative_indicators": negative_count,
        "insights": generate_sentiment_insights(sentiment, positive_count, negative_count)
    }


def summarize_text(text: str, max_sentences: int = 3) -> Dict[str, Any]:
    """
    Generate text summary

    In production, use:
    - Hugging Face summarization models
    - OpenAI API
    - Custom transformer models
    """
    # Simple extractive summarization (replace with real model)
    sentences = [s.strip() for s in text.split('.') if s.strip()]

    if len(sentences) <= max_sentences:
        summary = text
        reduction = 0
    else:
        # Take first, middle, and last sentences (simple heuristic)
        key_indices = [0, len(sentences) // 2, len(sentences) - 1]
        summary_sentences = [sentences[i] for i in key_indices if i < len(sentences)]
        summary = '. '.join(summary_sentences) + '.'
        reduction = round((1 - len(summary) / len(text)) * 100, 1)

    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
        "reduction_percent": reduction,
        "total_sentences": len(sentences),
        "summary_sentences": min(max_sentences, len(sentences))
    }


def calculate_statistics(text: str) -> Dict[str, Any]:
    """
    Calculate text statistics
    """
    words = text.split()
    sentences = [s.strip() for s in text.split('.') if s.strip()]

    # Calculate averages
    avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
    avg_sentence_length = len(words) / max(len(sentences), 1)

    # Character analysis
    char_count = len(text)
    alpha_count = sum(1 for c in text if c.isalpha())
    digit_count = sum(1 for c in text if c.isdigit())
    space_count = sum(1 for c in text if c.isspace())

    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "character_count": char_count,
        "average_word_length": round(avg_word_length, 2),
        "average_sentence_length": round(avg_sentence_length, 2),
        "alphabetic_characters": alpha_count,
        "numeric_characters": digit_count,
        "whitespace_characters": space_count,
        "unique_words": len(set(word.lower() for word in words)),
        "lexical_diversity": round(len(set(word.lower() for word in words)) / max(len(words), 1), 2)
    }


def extract_keywords(text: str, top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Extract keywords from text

    In production, use:
    - spaCy for NER and keyword extraction
    - RAKE algorithm
    - TF-IDF scoring
    - BERT-based keyword extraction
    """
    # Simple frequency-based extraction (replace with real NLP)
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'as', 'by', 'with', 'from', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }

    # Count word frequencies
    words = [word.lower().strip('.,!?;:()[]{}') for word in text.split()]
    word_freq = {}

    for word in words:
        if len(word) > 3 and word not in stop_words and word.isalpha():
            word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and get top N
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    return [
        {
            "keyword": word,
            "frequency": freq,
            "relevance": round(freq / max(len(words), 1), 3)
        }
        for word, freq in sorted_keywords[:top_n]
    ]


def generate_sentiment_insights(sentiment: str, positive: int, negative: int) -> List[str]:
    """
    Generate human-readable insights from sentiment analysis
    """
    insights = []

    if sentiment == "positive":
        insights.append(f"Strong positive sentiment detected with {positive} positive indicators")
        if negative > 0:
            insights.append(f"Minor negative elements present ({negative} indicators)")
        else:
            insights.append("No negative indicators found")
    elif sentiment == "negative":
        insights.append(f"Strong negative sentiment detected with {negative} negative indicators")
        if positive > 0:
            insights.append(f"Some positive elements present ({positive} indicators)")
        else:
            insights.append("No positive indicators found")
    elif sentiment == "mixed":
        insights.append(f"Mixed sentiment with balanced positive ({positive}) and negative ({negative}) indicators")
    else:
        insights.append("Neutral sentiment - no strong emotional indicators detected")

    return insights


def generate_recommendations(input_data: Dict[str, Any], top_k: int = 10) -> Dict[str, Any]:
    """
    Generate content recommendations using Phoenix Grok-based model

    This function uses the Phoenix recommendation system (X's For You feed algorithm)
    to predict engagement and rank content candidates.

    Args:
        input_data: {
            "user_history": [{"post_id": str, "action": str, "timestamp": int}],
            "candidates": [{"post_id": str, "text": str, "author_id": str}],
            "top_k": int (optional, defaults to 10)
        }
        top_k: Number of recommendations to return

    Returns:
        {
            "recommendations": [
                {
                    "post_id": str,
                    "rank": int,
                    "score": float,
                    "predictions": {
                        "like": float,
                        "repost": float,
                        "reply": float,
                        ...
                    }
                }
            ],
            "model_info": {
                "model_type": str,
                "using_mock": bool
            }
        }
    """
    if not PHOENIX_AVAILABLE:
        return {
            "error": "Phoenix model service not available",
            "message": "Install JAX and Haiku dependencies to enable recommendations",
            "status": "unavailable"
        }

    try:
        # Extract parameters
        user_history = input_data.get("user_history", [])
        candidates = input_data.get("candidates", [])
        requested_top_k = input_data.get("top_k", top_k)

        # Validate inputs
        if not user_history:
            return {
                "error": "user_history is required for recommendations",
                "status": "failed"
            }

        if not candidates:
            return {
                "error": "candidates list is required for recommendations",
                "status": "failed"
            }

        if len(candidates) > 1000:
            return {
                "error": "Too many candidates - maximum 1000 allowed",
                "status": "failed"
            }

        # Get model service
        model_service = get_model_service()

        # Generate recommendations
        recommendations = model_service.rank_candidates(
            user_history=user_history,
            candidates=candidates,
            top_k=requested_top_k
        )

        return {
            "recommendations": recommendations,
            "model_info": {
                "model_type": "Phoenix Grok-based Transformer",
                "using_mock": model_service.use_mock,
                "total_candidates": len(candidates),
                "returned_count": len(recommendations)
            },
            "insights": [
                f"Ranked {len(candidates)} candidates based on user engagement history",
                f"Top recommendation has score: {recommendations[0]['score']:.3f}" if recommendations else "No recommendations generated"
            ]
        }

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        return {
            "error": str(e),
            "status": "failed"
        }


# Example usage for testing
if __name__ == "__main__":
    import asyncio

    async def test():
        # Test sentiment analysis
        test_input = {
            "text": "This product is absolutely amazing! I love it. Best purchase ever. However, the shipping was a bit slow.",
            "analysis_type": "sentiment"
        }

        result = await process_job("test_purchaser_123456789012", test_input)
        print(json.dumps(result, indent=2))

        # Test summary
        test_input2 = {
            "text": "Artificial intelligence is transforming industries. Machine learning enables computers to learn from data. Deep learning uses neural networks for complex tasks. Natural language processing helps computers understand human language. Computer vision allows machines to interpret images. These technologies are reshaping our world.",
            "analysis_type": "summary"
        }

        result2 = await process_job("test_purchaser_123456789012", test_input2)
        print(json.dumps(result2, indent=2))

    asyncio.run(test())
    