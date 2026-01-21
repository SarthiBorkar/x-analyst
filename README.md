# X-Analyst

AI agent for text analysis and content recommendations, powered by Masumi payment network on Cardano blockchain.

## Features

- **Text Analysis**: Sentiment analysis, summarization, statistics, keyword extraction
- **Phoenix Recommendations**: ML-powered content ranking using X's Grok-based transformer
- **Masumi Integration**: Automated blockchain payment verification

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Masumi credentials

# Run agent
python main.py
```

## Test Locally

```bash
python main.py --standalone
```

## Deployment

Deploy to Railway:
```bash
railway init
railway up
```

Register on [Masumi Network](https://admin.masumi.network) and update your `.env` with credentials.

## Tech Stack

- **Masumi SDK** - Payment processing
- **JAX + Haiku** - ML inference
- **Phoenix Model** - Content recommendations (Grok-based transformer)
- **Cardano** - Blockchain payments

---

**Built with Masumi Network**
