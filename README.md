# MGraph AI Service Proxy

[![Current Release](https://img.shields.io/badge/release-v0.6.4-blue)](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Proxy/releases)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688)](https://fastapi.tiangolo.com/)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange)](https://aws.amazon.com/lambda/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![CI Pipeline - DEV](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Proxy/actions/workflows/ci-pipeline__dev.yml/badge.svg)](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Proxy/actions)

A serverless HTTP/HTTPS reverse proxy service built with FastAPI and deployable to AWS Lambda. This service provides a lightweight, type-safe proxy that can be deployed behind CloudFront for browser proxy configuration or API gateway functionality.

## 🎯 Purpose

MGraph-AI Service Proxy is a production-ready reverse proxy that:
- ✅ Forwards HTTP/HTTPS requests through AWS Lambda
- ✅ Works with browser proxy configurations (via CloudFront)
- ✅ Provides request filtering and header management
- ✅ Tracks proxy statistics and metrics
- ✅ Implements Type-Safe architecture for runtime validation
- ✅ Deploys as a serverless function with minimal cost

## 🚀 Key Features

- **Serverless Architecture**: Runs on AWS Lambda with CloudFront distribution
- **Browser Proxy Support**: Configure browsers to route through `proxy.dev.mgraph.ai`
- **Type-Safe Implementation**: Built with OSBot-Utils Type_Safe framework
- **Synchronous Processing**: Avoids FastAPI async complexity issues
- **Connection Pooling**: Thread-local session management for efficiency
- **Header Filtering**: Security-focused header manipulation
- **Statistics Tracking**: Monitor requests, errors, and timeouts

## ⚠️ Limitations

Due to AWS Lambda constraints, this proxy has the following limitations:
- **No HTTPS CONNECT tunneling** - Cannot handle true HTTPS proxy protocol
- **6MB request payload limit** - Request size Lambda restrictions
- **20MB response payload limit** - response size Lambda restrictions
- **No WebSocket support** - Lambda doesn't support persistent connections
- **Higher latency** - Cold starts and Lambda overhead

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [API Documentation](#-api-documentation)
- [Browser Configuration](#-browser-configuration)
- [Architecture](#-architecture)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Security](#-security)
- [License](#-license)

## 🎯 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/the-cyber-boardroom/MGraph-AI__Service__Proxy.git
cd MGraph-AI__Service__Proxy

# Install dependencies
pip install -r requirements-test.txt
pip install -e .

# Set environment variables
export FAST_API__AUTH__API_KEY__NAME="x-api-key"
export FAST_API__AUTH__API_KEY__VALUE="your-secret-key"

# Run locally
./scripts/run-locally.sh
# or
uvicorn mgraph_ai_service_proxy.fast_api.lambda_handler:app --reload --host 0.0.0.0 --port 10011
```

### Testing the Proxy

```bash
# Test proxy functionality with curl
curl -x http://localhost:10011 http://example.com

# Make a proxied request with authentication
curl -H "x-api-key: your-secret-key" \
     -x http://localhost:10011 \
     https://api.example.com/data
```

## 📦 Installation

### Prerequisites

- Python 3.12+
- AWS CLI (for deployment)
- AWS Account with Lambda access
- Domain in Route53 (for production proxy)

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## 📖 API Documentation

### Interactive API Documentation

Once running, access the interactive API docs at:
- Swagger UI: http://localhost:10011/docs
- ReDoc: http://localhost:10011/redoc

### Proxy Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/{path:path}` | ANY | Proxy requests to target URL |
| `/proxy/stats` | GET | Get proxy statistics |
| `/health` | GET | Service health check |
| `/info/status` | GET | Service status information |

### Making Proxy Requests

```python
import requests

# Direct proxy request (path contains full URL)
response = requests.get(
    "http://localhost:10011/http://example.com/api/data",
    headers={"x-api-key": "your-secret-key"}
)

# With custom headers
response = requests.post(
    "http://localhost:10011/https://api.example.com/users",
    headers={
        "x-api-key": "your-secret-key",
        "Content-Type": "application/json"
    },
    json={"name": "test"}
)
```

## 🌐 Browser Configuration

### Deploying for Browser Proxy Use

1. **Deploy to Lambda** (see [Deployment](#-deployment))
2. **Configure CloudFront** with your Lambda function URL as origin
3. **Setup Route53** to point `proxy.dev.mgraph.ai` to CloudFront
4. **Configure browser proxy settings**:

#### Chrome/Edge
- Settings → Advanced → System → "Open proxy settings"
- HTTP Proxy: `proxy.dev.mgraph.ai`
- HTTPS Proxy: `proxy.dev.mgraph.ai`
- Port: `443`

#### Firefox
- Settings → Network Settings → Manual proxy configuration
- HTTP/HTTPS Proxy: `proxy.dev.mgraph.ai`
- Port: `443`

## 🏗️ Architecture

### Service Components

```
mgraph_ai_service_proxy/
├── service/
│   └── proxy/
│       ├── Service__Proxy.py           # Main proxy service
│       ├── Service__Proxy__Stats.py    # Statistics tracking
│       ├── Service__Proxy__Filter.py   # Header filtering
│       └── schemas/
│           ├── Schema__Proxy__Config.py    # Configuration
│           ├── Schema__Proxy__Request.py   # Request model
│           └── Schema__Proxy__Response.py  # Response model
├── fast_api/
│   └── routes/
│       └── Routes__Proxy.py            # FastAPI endpoints
└── config.py                            # Service configuration
```

### Request Flow

```
Browser/Client → CloudFront → Lambda → Target Server
       ↑                                    ↓
       └────────── Response ←──────────────┘
```

### Type-Safe Architecture

All components use Type-Safe primitives:
- `Safe_Str` for strings (sanitized)
- `Safe_UInt` for counters (non-negative)
- `Safe_Str__Url` for URLs (validated)
- No raw primitives for security

## 🛠️ Development

### Adding Custom Filtering

```python
# In Service__Proxy__Filter.py
class Service__Proxy__Filter(Type_Safe):
    CUSTOM_HEADERS = {'X-Custom-Header'}
    
    def filter_custom_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        # Add custom filtering logic
        return {k: v for k, v in headers.items() 
                if k not in self.CUSTOM_HEADERS}
```

### Extending Statistics

```python
# In Service__Proxy__Stats.py
class Service__Proxy__Stats(Type_Safe):
    total_bytes: Safe_UInt  # Add new counter
    
    def record_bytes(self, size: int) -> None:
        self.total_bytes = Safe_UInt(self.total_bytes + size)
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mgraph_ai_service_proxy

# Run specific test category
pytest tests/unit/service/proxy/

# Run integration tests
pytest tests/integration/
```

### Test Coverage Areas

- **Type Safety**: Validates Safe type conversions
- **Header Filtering**: Request/response header manipulation
- **URL Building**: Various URL construction scenarios
- **Error Handling**: Timeouts, connection errors
- **Statistics**: Request counting and metrics

## 🚀 Deployment

### Deploy to AWS Lambda

```bash
# Package for Lambda
pip install -r requirements.txt -t package/
cp -r mgraph_ai_service_proxy package/
cd package && zip -r ../function.zip . && cd ..

# Deploy with AWS CLI
aws lambda create-function \
    --function-name mgraph-ai-proxy \
    --runtime python3.12 \
    --role arn:aws:iam::ACCOUNT:role/lambda-role \
    --handler mgraph_ai_service_proxy.fast_api.lambda_handler.run \
    --zip-file fileb://function.zip \
    --timeout 30 \
    --memory-size 512

# Create Function URL
aws lambda create-function-url-config \
    --function-name mgraph-ai-proxy \
    --auth-type NONE
```

### CloudFront Configuration

```json
{
  "Origins": [{
    "DomainName": "YOUR-FUNCTION-URL.lambda-url.region.on.aws",
    "CustomOriginConfig": {
      "OriginProtocolPolicy": "https-only"
    }
  }],
  "DefaultCacheBehavior": {
    "AllowedMethods": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
    "CachedMethods": ["GET", "HEAD"],
    "ForwardedValues": {
      "QueryString": true,
      "Headers": ["*"]
    },
    "MinTTL": 0,
    "DefaultTTL": 0,
    "MaxTTL": 0
  }
}
```

### CI/CD Pipeline

The service uses GitHub Actions for deployment:
- **dev branch**: Auto-deploy to development
- **main branch**: Auto-deploy to QA
- **Production**: Manual trigger required

## 🔒 Security

### Security Features

- **Header Filtering**: Removes sensitive proxy headers
- **Type Safety**: Runtime validation of all inputs
- **API Key Authentication**: Optional access control
- **No Raw Primitives**: Safe types prevent injection attacks

### Best Practices

1. **Rotate API keys regularly**
2. **Monitor CloudWatch logs for suspicious activity**
3. **Use CloudFront WAF rules for additional protection**
4. **Limit Lambda function permissions**
5. **Enable VPC endpoint if proxying internal resources**

## 📊 Monitoring

### CloudWatch Metrics

- Request count and latency
- Error rates (timeouts, connection errors)
- Lambda cold starts
- Memory usage

### Accessing Statistics

```bash
curl https://proxy.dev.mgraph.ai/proxy/stats \
     -H "x-api-key: your-secret-key"
```

Response:
```json
{
  "total_requests": 1234,
  "total_errors": 12,
  "total_timeouts": 3
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FAST_API__AUTH__API_KEY__NAME` | Header name for API key | No | - |
| `FAST_API__AUTH__API_KEY__VALUE` | API key value | No | - |
| `PROXY_VERIFY_SSL` | Verify SSL certificates | No | false |
| `PROXY_MAX_TIMEOUT` | Maximum request timeout | No | 25 |
| `PROXY_POOL_SIZE` | Connection pool size | No | 10 |

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Type safety via [OSBot-Utils](https://github.com/owasp-sbot/OSBot-Utils)
- Deployed on [AWS Lambda](https://aws.amazon.com/lambda/)

## 📞 Support

- 🐛 Issues: [GitHub Issues](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Proxy/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Proxy/discussions)

---

Created and maintained by [The Cyber Boardroom](https://github.com/the-cyber-boardroom) team