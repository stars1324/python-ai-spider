"""
Configuration module for Douban AI Spider project.
Centralizes all configuration settings including API keys, database paths, and scraping parameters.
"""

import os
from pathlib import Path

# ================================
# Project Paths
# ================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
ANALYSIS_DIR = PROJECT_ROOT / "analysis" / "output"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)

# ================================
# API Configuration
# ================================
# Get API key from environment variable or use default
# Set your API key as environment variable: export DEEPSEEK_API_KEY="your-key"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Alternative: OpenAI API configuration
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# OPENAI_BASE_URL = "https://api.openai.com/v1"
# OPENAI_MODEL = "gpt-3.5-turbo"

# AI Processing settings
AI_MAX_RETRIES = 3
AI_TIMEOUT = 30  # seconds
AI_TEMPERATURE = 0.1  # Low temperature for more deterministic output

# ================================
# Scraping Configuration
# ================================
BASE_URL = "https://movie.douban.com/top250"
TOTAL_PAGES = 10
MOVIES_PER_PAGE = 25

# Rate limiting to avoid being blocked
DELAY_MIN = 1  # Minimum delay in seconds between requests
DELAY_MAX = 3  # Maximum delay in seconds between requests

# Request timeout
REQUEST_TIMEOUT = 10  # seconds

# ================================
# Database Configuration
# ================================
DB_PATH = str(DATA_DIR / "douban.db")

# Database schema
TABLE_NAME = "movies"

# ================================
# Logging Configuration
# ================================
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = str(LOGS_DIR / "spider.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ================================
# User-Agent Pool for Anti-Scraping
# ================================
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# ================================
# AI Prompt Templates
# ================================

# System prompt for AI engine
AI_SYSTEM_PROMPT = """You are a professional data extraction assistant specialized in parsing movie information.
Your task is to extract structured data from unstructured text and return it in valid JSON format.
Always ensure the output is valid JSON that can be parsed without errors."""

# User prompt template for parsing movie info
AI_USER_PROMPT_TEMPLATE = """Extract the following information from the text below and return as JSON:
- director: The director name(s)
- actors: List of main actors (extract as many as available)
- year: Release year as a number
- country: Production country
- genres: List of movie genres

Text to parse:
{text}

Return ONLY valid JSON in this exact format:
{{
    "director": "string",
    "actors": ["actor1", "actor2", ...],
    "year": 2000,
    "country": "string",
    "genres": ["genre1", "genre2", ...]
}}

If any field cannot be found, use null or empty list [] for arrays."""

# ================================
# Visualization Configuration
# ================================
CHART_WIDTH = 1200
CHART_HEIGHT = 800
CHART_THEME = "macarons"  # Options: macarons, infograph, shine, vintage
