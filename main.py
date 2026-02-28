"""
Main entry point for Douban AI Spider project.
Orchestrates the entire workflow: scraping, AI parsing, database storage, and visualization.
"""

import argparse
import sys
from pathlib import Path

from core.spider import DoubanSpider
from core.ai_engine import AIEngine
from core.database import Database
from analysis.charts import ChartGenerator
from utils.logger import get_logger
from utils.config import DB_PATH

logger = get_logger(__name__)


def main():
    """
    Main function that orchestrates the entire spider workflow.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Douban AI Spider - Intelligent Movie Data Crawler'
    )
    parser.add_argument(
        '--skip-scrape',
        action='store_true',
        help='Skip web scraping (use existing database)'
    )
    parser.add_argument(
        '--skip-ai',
        action='store_true',
        help='Skip AI parsing (store raw data only)'
    )
    parser.add_argument(
        '--skip-charts',
        action='store_true',
        help='Skip chart generation'
    )
    parser.add_argument(
        '--pages',
        type=int,
        default=10,
        help='Number of pages to scrape (default: 10)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (scrape only 1 page)'
    )

    args = parser.parse_args()

    # Print welcome message
    print("=" * 60)
    print("  Douban AI Spider - Intelligent Movie Data Crawler")
    print("=" * 60)
    print()

    # Step 1: Web Scraping
    if args.skip_scrape:
        logger.info("Skipping web scraping as requested")
        logger.info(f"Using existing database: {DB_PATH}")
    else:
        logger.info("Step 1: Starting web scraping...")

        # Adjust pages for test mode
        pages_to_scrape = 1 if args.test else args.pages

        try:
            with DoubanSpider() as spider:
                # Override total pages if specified
                if pages_to_scrape != 10:
                    spider.total_pages = pages_to_scrape

                # Fetch all movie data
                raw_movies = spider.fetch_all_pages()

                if not raw_movies:
                    logger.error("No movies were scraped. Exiting.")
                    return 1

                logger.info(f"Successfully scraped {len(raw_movies)} movies")

                # Step 2: AI Parsing (optional)
                if args.skip_ai:
                    logger.info("Skipping AI parsing as requested")
                    logger.info("Raw data will be stored without AI processing")
                    processed_movies = raw_movies
                else:
                    logger.info("Step 2: Starting AI data parsing...")

                    try:
                        with AIEngine() as ai:
                            # Parse movie information with AI
                            processed_movies = ai.parse_movie_batch(raw_movies)

                            # Remove 'info_text' field as it's no longer needed
                            for movie in processed_movies:
                                movie.pop('info_text', None)
                                movie.pop('cover_url', None)
                                movie.pop('detail_url', None)

                    except ValueError as e:
                        logger.error(f"AI Engine initialization failed: {e}")
                        logger.error("Please set DEEPSEEK_API_KEY environment variable")
                        logger.info("Continuing without AI parsing...")

                        # Use raw movies without AI processing
                        processed_movies = []
                        for movie in raw_movies:
                            movie.pop('info_text', None)
                            movie.pop('cover_url', None)
                            movie.pop('detail_url', None)
                            # Set default values for AI fields
                            movie.update({
                                'director': None,
                                'actors': [],
                                'year': None,
                                'country': None,
                                'genres': []
                            })
                            processed_movies.append(movie)

        except Exception as e:
            logger.error(f"Error during scraping phase: {e}")
            return 1

        # Step 3: Database Storage
        logger.info("Step 3: Storing data in database...")

        try:
            with Database() as db:
                # Insert movies into database
                success_count = db.insert_movies_batch(processed_movies)
                logger.info(f"Successfully stored {success_count}/{len(processed_movies)} movies in database")

        except Exception as e:
            logger.error(f"Error during database storage: {e}")
            return 1

    # Step 4: Data Visualization
    if args.skip_charts:
        logger.info("Skipping chart generation as requested")
    else:
        logger.info("Step 4: Generating data visualizations...")

        try:
            # Load movies from database
            with Database() as db:
                movies = db.get_all_movies()

                if not movies:
                    logger.warning("No movies found in database. Skipping chart generation.")
                else:
                    # Generate charts
                    chart_generator = ChartGenerator()
                    results = chart_generator.generate_all_charts(movies)

                    logger.info("Chart generation completed:")
                    for chart_type, path in results.items():
                        if path:
                            logger.info(f"  ✓ {chart_type}: {path}")
                        else:
                            logger.warning(f"  ✗ {chart_type}: Failed to generate")

        except Exception as e:
            logger.error(f"Error during chart generation: {e}")
            # Don't return error as charts are optional

    # Print completion message
    print()
    print("=" * 60)
    print("  ✓ Process completed successfully!")
    print("=" * 60)
    print(f"  Database: {DB_PATH}")
    print(f"  Charts:   {Path(DB_PATH).parent / 'analysis' / 'output'}")
    print("=" * 60)
    print()

    return 0


def show_database_info():
    """
    Display information about the current database.
    """
    try:
        with Database() as db:
            movies = db.get_all_movies()
            stats = db.get_statistics()

            print("\n" + "=" * 60)
            print("DATABASE INFORMATION")
            print("=" * 60)
            print(f"Database Path: {DB_PATH}")
            print(f"Total Movies: {stats.get('total_movies', 0)}")
            print(f"Average Rating: {stats.get('avg_rating', 'N/A')}")
            print(f"Year Range: {stats.get('year_range', {}).get('min', 'N/A')} - {stats.get('year_range', {}).get('max', 'N/A')}")

            if movies:
                print("\nTop 5 Movies:")
                for movie in movies[:5]:
                    print(f"  {movie['rank']}. {movie['title']} - {movie['rating']}")

            print("\nTop 5 Directors:")
            directors = db.get_top_directors(5)
            for director, count in directors:
                print(f"  {director}: {count} movie(s)")

            print("=" * 60 + "\n")

    except Exception as e:
        logger.error(f"Error reading database: {e}")
        return 1

    return 0


def clear_database():
    """
    Clear all data from the database.
    """
    print("\n⚠️  WARNING: This will delete all data from the database!")
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() != 'yes':
        print("Operation cancelled.")
        return 0

    try:
        with Database() as db:
            db.delete_all_movies()
            print("✓ Database cleared successfully.")

    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        return 1

    return 0


if __name__ == "__main__":
    # Check for special commands
    if len(sys.argv) > 1:
        if sys.argv[1] == 'info':
            sys.exit(show_database_info())
        elif sys.argv[1] == 'clear':
            sys.exit(clear_database())

    # Run main spider workflow
    sys.exit(main())
