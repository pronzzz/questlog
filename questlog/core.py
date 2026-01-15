import os
import json
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

# Configure Gemini
def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it and try again.")
    genai.configure(api_key=api_key)

def generate_roadmap_data(topic: str, difficulty: str, language: str) -> Dict[str, Any]:
    """
    Generates structured roadmap data using Gemini API.
    """
    model = genai.GenerativeModel("gemini-flash-latest")
    
    prompt = f"""
    You are a Senior Staff Engineer designing a rigorous curriculum for a junior colleague. 
    You despise fluff. You prioritize official documentation over Medium articles. 
    You prioritize "building" over "reading."

    Create a learning roadmap for: "{topic}"
    Difficulty: {difficulty}
    Language: {language}

    Requirements:
    1. Break the topic into 4-6 "Levels".
    2. Each level needs 3 Resources (Read/Watch) and 1 "Boss Fight" (Build Task).
    3. Resources must be real, high-quality links (Official Docs > High rep blogs > Videos).
    4. Do not check if links exist, just provide the best known URL.
    
    Output strictly valid JSON with this schema:
    {{
      "topic_title": "String",
      "difficulty": "String",
      "levels": [
        {{
          "name": "Level Name",
          "resources": [
            {{"title": "Resource Title", "url": "URL", "type": "read|watch", "description": "Short reasoning"}}
          ],
          "boss_fight": {{
            "title": "Project Name",
            "description": "Objective of the project",
            "tasks": ["Task 1", "Task 2", "Task 3"]
          }}
        }}
      ]
    }}
    """
    
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        # Fallback if model returns markdown block
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

import requests

def validate_url(url: str, title: str) -> str:
    """
    Checks if a URL is valid (200 OK). Use HEAD request.
    If invalid, returns a Google Search URL.
    """
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code >= 400:
            raise Exception(f"Status code {response.status_code}")
        return url
    except Exception:
        # Fallback to Google Search
        clean_query = title.replace(" ", "+")
        return f"https://www.google.com/search?q={clean_query}"

def process_roadmap(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Iterates through the roadmap data and validates all resource links.
    """
    total_links = 0
    for level in data.get("levels", []):
        total_links += len(level.get("resources", []))
        
    print(f"Validating {total_links} links...") # This will be captured by the rich console in CLI if we handle it right, or just stdout
    
    for level in data.get("levels", []):
        for resource in level.get("resources", []):
            original_url = resource.get("url")
            title = resource.get("title")
            if original_url:
                validated_url = validate_url(original_url, title)
                resource["url"] = validated_url
    return data

def render_markdown(data: Dict[str, Any], template_path: str = "questlog/templates/roadmap.md.j2") -> str:
    """
    Renders the roadmap data into a Markdown string using Jinja2.
    """
    env = Environment(loader=FileSystemLoader("."))
    try:
        template = env.get_template(template_path)
    except Exception:
        # Fallback to local path if running from root vs package
        env = Environment(loader=FileSystemLoader(os.path.dirname(__file__) + "/templates"))
        template = env.get_template("roadmap.md.j2")
        
    return template.render(data)
