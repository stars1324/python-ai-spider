"""
AI Engine module for Douban AI Spider project.
Handles integration with LLM APIs (DeepSeek/OpenAI) for intelligent data extraction.
"""

import json
import os
from typing import Dict, List, Optional, Any

from openai import OpenAI

from utils.config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    AI_MAX_RETRIES, AI_TIMEOUT, AI_TEMPERATURE,
    AI_SYSTEM_PROMPT, AI_USER_PROMPT_TEMPLATE
)
from utils.logger import get_logger

logger = get_logger(__name__)


class AIEngine:
    """
    AI-powered data extraction engine using Large Language Models.
    Parses unstructured text into structured JSON format.
    """

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        Initialize the AI engine with API configuration.

        Args:
            api_key: API key for the LLM service (defaults to DEEPSEEK_API_KEY from config)
            base_url: Base URL for the API (defaults to DEEPSEEK_BASE_URL from config)
            model: Model name to use (defaults to DEEPSEEK_MODEL from config)
        """
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.base_url = base_url or DEEPSEEK_BASE_URL
        self.model = model or DEEPSEEK_MODEL

        # Validate API key
        if not self.api_key:
            logger.warning("No API key provided. Set DEEPSEEK_API_KEY environment variable.")
            raise ValueError("API key is required. Set DEEPSEEK_API_KEY environment variable or pass api_key parameter.")

        # Initialize OpenAI client (compatible with DeepSeek)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        # Statistics
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_tokens_used': 0
        }

        logger.info(f"AI Engine initialized with model: {self.model}")

    def parse_movie_info(self, info_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse unstructured movie information text into structured JSON.

        Args:
            info_text: Raw text containing director, actors, year, country, genres
                      Example: "导演: 克里斯托弗·诺兰 / 主演: 莱昂纳多·迪卡普里奥 ... / 2010年 / 美国 / 动作 / 科幻"

        Returns:
            Dictionary with keys: director, actors, year, country, genres
            Returns None if parsing fails
        """
        if not info_text or not info_text.strip():
            logger.warning("Empty info_text provided to AI engine")
            return None

        # Prepare the prompt
        user_prompt = AI_USER_PROMPT_TEMPLATE.format(text=info_text)

        try:
            response = self._call_api(
                system_prompt=AI_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )

            if response:
                parsed_data = self._parse_ai_response(response)
                if parsed_data:
                    logger.debug(f"Successfully parsed: {parsed_data.get('director', 'Unknown')}")
                    return parsed_data

            return None

        except Exception as e:
            logger.error(f"Error parsing movie info: {e}")
            self.stats['failed_calls'] += 1
            return None

    def _call_api(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """
        Make API call to the LLM service with retry logic.

        Args:
            system_prompt: System prompt defining the AI's role
            user_prompt: User prompt with the actual task

        Returns:
            AI response text, or None if all retries fail
        """
        for attempt in range(AI_MAX_RETRIES):
            try:
                logger.debug(f"API call attempt {attempt + 1}/{AI_MAX_RETRIES}")

                self.stats['total_calls'] += 1

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=AI_TEMPERATURE,
                    response_format={"type": "json_object"},  # Force JSON output
                    timeout=AI_TIMEOUT
                )

                # Extract response content
                content = response.choices[0].message.content

                # Track token usage
                if hasattr(response, 'usage') and response.usage:
                    self.stats['total_tokens_used'] += response.usage.total_tokens

                self.stats['successful_calls'] += 1
                return content

            except Exception as e:
                logger.warning(f"API call attempt {attempt + 1} failed: {e}")

                if attempt == AI_MAX_RETRIES - 1:
                    logger.error(f"All {AI_MAX_RETRIES} API call attempts failed")
                    self.stats['failed_calls'] += 1
                    return None

        return None

    def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse and validate AI response as JSON.

        Args:
            response_text: Raw response text from AI

        Returns:
            Parsed dictionary, or None if parsing fails
        """
        try:
            # Parse JSON response
            data = json.loads(response_text)

            # Validate required fields (allow None for optional fields)
            required_fields = ['director', 'actors', 'year', 'country', 'genres']
            result = {}

            for field in required_fields:
                if field in data:
                    result[field] = data[field]
                else:
                    result[field] = None
                    logger.warning(f"Missing field '{field}' in AI response")

            # Validate data types
            if result['actors'] is not None and not isinstance(result['actors'], list):
                logger.warning("'actors' field is not a list, converting")
                result['actors'] = [result['actors']]

            if result['genres'] is not None and not isinstance(result['genres'], list):
                logger.warning("'genres' field is not a list, converting")
                result['genres'] = [result['genres']]

            # Ensure year is an integer
            if result['year'] is not None:
                try:
                    result['year'] = int(result['year'])
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert year '{result['year']}' to int")
                    result['year'] = None

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"Response text: {response_text[:200]}...")
            return None

        except Exception as e:
            logger.error(f"Error processing AI response: {e}")
            return None

    def parse_movie_batch(self, movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse movie information for a batch of movies.

        Args:
            movies: List of movie dictionaries with 'info_text' field

        Returns:
            List of movie dictionaries with AI-parsed fields added
        """
        processed_movies = []
        total = len(movies)

        logger.info(f"Starting batch processing of {total} movies")

        for idx, movie in enumerate(movies, 1):
            logger.info(f"Processing movie {idx}/{total}: {movie.get('title', 'Unknown')}")

            # Get raw info text
            info_text = movie.get('info_text', '')

            if not info_text:
                logger.warning(f"No info_text for movie {movie.get('rank')}, skipping AI parsing")
                # Still include the movie with None values for AI fields
                movie.update({
                    'director': None,
                    'actors': [],
                    'year': None,
                    'country': None,
                    'genres': []
                })
                processed_movies.append(movie)
                continue

            # Parse with AI
            parsed_data = self.parse_movie_info(info_text)

            if parsed_data:
                # Merge parsed data into movie dictionary
                movie.update({
                    'director': parsed_data.get('director'),
                    'actors': parsed_data.get('actors', []),
                    'year': parsed_data.get('year'),
                    'country': parsed_data.get('country'),
                    'genres': parsed_data.get('genres', [])
                })
                logger.info(f"Successfully parsed: {movie.get('title')}")
            else:
                # Set default values if parsing failed
                movie.update({
                    'director': None,
                    'actors': [],
                    'year': None,
                    'country': None,
                    'genres': []
                })
                logger.warning(f"Failed to parse: {movie.get('title')}")

            processed_movies.append(movie)

        logger.info(f"Batch processing completed: {len(processed_movies)} movies")
        self._log_statistics()

        return processed_movies

    def generate_summary(self, movie_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a brief summary of a movie using AI.

        Args:
            movie_data: Dictionary with movie information

        Returns:
            Generated summary text, or None if generation fails
        """
        prompt = f"""Generate a brief one-sentence summary for this movie:

Title: {movie_data.get('title', 'Unknown')}
Director: {movie_data.get('director', 'Unknown')}
Year: {movie_data.get('year', 'Unknown')}
Genres: {', '.join(movie_data.get('genres', []))}

Return only the summary text, no JSON."""

        try:
            response = self._call_api(
                system_prompt="You are a movie critic skilled at writing concise, engaging movie summaries.",
                user_prompt=prompt
            )

            return response.strip() if response else None

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None

    def _log_statistics(self) -> None:
        """Log AI engine statistics."""
        logger.info("=" * 50)
        logger.info("AI Engine Statistics:")
        logger.info(f"  Total Calls: {self.stats['total_calls']}")
        logger.info(f"  Successful: {self.stats['successful_calls']}")
        logger.info(f"  Failed: {self.stats['failed_calls']}")
        logger.info(f"  Total Tokens: {self.stats['total_tokens_used']}")
        logger.info("=" * 50)

    def get_statistics(self) -> Dict[str, int]:
        """
        Get AI engine statistics.

        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()

    def reset_statistics(self) -> None:
        """Reset all statistics counters to zero."""
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_tokens_used': 0
        }
        logger.info("Statistics reset")

    def close(self) -> None:
        """Close the AI client connection."""
        if self.client:
            self.client.close()
            logger.info("AI client closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Test the AI engine
    # Make sure to set DEEPSEEK_API_KEY environment variable before running

    test_text = """导演: 克里斯托弗·诺兰 Christopher Nolan / 主演: 莱昂纳多·迪卡普里奥 Leonardo DiCaprio / 约瑟夫·高登-莱维特 Joseph Gordon-Levitt / 艾伦·佩吉 Ellen Page / 汤姆·哈迪 Tom Hardy / 渡边谦 Ken Watanabe / 希里安·墨菲 Cillian Murphy / 迪利普·劳 Dileep Rao / 基里安·墨菲 Kilarian Murphy / 2010年 / 美国 / 英国 / 动作 / 科幻 / 悬疑 / 冒险"""

    try:
        with AIEngine() as ai:
            print("Testing AI Engine...")
            print(f"Input text: {test_text[:100]}...")

            result = ai.parse_movie_info(test_text)

            if result:
                print("\nParsed result:")
                print(f"  Director: {result['director']}")
                print(f"  Actors: {', '.join(result['actors'][:5])}...")
                print(f"  Year: {result['year']}")
                print(f"  Country: {result['country']}")
                print(f"  Genres: {', '.join(result['genres'])}")
            else:
                print("Failed to parse text")

            ai._log_statistics()

    except ValueError as e:
        print(f"Error: {e}")
        print("Please set DEEPSEEK_API_KEY environment variable")
