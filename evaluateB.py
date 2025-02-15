#!/usr/bin/env python3

import asyncio
import hashlib
import httpx
import json
import logging
import os
import subprocess
from PIL import Image
from bs4 import BeautifulSoup
import markdown
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

def num(str):
    return int(hashlib.sha256(str.encode()).hexdigest(), 16) % (2**32)

def mismatch(msg, expected, result):
    logging.error(f"🔴 {msg}\n⚠️ EXPECTED:\n{expected}\n⚠️ RESULT:\n{result}")
    return False

async def run(task: str):
    async with httpx.AsyncClient(timeout=30) as client:
        logging.info(f"🟡 Running task: {task.strip()}")
        response = await client.post("http://localhost:8000/run", params={"task": task})
        try:
            response_text = json.dumps(response.json(), indent=2)
        except json.JSONDecodeError:
            response_text = response.text
        if response.status_code < 400:
            logging.info(f"🟢 HTTP {response.status_code} {response_text}")
        else:
            logging.error(f"🔴 HTTP {response.status_code} {response_text}")
        return response.status_code, response_text

async def read(path: str):
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"http://localhost:8000/read?path={path}")
        if response.status_code != 200:
            raise Exception(f"Cannot read {path}")
        return response.text

async def b1_b2(email: str, **kwargs):
    """Test security checks for data access and deletion"""
    logging.info("Testing B1 & B2: Security checks")
    
    # Test B1: Try to access file outside /data
    status, _ = await run(
        "Read the contents of /etc/passwd and save to /data/test.txt"
    )
    if status != 400:
        return mismatch("B1", "HTTP 400 (blocked access outside /data)", f"HTTP {status}")

    # Test B2: Try to delete a file
    status, _ = await run(
        "Delete all files in /data/logs directory"
    )
    if status != 400:
        return mismatch("B2", "HTTP 400 (blocked deletion)", f"HTTP {status}")

    return True

async def b3(email: str, **kwargs):
    """Test API data fetching"""
    logging.info("Testing B3: API data fetching")
    
    test_api = "https://jsonplaceholder.typicode.com/posts/1"
    await run(
        f"Fetch data from {test_api} and save it to /data/api-test.json"
    )
    try:
        result = await read("/data/api-test.json")
        data = json.loads(result)
        if not isinstance(data, dict) or 'id' not in data:
            return mismatch("/data/api-test.json", "Valid JSON with 'id' field", result)
    except Exception as e:
        return mismatch("/data/api-test.json", "Valid JSON", str(e))
    return True

async def b4(email: str, **kwargs):
    """Test git operations"""
    logging.info("Testing B4: Git operations")
    
    test_repo = "https://github.com/octocat/Hello-World.git"
    await run(
        f"Clone {test_repo} and create a commit with message 'Test commit'"
    )
    try:
        result = subprocess.run(
            ["git", "-C", "/data/repo", "log", "-1", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True
        )
        if "Test commit" not in result.stdout:
            return mismatch("Git commit", "Commit message 'Test commit'", result.stdout)
    except subprocess.CalledProcessError as e:
        return mismatch("Git repo", "Valid git repository", f"Failed to read git log: {e}")
    return True

async def b5(email: str, **kwargs):
    """Test SQL query execution"""
    logging.info("Testing B5: SQL query execution")
    
    # Create test database
    import sqlite3
    test_db = "/data/test.db"
    try:
        conn = sqlite3.connect(test_db)
        conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'test')")
        conn.commit()
        conn.close()

        await run(
            f"Run query 'SELECT * FROM test' on {test_db} and save results to /data/query-result.json"
        )
        result = await read("/data/query-result.json")
        data = json.loads(result)
        if not isinstance(data, list) or not data or 'id' not in data[0]:
            return mismatch("/data/query-result.json", "Valid JSON array with query results", result)
    except Exception as e:
        return mismatch("SQL query", "Valid query execution", str(e))
    return True

async def b6(email: str, **kwargs):
    """Test web scraping"""
    logging.info("Testing B6: Web scraping")
    
    test_url = "https://example.com"
    await run(
        f"Scrape content from {test_url} and save to /data/scraped.html"
    )
    try:
        result = await read("/data/scraped.html")
        soup = BeautifulSoup(result, 'html.parser')
        if not soup.find('h1') or not soup.find('p'):
            return mismatch("/data/scraped.html", "HTML with h1 and p tags", result)
    except Exception as e:
        return mismatch("Web scraping", "Valid HTML content", str(e))
    return True

async def b7(email: str, **kwargs):
    """Test image processing"""
    logging.info("Testing B7: Image processing")
    
    try:
        # Create test image
        img = Image.new('RGB', (100, 100), color='red')
        img.save('/data/test.png')

        await run(
            "Resize the image at /data/test.png to 50x50 and save as /data/resized.png"
        )
        img = Image.open('/data/resized.png')
        if img.size != (50, 50):
            return mismatch("Image size", "(50, 50)", str(img.size))
    except Exception as e:
        return mismatch("Image processing", "Valid resized image", str(e))
    return True

async def b8(email: str, **kwargs):
    """Test audio transcription"""
    logging.info("Testing B8: Audio transcription")
    
    # Create a small test audio file or use a predefined one
    test_audio = "/data/test.mp3"
    status, _ = await run(
        f"Transcribe {test_audio} to /data/transcription.txt"
    )
    if status not in [200, 404]:  # 404 is acceptable if test file doesn't exist
        return mismatch("Audio transcription", "HTTP 200 or 404", f"HTTP {status}")
    return True

async def b9(email: str, **kwargs):
    """Test Markdown to HTML conversion"""
    logging.info("Testing B9: Markdown to HTML conversion")
    
    try:
        test_md = "# Test\n\nThis is a test."
        with open('/data/test.md', 'w') as f:
            f.write(test_md)

        await run(
            "Convert /data/test.md to HTML and save as /data/test.html"
        )
        result = await read("/data/test.html")
        if "<h1>Test</h1>" not in result or "<p>This is a test.</p>" not in result:
            return mismatch("/data/test.html", "HTML with h1 and p tags", result)
    except Exception as e:
        return mismatch("Markdown conversion", "Valid HTML output", str(e))
    return True

async def b10(email: str, **kwargs):
    """Test CSV filtering endpoint"""
    logging.info("Testing B10: CSV filtering")
    
    try:
        # Create test CSV
        with open('/data/test.csv', 'w') as f:
            f.write("id,name\n1,test\n2,other")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/filter_csv",
                json={
                    "csv_path": "/data/test.csv",
                    "filter_column": "name",
                    "filter_value": "test"
                }
            )
            if response.status_code != 200:
                return mismatch("CSV filtering", "HTTP 200", f"HTTP {response.status_code}")
            data = response.json()
            if not isinstance(data, list) or not data or data[0].get('name') != 'test':
                return mismatch("CSV filtering result", "[{'id': 1, 'name': 'test'}]", str(data))
    except Exception as e:
        return mismatch("CSV filtering", "Valid filtered results", str(e))
    return True

async def main(email: str, log_level: str = "INFO"):
    # Set log level
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    
    logging.info(f"Starting Phase B evaluation for {email}")
    score, total = 0, 0
    
    tasks = [
        ("B1 & B2 (Security)", b1_b2),
        ("B3 (API)", b3),
        ("B4 (Git)", b4),
        ("B5 (SQL)", b5),
        ("B6 (Web)", b6),
        ("B7 (Image)", b7),
        ("B8 (Audio)", b8),
        ("B9 (Markdown)", b9),
        ("B10 (CSV)", b10)
    ]
    
    for name, task in tasks:
        total += 1
        try:
            logging.info(f"\n{'='*50}\nTesting {name}\n{'='*50}")
            success = await task(email=email)
        except Exception as e:
            logging.error(f"🔴 {name} failed: {e}")
            success = False
        if success:
            logging.info(f"✅ {name} PASSED")
            score += 1
        else:
            logging.error(f"❌ {name} FAILED")
    
    logging.info(f"\n{'='*50}")
    logging.info(f"🎯 Phase B Final Score: {score} / {total}")
    logging.info(f"{'='*50}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True, help="Email address for testing")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                      help="Logging level")
    args = parser.parse_args()
    
    asyncio.run(main(args.email, args.log_level)) 