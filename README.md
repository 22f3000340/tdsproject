# DataWorks Task Automation API

An automation agent that processes various data operations tasks using LLMs. Built for the DataWorks Solutions operations team to handle routine tasks through a simple API interface.

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

## Installation

### Using Docker (Recommended)
```bash
# Pull the image
docker pull sokh1125/tdsproject

# Run the container
docker run -p 8000:8000 -v $(pwd)/data:/data -e AIPROXY_TOKEN=your_token_here sokh1125/tdsproject
```

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/your-repo-name.git

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /run
Execute a task described in plain English.

```bash
curl -X POST "http://localhost:8000/run?task=Format the contents of /data/format.md using prettier@3.4.2"
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

## Environment Variables

- `AIPROXY_TOKEN`: Your AI Proxy token for LLM access

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 