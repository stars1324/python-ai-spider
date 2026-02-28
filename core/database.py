"""
Database module for Douban AI Spider project.
Handles all SQLite database operations including initialization, insertion, and querying.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

from utils.config import DB_PATH, TABLE_NAME
from utils.logger import get_logger

logger = get_logger(__name__)


class Database:
    """
    Database manager for movie data storage and retrieval.
    Uses SQLite for lightweight, serverless data persistence.
    """

    def __init__(self, db_path: str = None):
        """
        Initialize database connection and create tables if they don't exist.

        Args:
            db_path: Path to the SQLite database file (defaults to config value)
        """
        self.db_path = db_path or DB_PATH
        self.connection = None
        self._connect()
        self._create_tables()

    def _connect(self) -> None:
        """
        Establish database connection.
        Creates the database file and parent directories if they don't exist.
        """
        try:
            # Ensure parent directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def _create_tables(self) -> None:
        """
        Create the movies table if it doesn't exist.
        Defines the schema for storing movie information.
        """
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank INTEGER NOT NULL UNIQUE,
            title TEXT NOT NULL,
            director TEXT,
            actors TEXT,  -- Stored as JSON string
            year INTEGER,
            country TEXT,
            genres TEXT,  -- Stored as JSON string
            rating REAL,
            vote_count INTEGER,
            quote TEXT,
            ai_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for better query performance
        CREATE INDEX IF NOT EXISTS idx_rank ON {TABLE_NAME}(rank);
        CREATE INDEX IF NOT EXISTS idx_rating ON {TABLE_NAME}(rating);
        CREATE INDEX IF NOT EXISTS idx_year ON {TABLE_NAME}(year);
        CREATE INDEX IF NOT EXISTS idx_country ON {TABLE_NAME}(country);
        """

        try:
            cursor = self.connection.cursor()
            cursor.executescript(create_table_sql)
            self.connection.commit()
            logger.info(f"Table '{TABLE_NAME}' is ready")
        except sqlite3.Error as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def insert_movie(self, movie_data: Dict[str, Any]) -> bool:
        """
        Insert a single movie record into the database.

        Args:
            movie_data: Dictionary containing movie information with keys:
                - rank (int): Movie ranking
                - title (str): Movie title
                - director (str): Director name(s)
                - actors (list): List of actors
                - year (int): Release year
                - country (str): Production country
                - genres (list): List of genres
                - rating (float): Movie rating
                - vote_count (int): Number of votes
                - quote (str): Famous quote (optional)
                - ai_summary (str): AI-generated summary (optional)

        Returns:
            True if insertion was successful, False otherwise
        """
        insert_sql = f"""
        INSERT OR REPLACE INTO {TABLE_NAME} (
            rank, title, director, actors, year, country, genres,
            rating, vote_count, quote, ai_summary, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            # Convert lists to JSON strings for storage
            actors_json = json.dumps(movie_data.get('actors', []), ensure_ascii=False)
            genres_json = json.dumps(movie_data.get('genres', []), ensure_ascii=False)

            cursor = self.connection.cursor()
            cursor.execute(insert_sql, (
                movie_data.get('rank'),
                movie_data.get('title'),
                movie_data.get('director'),
                actors_json,
                movie_data.get('year'),
                movie_data.get('country'),
                genres_json,
                movie_data.get('rating'),
                movie_data.get('vote_count'),
                movie_data.get('quote'),
                movie_data.get('ai_summary'),
                datetime.now().isoformat()
            ))

            self.connection.commit()
            logger.debug(f"Inserted movie: {movie_data.get('title')} (Rank: {movie_data.get('rank')})")
            return True

        except sqlite3.Error as e:
            logger.error(f"Failed to insert movie {movie_data.get('rank')}: {e}")
            self.connection.rollback()
            return False

    def insert_movies_batch(self, movies: List[Dict[str, Any]]) -> int:
        """
        Insert multiple movie records in a single transaction.

        Args:
            movies: List of movie data dictionaries

        Returns:
            Number of successfully inserted movies
        """
        success_count = 0

        try:
            cursor = self.connection.cursor()

            for movie_data in movies:
                insert_sql = f"""
                INSERT OR REPLACE INTO {TABLE_NAME} (
                    rank, title, director, actors, year, country, genres,
                    rating, vote_count, quote, ai_summary, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                actors_json = json.dumps(movie_data.get('actors', []), ensure_ascii=False)
                genres_json = json.dumps(movie_data.get('genres', []), ensure_ascii=False)

                try:
                    cursor.execute(insert_sql, (
                        movie_data.get('rank'),
                        movie_data.get('title'),
                        movie_data.get('director'),
                        actors_json,
                        movie_data.get('year'),
                        movie_data.get('country'),
                        genres_json,
                        movie_data.get('rating'),
                        movie_data.get('vote_count'),
                        movie_data.get('quote'),
                        movie_data.get('ai_summary'),
                        datetime.now().isoformat()
                    ))
                    success_count += 1
                except sqlite3.Error as e:
                    logger.warning(f"Failed to insert movie {movie_data.get('rank')}: {e}")

            self.connection.commit()
            logger.info(f"Batch insert completed: {success_count}/{len(movies)} movies inserted")
            return success_count

        except sqlite3.Error as e:
            logger.error(f"Batch insert failed: {e}")
            self.connection.rollback()
            return success_count

    def get_movie_by_rank(self, rank: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a movie by its ranking.

        Args:
            rank: Movie rank (1-250)

        Returns:
            Movie data dictionary or None if not found
        """
        sql = f"SELECT * FROM {TABLE_NAME} WHERE rank = ?"

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (rank,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(row)
            return None

        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve movie rank {rank}: {e}")
            return None

    def get_all_movies(self) -> List[Dict[str, Any]]:
        """
        Retrieve all movies from the database.

        Returns:
            List of movie data dictionaries
        """
        sql = f"SELECT * FROM {TABLE_NAME} ORDER BY rank ASC"

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()

            return [self._row_to_dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve all movies: {e}")
            return []

    def get_movies_by_year(self, year: int) -> List[Dict[str, Any]]:
        """
        Retrieve all movies released in a specific year.

        Args:
            year: Release year

        Returns:
            List of movie data dictionaries
        """
        sql = f"SELECT * FROM {TABLE_NAME} WHERE year = ? ORDER BY rating DESC"

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (year,))
            rows = cursor.fetchall()

            return [self._row_to_dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve movies for year {year}: {e}")
            return []

    def get_top_directors(self, limit: int = 10) -> List[tuple]:
        """
        Get directors with the most movies in Top 250.

        Args:
            limit: Maximum number of directors to return

        Returns:
            List of tuples (director, count)
        """
        sql = f"""
        SELECT director, COUNT(*) as movie_count
        FROM {TABLE_NAME}
        WHERE director IS NOT NULL AND director != ''
        GROUP BY director
        ORDER BY movie_count DESC
        LIMIT ?
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, (limit,))
            return cursor.fetchall()

        except sqlite3.Error as e:
            logger.error(f"Failed to get top directors: {e}")
            return []

    def get_genre_distribution(self) -> List[tuple]:
        """
        Get distribution of movie genres.

        Returns:
            List of tuples (genre, count)
        """
        sql = f"""
        SELECT genre, COUNT(*) as count
        FROM (
            SELECT json_each.value as genre
            FROM {TABLE_NAME},
                 json_each({TABLE_NAME}.genres)
            WHERE json_valid({TABLE_NAME}.genres)
        )
        GROUP BY genre
        ORDER BY count DESC
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            return cursor.fetchall()

        except sqlite3.Error as e:
            logger.error(f"Failed to get genre distribution: {e}")
            return []

    def get_year_distribution(self) -> List[tuple]:
        """
        Get distribution of movies by release year.

        Returns:
            List of tuples (year, count)
        """
        sql = f"""
        SELECT year, COUNT(*) as count
        FROM {TABLE_NAME}
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year ASC
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            return cursor.fetchall()

        except sqlite3.Error as e:
            logger.error(f"Failed to get year distribution: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics about the movie database.

        Returns:
            Dictionary containing various statistics
        """
        stats = {}

        try:
            cursor = self.connection.cursor()

            # Total movies
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            stats['total_movies'] = cursor.fetchone()[0]

            # Average rating
            cursor.execute(f"SELECT AVG(rating) FROM {TABLE_NAME}")
            stats['avg_rating'] = round(cursor.fetchone()[0], 2) if cursor.fetchone()[0] else 0

            # Highest rated movie
            cursor.execute(f"SELECT title, rating FROM {TABLE_NAME} ORDER BY rating DESC LIMIT 1")
            result = cursor.fetchone()
            stats['highest_rated'] = {'title': result[0], 'rating': result[1]} if result else None

            # Year range
            cursor.execute(f"SELECT MIN(year), MAX(year) FROM {TABLE_NAME}")
            min_year, max_year = cursor.fetchone()
            stats['year_range'] = {'min': min_year, 'max': max_year}

            # Total votes
            cursor.execute(f"SELECT SUM(vote_count) FROM {TABLE_NAME}")
            stats['total_votes'] = cursor.fetchone()[0] or 0

            return stats

        except sqlite3.Error as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """
        Convert a database row to a dictionary.
        Parses JSON fields back into Python objects.

        Args:
            row: SQLite row object

        Returns:
            Dictionary representation of the row
        """
        movie = dict(row)

        # Parse JSON fields back to Python objects
        try:
            if movie.get('actors'):
                movie['actors'] = json.loads(movie['actors'])
            if movie.get('genres'):
                movie['genres'] = json.loads(movie['genres'])
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON for movie {movie.get('rank')}: {e}")

        return movie

    def delete_all_movies(self) -> bool:
        """
        Delete all movies from the database.
        Use with caution!

        Returns:
            True if deletion was successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM {TABLE_NAME}")
            self.connection.commit()
            logger.warning("All movies deleted from database")
            return True

        except sqlite3.Error as e:
            logger.error(f"Failed to delete all movies: {e}")
            self.connection.rollback()
            return False

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Test the database module
    with Database() as db:
        # Get statistics
        stats = db.get_statistics()
        print("Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # Get all movies
        movies = db.get_all_movies()
        print(f"\nTotal movies in database: {len(movies)}")

        if movies:
            print(f"\nFirst movie: {movies[0]['title']}")

        # Get top directors
        directors = db.get_top_directors(5)
        print(f"\nTop 5 Directors:")
        for director, count in directors:
            print(f"  {director}: {count} movies")
