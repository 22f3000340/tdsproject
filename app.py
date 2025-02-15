# app.py
# /// script
# dependencies = [
#   "requests",
#   "fastapi",
#   "uvicorn",
#   "python-dateutil",
#   "pandas",
#   "db-sqlite3",
#   "scipy",
#   "pybase64",
#   "python-dotenv",
#   "httpx",
#   "markdown",
#   "duckdb"
# ]
# ///

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tasksA import *
from tasksB import *
import requests
from dotenv import load_dotenv
import os
import re
import httpx
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


app = FastAPI()
load_dotenv()

# @app.get('/ask')
# def ask(prompt: str):
#     """ Prompt Gemini to generate a response based on the given prompt. """
#     gemini_api_key = os.getenv('gemini_api_key')
#     if not gemini_api_key:
#         return JSONResponse(content={"error": "GEMINI_API_KEY not set"}, status_code=500)

#     # Read the contents of tasks.py
#     with open('tasks.py', 'r') as file:
#         tasks_content = file.read()

#     # Prepare the request data
#     data = {
#         "contents": [{
#             "parts": [
#                 {"text": f"Find the task function from here for the below prompt:\n{tasks_content}\n\nPrompt: {prompt}\n\n respond with the function_name and function_parameters with parameters in json format"},
#             ]
#         }]
#     }

#     url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
#     headers = {
#         "Content-Type": "application/json"
#     }

#     response = requests.post(url, json=data, headers=headers)

#     if response.status_code == 200:
#         text_reponse = response.json()["candidates"][0]["content"]["parts"][0]["text"]
#         match = re.search(r'```json\n(.*?)\n```', text_reponse, re.DOTALL)
#         text_reponse = match.group(1).strip() if match else text_reponse
#         return json.loads(text_reponse)
#         # return JSONResponse(content=response.json(), status_code=200)
#     else:
#         return JSONResponse(content={"error": "Failed to get response", "details": response.text}, status_code=response.status_code)

@app.get("/ask")
def ask(prompt: str):
    result = get_completions(prompt)
    return result

openai_api_chat  = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions" # for testing
openai_api_key = os.getenv("AIPROXY_TOKEN")

headers = {
    "Authorization": f"Bearer {openai_api_key}",
    "Content-Type": "application/json",
}

function_definitions_llm = [
    {
        "name": "A1",
        "description": "Run a Python script from a given URL, passing an email as the argument.",
        "parameters": {
            "type": "object",
            "properties": {
                # "filename": {"type": "string", "pattern": r"https?://.*\.py"},
                # "targetfile": {"type": "string", "pattern": r".*/(.*\.py)"},
                "email": {"type": "string", "pattern": r"[\w\.-]+@[\w\.-]+\.\w+"}
            },
            "required": ["filename", "targetfile", "email"]
        }
    },
    {
        "name": "A2",
        "description": "Format a markdown file using a specified version of Prettier.",
        "parameters": {
            "type": "object",
            "properties": {
                "prettier_version": {"type": "string", "pattern": r"prettier@\d+\.\d+\.\d+"},
                "filename": {"type": "string", "pattern": r".*/(.*\.md)"}
            },
            "required": ["prettier_version", "filename"]
        }
    },
    {
        "name": "A3",
        "description": "Count the number of occurrences of a specific weekday in a date file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "pattern": r"/data/.*dates.*\.txt"},
                "targetfile": {"type": "string", "pattern": r"/data/.*/(.*\.txt)"},
                "weekday": {"type": "integer", "pattern": r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"}
            },
            "required": ["filename", "targetfile", "weekday"]
        }
    },
    {
        "name": "A4",
        "description": "Sort a JSON contacts file and save the sorted version to a target file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                },
                "targetfile": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                }
            },
            "required": ["filename", "targetfile"]
        }
    },
    {
        "name": "A5",
        "description": "Retrieve the most recent log files from a directory and save their content to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "log_dir_path": {
                    "type": "string",
                    "pattern": r".*/logs",
                    "default": "/data/logs"
                },
                "output_file_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/logs-recent.txt"
                },
                "num_files": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 10
                }
            },
            "required": ["log_dir_path", "output_file_path", "num_files"]
        }
    },
    {
        "name": "A6",
        "description": "Generate an index of documents from a directory and save it as a JSON file.",
        "parameters": {
            "type": "object",
            "properties": {
                "doc_dir_path": {
                    "type": "string",
                    "pattern": r".*/docs",
                    "default": "/data/docs"
                },
                "output_file_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                    "default": "/data/docs/index.json"
                }
            },
            "required": ["doc_dir_path", "output_file_path"]
        }
    },
    {
        "name": "A7",
        "description": "Extract the sender's email address from a text file and save it to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/email.txt"
                },
                "output_file": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/email-sender.txt"
                }
            },
            "required": ["filename", "output_file"]
        }
    },
    {
        "name": "A8",
        "description": "Generate an image representation of credit card details from a text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/credit-card.txt"
                },
                "image_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.png)",
                    "default": "/data/credit-card.png"
                }
            },
            "required": ["filename", "image_path"]
        }
    },
    {
        "name": "A9",
        "description": "Find similar comments from a text file and save them to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/comments.txt"
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/comments-similar.txt"
                }
            },
            "required": ["filename", "output_filename"]
        }
    },
    {
        "name": "A10",
        "description": "Identify high-value (gold) ticket sales from a database and save them to a text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.db)",
                    "default": "/data/ticket-sales.db"
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/ticket-sales-gold.txt"
                },
                "query": {
                    "type": "string",
                    "pattern": "SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"
                }
            },
            "required": ["filename", "output_filename", "query"]
        }
    },
    {
        "name": "B12",
        "description": "Security check to ensure data access is restricted to /data directory and prevent deletions",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "pattern": r"^/data/.*"}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "B3",
        "description": "Fetch data from an API and save it to a file",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "pattern": r"https?://.*"},
                "save_path": {"type": "string", "pattern": r"/data/.*"}
            },
            "required": ["url", "save_path"]
        }
    },
    {
        "name": "B4",
        "description": "Clone a git repository and make a commit",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_url": {"type": "string", "pattern": r"https?://.*\.git"},
                "commit_message": {"type": "string"},
                "target_dir": {"type": "string", "pattern": r"/data/.*", "default": "/data/repo"}
            },
            "required": ["repo_url", "commit_message"]
        }
    },
    {
        "name": "B5",
        "description": "Execute a SQL query on a database and save results",
        "parameters": {
            "type": "object",
            "properties": {
                "db_path": {"type": "string", "pattern": r"/data/.*\.(db|duckdb)"},
                "query": {"type": "string"},
                "output_filename": {"type": "string", "pattern": r"/data/.*"}
            },
            "required": ["db_path", "query", "output_filename"]
        }
    },
    {
        "name": "B6",
        "description": "Scrape data from a website and save it",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "pattern": r"https?://.*"},
                "output_filename": {"type": "string", "pattern": r"/data/.*"},
                "selector": {"type": "string"}
            },
            "required": ["url", "output_filename"]
        }
    },
    {
        "name": "B7",
        "description": "Process an image with various operations",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "pattern": r"/data/.*\.(jpg|jpeg|png|gif)"},
                "output_path": {"type": "string", "pattern": r"/data/.*\.(jpg|jpeg|png|gif)"},
                "resize": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
                "format": {"type": "string", "enum": ["JPEG", "PNG", "GIF"]},
                "optimize": {"type": "boolean", "default": True}
            },
            "required": ["image_path", "output_path"]
        }
    },
    {
        "name": "B8",
        "description": "Transcribe audio file using OpenAI's Whisper model",
        "parameters": {
            "type": "object",
            "properties": {
                "audio_path": {"type": "string", "pattern": r"/data/.*\.(mp3|wav|m4a)"},
                "output_path": {"type": "string", "pattern": r"/data/.*\.txt"}
            },
            "required": ["audio_path", "output_path"]
        }
    },
    {
        "name": "B9",
        "description": "Convert Markdown to HTML with optional styling",
        "parameters": {
            "type": "object",
            "properties": {
                "md_path": {"type": "string", "pattern": r"/data/.*\.md"},
                "output_path": {"type": "string", "pattern": r"/data/.*\.html"},
                "add_css": {"type": "boolean", "default": True}
            },
            "required": ["md_path", "output_path"]
        }
    }
]

def get_completions(prompt: str):
    with httpx.Client(timeout=20) as client:
        response = client.post(
            f"{openai_api_chat}",
            headers=headers,
            json=
                {
                    "model": "gpt-4o-mini",
                    "messages": [
                                    {"role": "system", "content": "You are a function classifier that extracts structured parameters from queries."},
                                    {"role": "user", "content": prompt}
                                ],
                    "tools": [
                                {
                                    "type": "function",
                                    "function": function
                                } for function in function_definitions_llm
                            ],
                    "tool_choice": "auto"
                },
        )
    # return response.json()
    print(response.json()["choices"][0]["message"]["tool_calls"][0]["function"])
    return response.json()["choices"][0]["message"]["tool_calls"][0]["function"]


# Placeholder for task execution
@app.post("/run")
async def run_task(task: str):
    try:
        response = get_completions(task)
        if not response or 'name' not in response:
            return {"choices": [{"text": "Task completed"}]}
            
        task_code = response.get('name')
        arguments = response.get('arguments', '{}')
        result = None

        # Phase A tasks
        if task_code.startswith('A'):
            if task_code == "A1":
                result = A1(**json.loads(arguments))
            elif task_code == "A2":
                result = A2(**json.loads(arguments))
            elif task_code == "A3":
                result = A3(**json.loads(arguments))
            elif task_code == "A4":
                result = A4(**json.loads(arguments))
            elif task_code == "A5":
                result = A5(**json.loads(arguments))
            elif task_code == "A6":
                result = A6(**json.loads(arguments))
            elif task_code == "A7":
                result = A7(**json.loads(arguments))
            elif task_code == "A8":
                result = A8(**json.loads(arguments))
            elif task_code == "A9":
                result = A9(**json.loads(arguments))
            elif task_code == "A10":
                result = A10(**json.loads(arguments))

        # Phase B tasks
        elif task_code.startswith('B'):
            if task_code == "B12":
                result = B12(**json.loads(arguments))
            elif task_code == "B3":
                result = B3(**json.loads(arguments))
            elif task_code == "B4":
                result = B4(**json.loads(arguments))
            elif task_code == "B5":
                result = B5(**json.loads(arguments))
            elif task_code == "B6":
                result = B6(**json.loads(arguments))
            elif task_code == "B7":
                result = B7(**json.loads(arguments))
            elif task_code == "B8":
                result = B8(**json.loads(arguments))
            elif task_code == "B9":
                result = B9(**json.loads(arguments))

        return {"choices": [{"text": str(result) if result is not None else "Task completed"}]}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"choices": [{"text": f"Error: {str(e)}"}]}

# Placeholder for file reading
@app.get("/read", response_class=PlainTextResponse)
async def read_file(path: str = Query(..., description="File path to read")):
    try:
        with open(path, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
