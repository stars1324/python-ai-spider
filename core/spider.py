"""
Spider module for Douban AI Spider project.
Handles web scraping, HTML parsing, and data extraction from Douban Top 250.
"""

import random
import time
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from utils.config import (
    BASE_URL, TOTAL_PAGES, MOVIES_PER_PAGE,
    DELAY_MIN, DELAY_MAX, REQUEST_TIMEOUT, USER_AGENTS
)
from utils.logger import get_logger

logger = get_logger(__name__)


class DoubanSpider:
    """
    Web scraper for Douban Top 250 movies.
    Implements anti-scraping measures and robust error handling.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize the spider with configuration.

        Args:
            base_url: Base URL for Douban Top 250 (defaults to config value)
        """
        self.base_url = base_url or BASE_URL
        self.total_pages = TOTAL_PAGES
        self.movies_per_page = MOVIES_PER_PAGE

        # HTTP client configuration
        self.client = None
        self._init_client()

        # Statistics
        self.stats = {
            'pages_fetched': 0,
            'movies_extracted': 0,
            'errors': 0
        }

    def _init_client(self) -> None:
        """
        Initialize HTTP client with default settings.
        """
        self.client = httpx.Client(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            headers=self._get_headers()
        )
        logger.info("HTTP client initialized")

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for request.
        Includes a random User-Agent to avoid detection.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def _random_delay(self) -> None:
        """
        Add random delay between requests to avoid being blocked.
        Delay time is between DELAY_MIN and DELAY_MAX seconds.
        """
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        logger.debug(f"Delaying for {delay:.2f} seconds...")
        time.sleep(delay)

    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a single page from the web.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string, or None if request fails
        """
        try:
            # Update headers with fresh User-Agent
            headers = self._get_headers()
            response = self.client.get(url, headers=headers)

            # Check for successful response
            if response.status_code == 200:
                logger.info(f"Successfully fetched: {url}")
                self.stats['pages_fetched'] += 1
                return response.text

            elif response.status_code == 403:
                logger.error(f"Access forbidden (403) for {url}. IP may be blocked.")
                self.stats['errors'] += 1
                return None

            else:
                logger.warning(f"Unexpected status code {response.status_code} for {url}")
                self.stats['errors'] += 1
                return None

        except httpx.TimeoutException:
            logger.error(f"Request timeout for {url}")
            self.stats['errors'] += 1
            return None

        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            self.stats['errors'] += 1
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            self.stats['errors'] += 1
            return None

    def _parse_movie_item(self, item, rank: int) -> Optional[Dict[str, Any]]:
        """
        Parse a single movie item from HTML.

        Args:
            item: BeautifulSoup element containing movie information
            rank: Movie ranking position

        Returns:
            Dictionary containing raw movie data, or None if parsing fails
        """
        try:
            movie = {}

            # Extract rank
            movie['rank'] = rank

            # Extract title (Chinese title)
            title_elem = item.find('span', class_='title')
            movie['title'] = title_elem.text.strip() if title_elem else ''

            # Extract rating
            rating_elem = item.find('span', class_='rating_num')
            movie['rating'] = float(rating_elem.text.strip()) if rating_elem else 0.0

            # Extract vote count (number of people who rated)
            # Format: "XXXXX人评价"
            vote_elem = item.find('div', class_='star').find_all('span')[-1]
            if vote_elem:
                vote_text = vote_elem.text.strip()
                # Extract numeric part
                movie['vote_count'] = int(vote_text.replace('人评价', '').replace(',', ''))
            else:
                movie['vote_count'] = 0

            # Extract quote (famous quote from the movie)
            quote_elem = item.find('span', class_='inq')
            movie['quote'] = quote_elem.text.strip() if quote_elem else ''

            # Extract info block (contains director, actors, year, country, genre)
            # Format example: "导演: 克里斯托弗·诺兰 Christopher Nolan / 主演: 约瑟夫·高登-莱维特 Joseph Gordon-Levitt ... / 2010年 / 美国 / 英国 / 动作 / 科幻 / 悬疑"
            info_elem = item.find('div', class_='bd').find('p', class_='')
            movie['info_text'] = info_elem.text.strip() if info_elem else ''

            # Extract image URL
            img_elem = item.find('div', class_='pic').find('img')
            movie['cover_url'] = img_elem.get('src', '') if img_elem else ''

            # Extract detail page URL
            link_elem = item.find('div', class_='hd').find('a')
            movie['detail_url'] = link_elem.get('href', '') if link_elem else ''

            self.stats['movies_extracted'] += 1
            return movie

        except Exception as e:
            logger.error(f"Error parsing movie item at rank {rank}: {e}")
            self.stats['errors'] += 1
            return None

    def _parse_page(self, html: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Parse movie items from a single page of HTML.

        Args:
            html: HTML content string
            page_num: Page number (for logging purposes)

        Returns:
            List of movie data dictionaries
        """
        movies = []

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Find all movie items
            movie_items = soup.find_all('div', class_='item')
            logger.info(f"Found {len(movie_items)} movies on page {page_num}")

            for idx, item in enumerate(movie_items):
                # Calculate rank based on page number and position
                rank = (page_num - 1) * self.movies_per_page + idx + 1

                movie = self._parse_movie_item(item, rank)
                if movie:
                    movies.append(movie)

        except Exception as e:
            logger.error(f"Error parsing page {page_num}: {e}")
            self.stats['errors'] += 1

        return movies

    def fetch_page(self, page_num: int = 1) -> List[Dict[str, Any]]:
        """
        Fetch and parse a single page of movies.

        Args:
            page_num: Page number to fetch (1-10)

        Returns:
            List of movie data dictionaries
        """
        # Build URL for the specific page
        # Format: https://movie.douban.com/top250?start=0
        start = (page_num - 1) * self.movies_per_page
        url = f"{self.base_url}?start={start}"

        logger.info(f"Fetching page {page_num}: {url}")

        # Fetch HTML content
        html = self._fetch_page(url)

        if not html:
            logger.error(f"Failed to fetch page {page_num}")
            return []

        # Parse movies from HTML
        movies = self._parse_page(html, page_num)

        # Add delay before next request (except for last page)
        if page_num < self.total_pages:
            self._random_delay()

        return movies

    def fetch_all_pages(self) -> List[Dict[str, Any]]:
        """
        Fetch all pages of movies from Douban Top 250.

        Returns:
            List of all movie data dictionaries
        """
        all_movies = []

        logger.info(f"Starting to fetch {self.total_pages} pages from {self.base_url}")

        for page_num in range(1, self.total_pages + 1):
            logger.info(f"Processing page {page_num}/{self.total_pages}")

            movies = self.fetch_page(page_num)
            all_movies.extend(movies)

            logger.info(f"Collected {len(movies)} movies from page {page_num}")

        logger.info(f"Completed! Total movies collected: {len(all_movies)}")
        self._log_statistics()

        return all_movies

    def fetch_single_movie_detail(self, detail_url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information from a movie's detail page.

        Args:
            detail_url: URL of the movie detail page

        Returns:
            Dictionary with additional movie details, or None if fetch fails
        """
        html = self._fetch_page(detail_url)

        if not html:
            return None

        try:
            soup = BeautifulSoup(html, 'html.parser')

            details = {}

            # Extract additional information from detail page
            # This can be expanded based on specific needs

            # Extract full summary/plot
            summary_elem = soup.find('span', property='v:summary')
            details['plot_summary'] = summary_elem.text.strip() if summary_elem else ''

            # Extract episode information if available
            # ... more parsing logic can be added here

            return details

        except Exception as e:
            logger.error(f"Error parsing detail page {detail_url}: {e}")
            return None

    def _log_statistics(self) -> None:
        """Log scraping statistics."""
        logger.info("=" * 50)
        logger.info("Scraping Statistics:")
        logger.info(f"  Pages Fetched: {self.stats['pages_fetched']}")
        logger.info(f"  Movies Extracted: {self.stats['movies_extracted']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info("=" * 50)

    def get_statistics(self) -> Dict[str, int]:
        """
        Get scraping statistics.

        Returns:
            Dictionary with statistics keys: pages_fetched, movies_extracted, errors
        """
        return self.stats.copy()

    def reset_statistics(self) -> None:
        """Reset all statistics counters to zero."""
        self.stats = {
            'pages_fetched': 0,
            'movies_extracted': 0,
            'errors': 0
        }
        logger.info("Statistics reset")

    def close(self) -> None:
        """Close the HTTP client."""
        if self.client:
            self.client.close()
            logger.info("HTTP client closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Test the spider module
    with DoubanSpider() as spider:
        # Fetch first page only for testing
        print("Fetching first page...")
        movies = spider.fetch_page(1)

        print(f"\nFetched {len(movies)} movies:")
        for movie in movies[:3]:  # Show first 3
            print(f"\nRank {movie['rank']}: {movie['title']}")
            print(f"  Rating: {movie['rating']}")
            print(f"  Votes: {movie['vote_count']}")
            print(f"  Quote: {movie['quote'][:50]}..." if movie['quote'] else "  Quote: N/A")
            print(f"  Info: {movie['info_text'][:100]}...")

        spider._log_statistics()
