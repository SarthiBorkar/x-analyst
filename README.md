# X-Analyst AI Agent

**Advanced data analysis agent powered by Masumi Network on Cardano blockchain**

X-Analyst is an autonomous AI agent that provides sophisticated text analysis services including sentiment analysis, summarization, statistical analysis, and keyword extraction. Built on the Masumi decentralized protocol, it enables trustless payments and verifiable execution on Cardano blockchain.

---

## Features

### Text Analysis
- **Sentiment Analysis**: Detect positive, negative, neutral, or mixed sentiment with confidence scores
- **Text Summarization**: Generate concise summaries from longer text
- **Statistical Analysis**: Calculate comprehensive text statistics (word count, lexical diversity, etc.)
- **Keyword Extraction**: Identify and rank important keywords by relevance

### Phoenix ML Recommendations (NEW!)
- **Content Ranking**: Powered by X's Grok-based transformer from the For You algorithm
- **Engagement Prediction**: Predicts likes, reposts, replies, clicks for personalized recommendations
- **Production-Ready ML**: Supports both mock mode (for testing) and real model inference
- **Scalable**: Handles up to 1000 candidates per request with sub-second latency

### Masumi Integration
- **Blockchain Payments**: Automated payment verification and processing via Cardano smart contracts
- **MIP-003 Compliant**: Implements Masumi Improvement Proposal 003 API standard
- **Dual Mode Operation**: Run standalone for testing or as API server for production
- **TxPipe Audited**: Smart contracts verified by leading Cardano security firm

---

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/sarthiborkar/Build/x-algo/x-analyst
pip install -r requirements.txt
```

### 2. Test Locally (No Blockchain)

```bash
# Run in standalone mode - no payment required
python main.py --standalone

# When prompted, enter test input:
{"text": "This is amazing!", "analysis_type": "sentiment"}
```

### 3. Configure for Production

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials (see Configuration section)
nano .env
```

### 4. Run as API Server

```bash
# Start agent server
python main.py

# Visit http://localhost:8080/docs for Swagger UI
```

---

## What Makes This Agent Special

### Autonomous Payment Processing

X-Analyst leverages Masumi's smart contract architecture to handle payments automatically:

1. **Buyers** lock ADA in audited smart contracts (TxPipe verified)
2. **Agent** verifies payment on Cardano blockchain before processing
3. **Execution** occurs only after cryptographic payment confirmation
4. **Settlement** releases funds automatically upon job completion
5. **Refunds** are automatic if deadlines are missed

**You never handle payments manually** - the Masumi pip package manages everything.

### Blockchain-Backed Integrity

Every job execution is recorded on Cardano blockchain:
- **Input hashing** (MIP-004 standard) ensures data integrity
- **Output hashing** provides cryptographic proof of results
- **Decision logging** creates immutable audit trail
- **Dispute resolution** via on-chain evidence

### Decentralized Discovery

Your agent is discoverable through:
- **Masumi Registry Service**: On-chain agent directory
- **Sokosumi Marketplace**: User-friendly agent discovery platform
- **Direct API**: Programmable agent-to-agent (A2A) transactions

---

## Configuration

### Required Credentials

Create `.env` file with these values:

```env
# Agent Identity (get after registration)
AGENT_IDENTIFIER=xanalyst_your_id_here

# Payment Service Credentials
SELLER_VKEY=your_wallet_vkey_from_payment_service
PAYMENT_API_KEY=your_payment_service_api_key

# Network Selection
NETWORK=Preprod  # Use 'Preprod' for testing, 'Mainnet' for production

# Payment Service URL
PAYMENT_SERVICE_URL=http://localhost:3001/api/v1
```

### Where to Get Credentials

**SELLER_VKEY and PAYMENT_API_KEY:**
1. Run Masumi Payment Service locally (see DEVELOPMENT_GUIDE.md)
2. Create wallet via Payment Service API
3. Extract `vkey` from response
4. Generate secure API key: `openssl rand -hex 32`

**AGENT_IDENTIFIER:**
1. Register agent at https://admin.masumi.network
2. Or use Registry Service API (POST /registry)
3. Receive unique identifier after registration

**See DEVELOPMENT_GUIDE.md for detailed setup instructions**

---

## Project Structure

```
x-analyst/
├── agent.py                 # Core agent logic (process_job function)
├── main.py                  # Entry point (uses masumi.run())
├── agent_example.py         # Enhanced example implementation
├── test_buyer.py            # Test script to simulate purchases
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .env                     # Your actual credentials (gitignored)
├── README.md                # This file
└── DEVELOPMENT_GUIDE.md     # Complete development workflow guide
```

---

## How It Works

### Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Buyer     │────────>│  X-Analyst   │────────>│  Cardano    │
│  (Customer) │  Request│   (Agent)    │  Verify │ Blockchain  │
└─────────────┘         └──────────────┘         └─────────────┘
       │                        │                        │
       │ 1. Lock ADA           │                        │
       │────────────────────────────────────────────────>│
       │                        │                        │
       │ 2. Start Job          │                        │
       │───────────────────────>│                        │
       │                        │ 3. Verify Payment      │
       │                        │<───────────────────────│
       │                        │                        │
       │                        │ 4. Process Job         │
       │                        │ (sentiment analysis)   │
       │                        │                        │
       │ 5. Return Results     │                        │
       │<───────────────────────│                        │
       │                        │ 6. Complete Payment    │
       │                        │───────────────────────>│
       │                        │                        │
       │                        │ 7. Release Funds       │
       │                        │<───────────────────────│
```

### Payment Flow Time Controls

Every payment request includes deadlines:
- **pay_by_time**: Buyer must pay by this timestamp
- **submit_result_time**: Agent must complete job by this timestamp
- **unlock_time**: Earliest time funds can be unlocked
- **external_dispute_unlock_time**: Dispute resolution deadline

**Smart contracts enforce these automatically** - no manual intervention required.

---

## API Endpoints (MIP-003 Compliant)

When running in API mode (`python main.py`), X-Analyst exposes these endpoints:

### GET /input_schema
Returns JSON schema describing accepted inputs.

**Response:**
```json
{
  "input_data": [
    {
      "id": "text",
      "type": "string",
      "name": "Text Input",
      "data": {"description": "Text to analyze"},
      "validations": [{"validation": "required", "value": "true"}]
    }
  ]
}
```

### GET /availability
Checks if agent is ready to process jobs.

**Response:**
```json
{"status": "available"}
```

### POST /start_job
Starts new job with payment verification.

**Request:**
```json
{
  "identifier_from_purchaser": "buyer_26char_hex_id",
  "input_data": {
    "text": "Analyze this text",
    "analysis_type": "sentiment"
  },
  "blockchain_identifier": "payment_blockchain_id"
}
```

**Response:**
```json
{
  "job_id": "unique_job_id",
  "status": "processing"
}
```

### GET /status?job_id=xyz
Check job status and retrieve results.

**Response:**
```json
{
  "status": "completed",
  "result": {
    "sentiment": "positive",
    "confidence": 0.85,
    "insights": ["Strong positive indicators"]
  }
}
```

### POST /provide_input
Provide additional input to running job (for multi-step agents).

---

## Usage Examples

### Example 1: Sentiment Analysis

```python
from masumi import Config, Purchase
import asyncio

async def analyze_sentiment():
    config = Config(
        payment_service_url="http://localhost:3001/api/v1",
        payment_api_key="your_api_key"
    )

    purchase = Purchase(
        agent_identifier="xanalyst_your_id",
        config=config
    )

    result = await purchase.start_job_with_payment(
        input_data={
            "text": "This product is absolutely fantastic!",
            "analysis_type": "sentiment"
        },
        payment_amount=10000000,  # 10 ADA
        payment_unit="lovelace"
    )

    print(result)

asyncio.run(analyze_sentiment())
```

### Example 2: Text Summarization

```python
result = await purchase.start_job_with_payment(
    input_data={
        "text": "Long article text here...",
        "analysis_type": "summary"
    },
    payment_amount=5000000  # 5 ADA
)
```

### Example 3: Keyword Extraction

```python
result = await purchase.start_job_with_payment(
    input_data={
        "text": "Blockchain enables decentralized applications...",
        "analysis_type": "keywords"
    },
    payment_amount=5000000
)
```

---

## Testing

### Unit Testing (No Blockchain)

```bash
# Test agent logic standalone
python main.py --standalone

# Run example implementation
python agent_example.py
```

### Integration Testing (With Payments)

```bash
# 1. Start Payment Service
cd masumi-payment-service
npm start

# 2. Start agent in API mode
cd /Users/sarthiborkar/Build/x-algo/x-analyst
python main.py

# 3. Run test buyer script
python test_buyer.py
```

### Get Test Tokens

**Cardano Faucet:**
https://docs.cardano.org/cardano-testnets/tools/faucet

**Masumi Dispenser:**
https://dispenser.masumi.network

---

## Deployment

### Option 1: Kodosumi Runtime (Recommended)

```bash
# Install Kodosumi CLI
pip install kodosumi

# Login
koco login

# Deploy
koco deploy --name x-analyst --port 8080

# Get deployment URL
koco info x-analyst
```

### Option 2: Docker Self-Hosted

```bash
# Build image
docker build -t x-analyst .

# Run container
docker run -p 8080:8080 --env-file .env x-analyst
```

### Option 3: Cloud Platforms

Deploy to AWS, GCP, Azure, or Heroku:
1. Set environment variables in platform dashboard
2. Expose port 8080
3. Ensure PostgreSQL database access for Payment Service
4. Configure HTTPS for production

---

## Production Checklist

Before going to Mainnet:

- [ ] Thoroughly tested on Preprod network
- [ ] Payment Service running with Mainnet configuration
- [ ] Agent registered with Mainnet credentials
- [ ] Environment variables use Mainnet values
- [ ] HTTPS enabled for production deployment
- [ ] Monitoring configured (logs, metrics, alerts)
- [ ] Error handling tested (payment failures, timeouts)
- [ ] Agent listed on Sokosumi marketplace
- [ ] Documentation updated with pricing and capabilities

---

## Troubleshooting

### "Payment not verified"
- Check buyer wallet has sufficient ADA/USDC
- Verify `blockchain_identifier` is correct
- Confirm Blockfrost API key matches network (Preprod/Mainnet)
- Review Payment Service logs

### "Agent not found"
- Wait 2-3 minutes after registration for registry sync
- Verify `AGENT_IDENTIFIER` in .env matches registration
- Check Registry Service: `curl https://registry.masumi.network/api/v1/agents/{your_id}`

### "Job timeout"
- Increase `submit_result_time` deadline in payment request
- Optimize `process_job()` execution time
- Check agent server is running and accessible

### Database errors
- Verify PostgreSQL is running
- Check `DATABASE_URL` in Payment Service .env
- Run migrations: `npm run prisma:migrate`

---

## Extending the Agent

### Add New Analysis Types

Edit `/Users/sarthiborkar/Build/x-algo/x-analyst/agent.py`:

```python
async def process_job(identifier_from_purchaser: str, input_data: dict):
    analysis_type = input_data.get("analysis_type")

    if analysis_type == "emotion":
        # Add emotion detection
        result = detect_emotions(text)
    elif analysis_type == "entity_extraction":
        # Add named entity recognition
        result = extract_entities(text)

    return {"result": result}
```

### Integrate ML Models

```python
from transformers import pipeline

sentiment_analyzer = pipeline("sentiment-analysis")

async def process_job(identifier_from_purchaser: str, input_data: dict):
    text = input_data.get("text")
    result = sentiment_analyzer(text)
    return {"result": result}
```

### Add External API Calls

```python
import httpx

async def process_job(identifier_from_purchaser: str, input_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/analyze",
            json={"text": input_data.get("text")}
        )
    return {"result": response.json()}
```

---

## Resources

- **Complete Development Guide**: See `DEVELOPMENT_GUIDE.md`
- **Example Implementation**: See `agent_example.py`
- **Test Buyer Script**: See `test_buyer.py`

### Official Documentation

- **Masumi Docs**: https://docs.masumi.network
- **Kodosumi Docs**: https://docs.kodosumi.io
- **Sokosumi Marketplace**: https://sokosumi.com
- **Admin Dashboard**: https://admin.masumi.network
- **Network Explorer**: https://explorer.masumi.network

### Community & Support

- **Discord**: https://discord.gg/zRxq4BS6
- **GitHub**: https://github.com/masumi-network
- **Improvement Proposals**: https://github.com/masumi-network/masumi-improvement-proposals

### Blockchain Resources

- **Blockfrost API**: https://blockfrost.io (get API keys)
- **Cardano Faucet**: https://docs.cardano.org/cardano-testnets/tools/faucet
- **Masumi Dispenser**: https://dispenser.masumi.network
- **Cardano Explorer**: https://cardanoscan.io

---

## Security & Best Practices

1. **Never commit API keys**: Always use `.env` files (already in `.gitignore`)
2. **Separate Preprod/Mainnet keys**: Use different credentials for testing and production
3. **Protect wallet keys**: Never expose or commit `skey` files
4. **Test thoroughly on Preprod**: Don't rush to Mainnet
5. **Monitor logs**: Watch for suspicious activity or errors
6. **Keep packages updated**: Run `pip install --upgrade masumi`
7. **Use HTTPS in production**: Secure your API endpoints
8. **Validate inputs**: Sanitize user input to prevent injection attacks

---

## Smart Contract Audit

Masumi's payment smart contracts have been audited by **TxPipe**, a leading Cardano security firm. The audit confirms:
- No critical vulnerabilities
- Proper fund locking and release mechanisms
- Correct deadline enforcement
- Secure refund logic

**Audit report**: https://docs.masumi.network/security/audit

---

## License

MIT License - See LICENSE file for details

---

## Contributing

We welcome contributions! To contribute to X-Analyst:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## About Masumi Network

Masumi is a decentralized protocol for AI agent payments, identity, and collaboration built on Cardano blockchain. It enables:
- **Trustless payments** via smart contracts
- **On-chain identity** with blockchain-backed credentials
- **Decision logging** with cryptographic proof
- **Agent-to-Agent (A2A)** and **Human-to-Agent (H2A)** transactions

**Learn more**: https://masumi.network

---

## Contact

- **Project Maintainer**: Sarthi Borkar
- **Email**: [your-email@example.com]
- **Discord**: Join the Masumi community at https://discord.gg/zRxq4BS6

---

**Built with Masumi Network on Cardano Blockchain**
