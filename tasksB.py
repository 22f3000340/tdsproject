# Phase B: LLM-based Automation Agent for DataWorks Solutions

# B1 & B2: Security Checks
import os
import logging

def B12(filepath):
    """
    Security check to ensure:
    B1. Data outside /data is never accessed
    B2. Data is never deleted
    """
    # B1: Check if path starts with /data
    if not filepath.startswith('/data'):
        logging.error(f"Security violation: Attempted to access {filepath} outside /data directory")
        return False
    
    # B2: Check if operation might be trying to delete data
    if any(keyword in filepath.lower() for keyword in ['delete', 'remove', 'rm', 'del']):
        logging.error(f"Security violation: Attempted deletion operation on {filepath}")
        return False
    
    return True

# B3: Fetch Data from an API
def B3(url, save_path):
    """
    Fetch data from an API and save it to a file
    Args:
        url: API endpoint URL
        save_path: Path to save the response data
    """
    if not B12(save_path):
        logging.error(f"Security check failed for path: {save_path}")
        return None

    import requests
    import json

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Try to parse as JSON first
        try:
            content = json.dumps(response.json(), indent=2)
            content_type = 'json'
        except json.JSONDecodeError:
            # If not JSON, save as plain text
            content = response.text
            content_type = 'text'

        # Save the content
        with open(save_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        logging.info(f"Successfully saved {content_type} data to {save_path}")
        return True
    except requests.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error saving data: {str(e)}")
        return None

# B4: Clone a Git Repo and Make a Commit
def B4(repo_url, commit_message, target_dir='/data/repo'):
    """
    Clone a git repository and make a commit
    Args:
        repo_url: URL of the git repository
        commit_message: Commit message
        target_dir: Directory to clone into (must be under /data)
    """
    if not B12(target_dir):
        logging.error(f"Security check failed for path: {target_dir}")
        return None

    import subprocess
    import shutil

    try:
        # Clean up existing repo if it exists
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        # Clone the repository
        subprocess.run(["git", "clone", repo_url, target_dir], 
                      check=True, capture_output=True, text=True)

        # Configure git
        subprocess.run(["git", "-C", target_dir, "config", "user.email", "agent@dataworks.local"],
                      check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", target_dir, "config", "user.name", "DataWorks Agent"],
                      check=True, capture_output=True, text=True)

        # Add all changes
        subprocess.run(["git", "-C", target_dir, "add", "."],
                      check=True, capture_output=True, text=True)

        # Create commit
        subprocess.run(["git", "-C", target_dir, "commit", "-m", commit_message],
                      check=True, capture_output=True, text=True)

        logging.info(f"Successfully cloned repo and created commit in {target_dir}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Git operation failed: {e.stderr}")
        return None
    except Exception as e:
        logging.error(f"Error in git operation: {str(e)}")
        return None

# B5: Run SQL Query
def B5(db_path, query, output_filename):
    """
    Execute a SQL query on a database and save results
    Args:
        db_path: Path to SQLite or DuckDB database
        query: SQL query to execute
        output_filename: File to save results to
    """
    if not B12(db_path) or not B12(output_filename):
        logging.error("Security check failed for database or output path")
        return None

    import sqlite3
    import duckdb
    import json
    import pandas as pd

    try:
        # Determine database type and connect
        if db_path.endswith('.db'):
            conn = sqlite3.connect(db_path)
            # Enable DataFrame support
            conn.row_factory = sqlite3.Row
        else:
            conn = duckdb.connect(db_path)

        # Execute query
        if isinstance(conn, sqlite3.Connection):
            df = pd.read_sql_query(query, conn)
        else:
            df = conn.execute(query).df()

        # Convert results to JSON for saving
        result_json = df.to_json(orient='records', date_format='iso')
        
        # Save results
        with open(output_filename, 'w', encoding='utf-8') as f:
            if df.shape[0] == 1 and df.shape[1] == 1:
                # If single value, save just the value
                f.write(str(df.iloc[0, 0]))
            else:
                # Otherwise save formatted JSON
                json.dump(json.loads(result_json), f, indent=2)

        conn.close()
        logging.info(f"Successfully executed query and saved results to {output_filename}")
        return True
    except Exception as e:
        logging.error(f"Database operation failed: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return None

# B6: Web Scraping
def B6(url, output_filename, selector=None):
    """
    Scrape data from a website and save it
    Args:
        url: Website URL to scrape
        output_filename: File to save scraped data to
        selector: Optional CSS selector to extract specific content
    """
    if not B12(output_filename):
        logging.error(f"Security check failed for path: {output_filename}")
        return None

    import requests
    from bs4 import BeautifulSoup
    import json

    try:
        # Fetch webpage
        headers = {'User-Agent': 'DataWorks Agent/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract content based on selector if provided
        if selector:
            elements = soup.select(selector)
            content = [elem.get_text(strip=True) for elem in elements]
            # Save as JSON if multiple elements, text if single
            if len(content) > 1:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2)
            else:
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(content[0] if content else '')
        else:
            # Save full page content if no selector
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())

        logging.info(f"Successfully scraped website and saved to {output_filename}")
        return True
    except requests.RequestException as e:
        logging.error(f"Web scraping request failed: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error during web scraping: {str(e)}")
        return None

# B7: Image Processing
def B7(image_path, output_path, resize=None, format=None, optimize=True):
    """
    Process an image with various operations
    Args:
        image_path: Path to input image
        output_path: Path to save processed image
        resize: Optional tuple of (width, height) for resizing
        format: Optional output format (e.g., 'JPEG', 'PNG')
        optimize: Whether to optimize the output image
    """
    if not B12(image_path) or not B12(output_path):
        logging.error("Security check failed for image paths")
        return None

    from PIL import Image
    import os

    try:
        # Open image
        img = Image.open(image_path)

        # Convert RGBA to RGB if saving as JPEG
        if format == 'JPEG' and img.mode == 'RGBA':
            img = img.convert('RGB')

        # Resize if specified
        if resize:
            if isinstance(resize, (list, tuple)) and len(resize) == 2:
                img = img.resize(resize, Image.Resampling.LANCZOS)
            else:
                logging.warning("Invalid resize parameter, skipping resize")

        # Determine output format
        if format:
            save_format = format
        else:
            # Use input format or determine from output path
            save_format = img.format or os.path.splitext(output_path)[1][1:].upper() or 'PNG'

        # Save with optimization if supported
        save_args = {'format': save_format}
        if optimize and save_format in ['JPEG', 'PNG']:
            save_args['optimize'] = True
            if save_format == 'JPEG':
                save_args['quality'] = 85

        img.save(output_path, **save_args)
        logging.info(f"Successfully processed image and saved to {output_path}")
        return True
    except Exception as e:
        logging.error(f"Image processing failed: {str(e)}")
        return None

# B8: Audio Transcription
def B8(audio_path, output_path):
    """
    Transcribe audio file using OpenAI's Whisper model
    Args:
        audio_path: Path to input audio file
        output_path: Path to save transcription
    """
    if not B12(audio_path) or not B12(output_path):
        logging.error("Security check failed for audio paths")
        return None

    import os
    import requests
    import json

    try:
        # Get API token from environment
        api_token = os.getenv('AIPROXY_TOKEN')
        if not api_token:
            raise ValueError("AIPROXY_TOKEN environment variable not set")

        # Prepare the file for upload
        with open(audio_path, 'rb') as audio_file:
            files = {'file': audio_file}
            headers = {'Authorization': f'Bearer {api_token}'}
            
            # Make request to Whisper API
            response = requests.post(
                'http://aiproxy.sanand.workers.dev/openai/v1/audio/transcriptions',
                headers=headers,
                files=files,
                data={'model': 'whisper-1'}
            )
            response.raise_for_status()

            # Parse response
            result = response.json()
            
            # Save transcription
            with open(output_path, 'w', encoding='utf-8') as f:
                if isinstance(result, dict) and 'text' in result:
                    f.write(result['text'])
                else:
                    json.dump(result, f, indent=2)

        logging.info(f"Successfully transcribed audio and saved to {output_path}")
        return True
    except requests.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Transcription failed: {str(e)}")
        return None

# B9: Markdown to HTML Conversion
def B9(md_path, output_path, add_css=True):
    """
    Convert Markdown to HTML with optional styling
    Args:
        md_path: Path to input Markdown file
        output_path: Path to save HTML output
        add_css: Whether to add basic CSS styling
    """
    if not B12(md_path) or not B12(output_path):
        logging.error("Security check failed for file paths")
        return None

    import markdown
    from markdown.extensions import fenced_code
    from markdown.extensions import tables
    from markdown.extensions import toc

    try:
        # Read Markdown content
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Create Markdown converter with extensions
        md = markdown.Markdown(extensions=[
            'fenced_code',
            'tables',
            'toc',
            'attr_list',
            'def_list',
            'footnotes'
        ])

        # Convert to HTML
        html_content = md.convert(md_content)

        # Add CSS if requested
        if add_css:
            css = """
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; line-height: 1.6; padding: 1em; max-width: 50em; margin: auto; }
                code { background: #f4f4f4; padding: 0.2em 0.4em; border-radius: 3px; }
                pre { background: #f4f4f4; padding: 1em; overflow-x: auto; }
                img { max-width: 100%; }
                table { border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 8px; }
                th { background-color: #f4f4f4; }
            </style>
            """
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                {css}
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

        # Save HTML output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logging.info(f"Successfully converted Markdown to HTML and saved to {output_path}")
        return True
    except Exception as e:
        logging.error(f"Markdown conversion failed: {str(e)}")
        return None

# B10: API Endpoint for CSV Filtering
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

class CSVFilterRequest(BaseModel):
    csv_path: str
    filter_column: str
    filter_value: str

def B10(app: FastAPI):
    """
    Add an endpoint to filter CSV data
    Args:
        app: FastAPI application instance
    """
    @app.post("/filter_csv")
    async def filter_csv(request: CSVFilterRequest):
        """
        Filter a CSV file and return matching rows as JSON
        """
        if not B12(request.csv_path):
            raise HTTPException(status_code=400, detail="Invalid file path")

        try:
            # Read CSV file
            df = pd.read_csv(request.csv_path)

            # Validate column exists
            if request.filter_column not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column '{request.filter_column}' not found in CSV"
                )

            # Apply filter
            filtered_df = df[df[request.filter_column] == request.filter_value]

            # Convert to JSON response
            return filtered_df.to_dict(orient='records')

        except pd.errors.EmptyDataError:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        except pd.errors.ParserError:
            raise HTTPException(status_code=400, detail="Invalid CSV format")
        except Exception as e:
            logging.error(f"CSV filtering failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    return app