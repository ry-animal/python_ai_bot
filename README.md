# Python AI Bot API

A secure, serverless API for text generation using OpenAI's GPT models, deployed on Vercel.

## Features

- Direct integration with OpenAI API
- Comprehensive security measures:
  - API Key Authentication
  - JWT Authentication
  - Rate Limiting
  - Input Validation
  - CORS Support
  - Request Logging

## API Endpoints

### Text Generation

- `GET /generate-debug?prompt=<your_prompt>` - Generate text (for debugging)
- `POST /generate` - Generate text with JSON body

Example POST request:

```json
{
  "prompt": "Tell me a joke about programming"
}
```

### Authentication

- `GET /auth?user_id=<user_id>` - Generate JWT token (requires API key)
- `POST /auth` - Generate JWT token with JSON body

Example POST request:

```json
{
  "user_id": "your_user_id",
  "api_key": "your_api_key"
}
```

### System Status

- `GET /health` - Health check endpoint
- `GET /api/test` - Environment info
- `GET /api/test/openai` - Test OpenAI connectivity

## Authentication Methods

The API supports two authentication methods:

### 1. API Key Authentication

Include your API key in the request headers:

```
X-API-Key: your_api_key
```

### 2. JWT Authentication

First, obtain a JWT token using the `/auth` endpoint with your API key. Then include the token in the request headers:

```
Authorization: Bearer your_jwt_token
```

## Setting Up Security

### Environment Variables

Set these environment variables in your Vercel project:

- `OPENAI_API_KEY` - Your OpenAI API key
- `API_SECRET_KEY` - Secret key for API authentication
- `JWT_SECRET` - Secret key for JWT token signing
- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins for CORS (default: \*)

### Rate Limiting

The API has built-in rate limiting:

- 10 requests per minute per IP address (configurable)

### Input Validation

All inputs are validated:

- Maximum prompt length: 1000 characters
- Minimum prompt length: 1 character

## Deployment

The API is designed to be deployed to Vercel:

1. Fork this repository
2. Create a new Vercel project
3. Link your Vercel project to your forked repository
4. Set the required environment variables
5. Deploy!

## Development

1. Clone the repository
2. Install dependencies: `pip install -r api/requirements.txt`
3. Set environment variables
4. Run locally with Vercel CLI: `vercel dev`

## Security Best Practices

1. Use HTTPS for all requests
2. Rotate API keys and JWT secrets regularly
3. Set up proper CORS restrictions in production
4. Monitor logs for suspicious activity
5. Keep dependencies updated

## License

MIT
