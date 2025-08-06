# TSA Item Checker Backend

A Python FastAPI backend service that determines whether items can be carried in carry-on or checked baggage through TSA security using OpenRouter LLM calls.

## Features

- **FastAPI Backend**: Modern, fast Python web framework
- **OpenRouter Integration**: Uses Claude 3.5 Sonnet via OpenRouter for intelligent TSA rule analysis
- **RESTful API**: Simple JSON API for checking TSA compliance
- **Render.com Ready**: Configured for easy deployment on Render
- **CORS Enabled**: Ready for frontend integration
- **Comprehensive Response**: Returns detailed information about restrictions and notes

## API Endpoints

### `GET /`
Health check and API information

### `GET /health`
Service health check endpoint

### `POST /check-item`
Check if an item can be carried through TSA security

**Request Body:**
```json
{
  "item": "laptop",
  "description": "15-inch MacBook Pro" // optional
}
```

**Response:**
```json
{
  "item": "laptop",
  "carry_on_allowed": true,
  "checked_baggage_allowed": true,
  "description": "Laptops are allowed in both carry-on and checked baggage...",
  "restrictions": "Must be removed from bag during security screening",
  "additional_notes": "Battery should be charged for potential security checks"
}
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- OpenRouter API account

### Local Development

1. **Clone and setup the project:**
   ```bash
   git clone <your-repo-url>
   cd tsa-item-checker
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_actual_api_key_here
   PORT=8000
   ```

4. **Get OpenRouter API Key:**
   - Sign up at [OpenRouter](https://openrouter.ai/)
   - Get your API key from the dashboard
   - Add credits to your account for API usage

5. **Run the server:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Test the API:**
   - Visit `http://localhost:8000` for basic info
   - Visit `http://localhost:8000/docs` for interactive API documentation
   - Visit `http://localhost:8000/health` for health check

### Testing the API

You can test the API using curl:

```bash
# Test basic item
curl -X POST "http://localhost:8000/check-item" \
     -H "Content-Type: application/json" \
     -d '{"item": "toothpaste"}'

# Test with description
curl -X POST "http://localhost:8000/check-item" \
     -H "Content-Type: application/json" \
     -d '{"item": "battery pack", "description": "20000mAh portable charger"}'
```

## Deployment on Render.com

### Quick Deploy

1. **Connect your repository to Render:**
   - Sign up at [Render.com](https://render.com)
   - Connect your GitHub repository
   - Choose "Web Service"

2. **Configure the deployment:**
   - Render will automatically detect the `render.yaml` configuration
   - Set the environment variable:
     - `OPENROUTER_API_KEY`: Your OpenRouter API key

3. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app

### Manual Configuration (if not using render.yaml)

If you prefer manual configuration:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `OPENROUTER_API_KEY`: Your OpenRouter API key

## Project Structure

```
tsa-item-checker/
├── main.py              # FastAPI application and API endpoints
├── requirements.txt     # Python dependencies
├── render.yaml         # Render deployment configuration
├── env_example.txt     # Environment variables template
└── README.md           # This file
```

## Dependencies

- **FastAPI**: Web framework for building APIs
- **uvicorn**: ASGI server for FastAPI
- **pydantic**: Data validation and serialization
- **httpx**: Async HTTP client for OpenRouter API calls
- **python-dotenv**: Environment variable management
- **openai**: OpenAI client library (compatible with OpenRouter)

## Usage Examples

### Example 1: Check Liquid Item
```python
import requests

response = requests.post("http://localhost:8000/check-item", 
                        json={"item": "shampoo", "description": "300ml bottle"})
print(response.json())
```

### Example 2: Check Electronic Device
```python
import requests

response = requests.post("http://localhost:8000/check-item", 
                        json={"item": "drone", "description": "DJI Mini 2"})
print(response.json())
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Missing or invalid item name
- **500 Internal Server Error**: OpenRouter API issues or unexpected errors
- **504 Gateway Timeout**: Request timeout to LLM service

## Security & Privacy

- No sensitive data is stored
- All requests to OpenRouter are made over HTTPS
- API key is securely stored as an environment variable
- CORS is enabled for frontend integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this project for your own applications!

## Support

For issues or questions:
1. Check the [API documentation](http://localhost:8000/docs) when running locally
2. Verify your OpenRouter API key is valid and has credits
3. Check Render logs if deployment issues occur
4. Ensure environment variables are properly set

## Cost Considerations

- OpenRouter charges per API call based on the model used
- Claude 3.5 Sonnet is used for high-quality responses
- Monitor your OpenRouter usage to control costs
- Consider implementing caching for frequently asked items in production