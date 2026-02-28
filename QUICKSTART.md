# Quick Start Guide

This guide will help you get the Douban AI Spider up and running in minutes.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
```

## Step 2: Set Up API Key

You need an API key for the AI parsing feature. We recommend using DeepSeek:

1. **Get a DeepSeek API Key** (Recommended - Free tier available)
   - Visit: https://platform.deepseek.com/
   - Sign up and get your API key
   - Copy your API key

2. **Set the API Key as Environment Variable**

   On macOS/Linux:
   ```bash
   export DEEPSEEK_API_KEY="your-api-key-here"
   ```

   On Windows (PowerShell):
   ```powershell
   $env:DEEPSEEK_API_KEY="your-api-key-here"
   ```

   Or create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

## Step 3: Run the Spider

### Full Run (Scrape All 250 Movies)

```bash
python3 main.py
```

This will:
1. Scrape all 10 pages (250 movies) from Douban
2. Use AI to parse movie information
3. Store data in SQLite database
4. Generate visualization charts

### Test Run (Scrape Only 1 Page)

```bash
python3 main.py --test
```

Great for testing your setup!

### Custom Page Count

```bash
python3 main.py --pages 5
```

Scrape only 5 pages (125 movies).

## Step 4: View Results

### Check Database Info

```bash
python3 main.py info
```

This shows:
- Total movies in database
- Average rating
- Year range
- Top directors
- Top movies

### View Generated Charts

Charts are saved in `analysis/output/`:
- `year_distribution.png` - Movies by year
- `top_directors.png` - Most prolific directors
- `genre_distribution.png` - Genre breakdown
- `rating_distribution.png` - Rating histogram
- `country_distribution.png` - Movies by country
- `summary_report.txt` - Text summary

## Command Line Options

```
Usage: python3 main.py [OPTIONS]

Options:
  --skip-scrape    Skip web scraping (use existing database)
  --skip-ai        Skip AI parsing (store raw data only)
  --skip-charts    Skip chart generation
  --pages N        Number of pages to scrape (default: 10)
  --test           Run in test mode (scrape only 1 page)
```

## Examples

### Scrape without AI parsing (faster, no API key needed)

```bash
python3 main.py --skip-ai
```

### Generate charts from existing database

```bash
python3 main.py --skip-scrape --skip-ai
```

### Clear database and start fresh

```bash
python3 main.py clear
python3 main.py
```

## Troubleshooting

### "No API key provided" Error

Make sure you set the `DEEPSEEK_API_KEY` environment variable:

```bash
export DEEPSEEK_API_KEY="your-key-here"
python3 main.py
```

### 403 Forbidden Error

This means your IP might be temporarily blocked by Douban. Solutions:
- Wait a few minutes and try again
- Increase the delay in `utils/config.py` (DELAY_MIN and DELAY_MAX)
- Use a different network

### Import Errors

Make sure all dependencies are installed:

```bash
pip3 install -r requirements.txt
```

## Project Structure

```
python-ai-spider/
├── core/
│   ├── spider.py      # Web scraping logic
│   ├── ai_engine.py   # AI parsing (DeepSeek/OpenAI)
│   └── database.py    # SQLite operations
├── utils/
│   ├── config.py      # Configuration settings
│   └── logger.py      # Logging module
├── analysis/
│   └── charts.py      # Data visualization
├── data/
│   └── douban.db      # SQLite database (created after run)
├── analysis/output/   # Generated charts (created after run)
├── main.py            # Entry point
└── requirements.txt   # Dependencies
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check individual module tests by running them directly:
  ```bash
  python3 core/spider.py
  python3 core/ai_engine.py
  python3 core/database.py
  python3 analysis/charts.py
  ```

## Important Notes

1. **Rate Limiting**: The spider automatically adds delays between requests to avoid being blocked
2. **Educational Purpose Only**: This project is for learning purposes only
3. **API Costs**: DeepSeek offers free tier; monitor your API usage
4. **Data Storage**: All data is stored locally in SQLite database

## Support

For issues or questions:
- Check the [README.md](README.md) for detailed documentation
- Review the code comments in each module
- Check logs in `logs/spider.log` for detailed error information

Happy scraping! 🕷️
