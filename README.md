# Douban AI Spider - Intelligent Movie Data Crawler

An intelligent web scraping project that combines traditional crawling techniques with Large Language Model (LLM) AI capabilities to extract and analyze movie data from Douban Top 250.

## Project Overview

This project demonstrates how to leverage AI to solve the pain points of traditional web scraping, particularly in parsing unstructured text data into structured formats.

### Key Features

- **Automated Crawling**: Automatically fetches 250 top-rated movies from Douban
- **AI-Powered Parsing**: Uses LLM (DeepSeek/OpenAI) to intelligently parse unstructured movie information
- **Data Persistence**: Stores clean, structured data in SQLite database
- **Data Visualization**: Generates statistical charts and analysis

### Traditional vs AI Approach

| Aspect | Traditional (Regex) | AI-Powered |
|--------|---------------------|------------|
| Complexity | High - complex regex patterns | Low - natural language prompts |
| Maintainability | Fragile - breaks with HTML changes | Robust - adapts to format changes |
| Accuracy | Moderate | High - understands context |

## Tech Stack

- **Language**: Python 3.10+
- **HTTP Client**: httpx (async support)
- **HTML Parser**: BeautifulSoup4
- **AI Engine**: DeepSeek API / OpenAI API
- **Database**: SQLite3
- **Data Analysis**: Pandas + Matplotlib/PyEcharts

## Project Structure

```
Douban_AI_Spider/
├── core/
│   ├── __init__.py
│   ├── spider.py          # Web scraping logic
│   ├── ai_engine.py       # AI parsing engine
│   └── database.py        # Database operations
├── data/
│   └── douban.db          # SQLite database file
├── utils/
│   ├── config.py          # Configuration management
│   └── logger.py          # Logging module
├── analysis/
│   └── charts.py          # Data visualization
├── main.py                # Project entry point
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd python-ai-spider
```

2. **Create virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure API keys**:

Edit `utils/config.py` and add your API keys:
```python
DEEPSEEK_API_KEY = "your-deepseek-api-key"  # or OpenAI API key
```

Get your API key from:
- DeepSeek: https://platform.deepseek.com/
- OpenAI: https://platform.openai.com/

## Usage

Run the main script to start crawling and analysis:

```bash
python main.py
```

The script will:
1. Fetch movie data from Douban Top 250 (10 pages, 25 movies per page)
2. Use AI to parse unstructured information into structured data
3. Store the data in SQLite database
4. Generate visualization charts

### Modules Usage

You can also run individual modules:

```python
# Run spider only
from core.spider import DoubanSpider
spider = DoubanSpider()
movies = spider.fetch_all_pages()

# Run AI parsing only
from core.ai_engine import AIEngine
ai = AIEngine()
parsed_data = ai.parse_movie_info(raw_text)

# Query database
from core.database import Database
db = Database()
movies = db.get_all_movies()

# Generate charts
from analysis.charts import ChartGenerator
charts = ChartGenerator()
charts.generate_all_charts()
```

## Database Schema

### Table: `movies`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| rank | INTEGER | Movie ranking (1-250) |
| title | TEXT | Movie title |
| director | TEXT | Director name(s) |
| actors | TEXT | Actors list (JSON format) |
| year | INTEGER | Release year |
| country | TEXT | Production country |
| genres | TEXT | Movie genres (JSON format) |
| rating | REAL | Douban rating (0-10) |
| vote_count | INTEGER | Number of ratings |
| quote | TEXT | Famous quote from the movie |
| ai_summary | TEXT | AI-generated summary |
| created_at | TIMESTAMP | Record creation time |

## Anti-Scraping Measures

To respect Douban's servers and avoid being blocked:

- **Rate Limiting**: Random delay 1-3 seconds between requests
- **User-Agent Rotation**: Random user agents to simulate different browsers
- **Concurrency**: Single-threaded requests (no parallel scraping)
- **Exception Handling**: Comprehensive error handling with logging

## Legal & Ethical Notes

1. **Educational Purpose Only**: This project is for learning and research purposes only
2. **Respect robots.txt**: Follows website scraping guidelines
3. **Rate Limiting**: Implements delays to avoid server overload
4. **Data Usage**: Collected data should not be used for commercial purposes

## Configuration

Edit `utils/config.py` to customize:

```python
# API Configuration
DEEPSEEK_API_KEY = "your-api-key"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# Scraping Configuration
BASE_URL = "https://movie.douban.com/top250"
TOTAL_PAGES = 10
MOVIES_PER_PAGE = 25
DELAY_MIN = 1  # Minimum delay in seconds
DELAY_MAX = 3  # Maximum delay in seconds

# Database Configuration
DB_PATH = "data/douban.db"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "logs/spider.log"
```

## Troubleshooting

### Common Issues

1. **403 Forbidden Error**:
   - Increase delay time in config
   - Check if your IP is blocked
   - Try using different User-Agents

2. **API Rate Limit**:
   - Implement caching to avoid duplicate API calls
   - Check your API quota
   - Reduce batch size

3. **Database Locked**:
   - Close other database connections
   - Check file permissions

## Roadmap

- [ ] Add proxy support
- [ ] Implement incremental updates (only fetch new data)
- [ ] Add more visualization options
- [ ] Support for other movie databases (IMDb, Rotten Tomatoes)
- [ ] Export data to CSV/Excel
- [ ] Web dashboard for viewing results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes only. Please respect the terms of service of the websites being scraped.

## Blog Series

This project accompanies a blog series covering:
1. **Environment Setup**: Setting up development environment and analyzing HTML structure
2. **AI Integration**: Using LLM APIs for intelligent data extraction
3. **Database Design**: SQLite schema design and persistence logic
4. **Data Analysis**: Statistical analysis and visualization techniques

## Acknowledgments

- [Douban](https://movie.douban.com/) for providing the movie data
- [DeepSeek](https://www.deepseek.com/) for AI API services
- The open-source community for the amazing tools and libraries

---

**Note**: Always comply with website terms of service and robots.txt when scraping data. This project is intended for educational purposes to demonstrate AI-powered web scraping techniques.
