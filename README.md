# DataWorks Task Automation API

An automation agent that processes various data operations tasks using LLMs. Built for the DataWorks Solutions operations team to handle routine tasks through a simple API interface.

## Prerequisites

- Docker/Podman installed and running
- AI Proxy token (set as AIPROXY_TOKEN environment variable)
- At least 2GB of free disk space
- Internet connection (for pulling Docker image and LLM API calls)

## Quick Start

```bash
# 1. Create a data directory for persistent storage
mkdir -p data

# 2. Set your AI Proxy token
export AIPROXY_TOKEN=your_token_here

# 3. Pull and run the container (using Docker or Podman)
# Using Docker:
docker pull sokh1125/tdsproject
docker run -p 8000:8000 -v $(pwd)/data:/data -e AIPROXY_TOKEN=$AIPROXY_TOKEN sokh1125/tdsproject

# Using Podman:
podman pull sokh1125/tdsproject
podman run -p 8000:8000 -v $(pwd)/data:/data -e AIPROXY_TOKEN=$AIPROXY_TOKEN sokh1125/tdsproject
```

The API will be available at `http://localhost:8000`

## Verifying Installation

Test if the API is working:

```bash
# Test the server is running
curl http://localhost:8000/

# Test task execution (A1)
curl -X POST "http://localhost:8000/run?task=Install uv and run the script with example@email.com"

# Test file reading
curl "http://localhost:8000/read?path=/data/format.md"
```

## Features

### Phase A: Operations Tasks
- File formatting with Prettier
- Date processing and analysis
- JSON data sorting and manipulation
- Log file processing
- Document indexing
- Email data extraction
- Credit card number extraction from images
- Text similarity analysis using embeddings
- Database querying

### Phase B: Business Tasks
- Secure data access (restricted to /data directory)
- Data preservation (no deletion operations)
- API data fetching
- Git operations
- SQL query execution
- Web scraping
- Image processing
- Audio transcription
- Markdown to HTML conversion
- CSV/JSON API endpoints

## Detailed Setup

### Using Container Runtime (Docker/Podman Recommended)
```bash
# Using Docker
docker pull sokh1125/tdsproject
docker run -p 8000:8000 \
  -v $(pwd)/data:/data \
  -e AIPROXY_TOKEN=$AIPROXY_TOKEN \
  sokh1125/tdsproject

# Using Podman
podman pull sokh1125/tdsproject
podman run -p 8000:8000 \
  -v $(pwd)/data:/data \
  -e AIPROXY_TOKEN=$AIPROXY_TOKEN \
  sokh1125/tdsproject

# For Windows PowerShell, use:
# Docker:
docker run -p 8000:8000 `
  -v ${PWD}/data:/data `
  -e AIPROXY_TOKEN=$env:AIPROXY_TOKEN `
  sokh1125/tdsproject

# Podman:
podman run -p 8000:8000 `
  -v ${PWD}/data:/data `
  -e AIPROXY_TOKEN=$env:AIPROXY_TOKEN `
  sokh1125/tdsproject
```

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export AIPROXY_TOKEN=your_token_here  # On Windows: set AIPROXY_TOKEN=your_token_here

# Create data directory
mkdir -p data

# Run the server
uvicorn app:app --host 0.0.0.0 --port 8000
```

## API Usage

### POST /run
Execute a task described in plain English.

```bash
# Example tasks:
curl -X POST "http://localhost:8000/run?task=Format the contents of /data/format.md using prettier@3.4.2"
curl -X POST "http://localhost:8000/run?task=Count Wednesdays in dates.txt"
curl -X POST "http://localhost:8000/run?task=Sort contacts by last name and first name"
```

Response codes:
- 200: Task completed successfully
- 400: Invalid task request
- 500: Internal server error

### GET /read
Retrieve the contents of a file.

```bash
curl "http://localhost:8000/read?path=/data/format.md"
```

Response codes:
- 200: File contents returned successfully
- 404: File not found
- 500: Internal server error

## Troubleshooting

1. **Port already in use**
```bash
# Stop any container using port 8000
docker stop $(docker ps | grep 8000 | awk '{print $1}')
```

2. **Permission denied for /data directory**
```bash
# Fix permissions
chmod 777 data
```

3. **Docker container exits immediately**
```bash
# Check logs
docker logs $(docker ps -a | grep sokh1125/tdsproject | awk '{print $1}')
```

4. **API returns 500 error**
- Verify AIPROXY_TOKEN is set correctly
- Check if the /data directory exists and is writable
- Ensure you have internet connectivity for LLM API calls

## Environment Variables

- `AIPROXY_TOKEN`: Your AI Proxy token for LLM access (Required)
- `PORT`: Port to run the server on (Optional, default: 8000)

## Important Notes

1. **AI Proxy Token Usage**
   - Use the AIPROXY_TOKEN environment variable
   - DO NOT commit your AI Proxy token to the repository
   - Token has a $1 limit; contact TDS team if you need more
   - Uses GPT-4o-Mini model through AI Proxy

2. **Performance Requirements**
   - Each API call (/run and /read) must complete within 20 seconds
   - Keep prompts short and concise for optimal performance

3. **Project Submission**
   - GitHub Repository: https://github.com/sokh1125/tdsproject1
   - Docker Image: sokh1125/tdsproject
   - Submit these URLs in the provided Google Form

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 