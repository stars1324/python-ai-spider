"""
Charts module for Douban AI Spider project.
Handles data visualization and statistical analysis of movie data.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from collections import Counter

from utils.config import ANALYSIS_DIR
from utils.logger import get_logger

# Configure matplotlib for Chinese character support
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

logger = get_logger(__name__)


class ChartGenerator:
    """
    Data visualization generator for movie statistics.
    Creates various charts using matplotlib and pandas.
    """

    def __init__(self, output_dir: str = None):
        """
        Initialize the chart generator.

        Args:
            output_dir: Directory to save generated charts (defaults to config value)
        """
        self.output_dir = Path(output_dir or ANALYSIS_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set plot style
        plt.style.use('seaborn-v0_8-darkgrid')

        # Chart configuration
        self.figure_size = (12, 8)
        self.dpi = 300

        logger.info(f"Chart generator initialized. Output directory: {self.output_dir}")

    def load_movies_from_database(self, db) -> List[Dict[str, Any]]:
        """
        Load movies from database for analysis.

        Args:
            db: Database instance

        Returns:
            List of movie dictionaries
        """
        movies = db.get_all_movies()
        logger.info(f"Loaded {len(movies)} movies from database")
        return movies

    def create_year_distribution_chart(self, movies: List[Dict[str, Any]]) -> Optional[str]:
        """
        Create a line chart showing movie distribution by release year.

        Args:
            movies: List of movie dictionaries

        Returns:
            Path to saved chart file, or None if generation fails
        """
        try:
            # Extract years
            years = [m.get('year') for m in movies if m.get('year')]

            if not years:
                logger.warning("No valid year data found")
                return None

            # Count movies per year
            year_counts = Counter(years)
            sorted_years = sorted(year_counts.items())

            # Create figure
            fig, ax = plt.subplots(figsize=self.figure_size)

            # Plot line chart
            years_list = [y[0] for y in sorted_years]
            counts_list = [y[1] for y in sorted_years]

            ax.plot(years_list, counts_list, marker='o', linewidth=2, markersize=6)
            ax.fill_between(years_list, counts_list, alpha=0.3)

            # Customize chart
            ax.set_xlabel('Release Year', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Movies', fontsize=12, fontweight='bold')
            ax.set_title('Douban Top 250: Movie Distribution by Year', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha='right')

            # Adjust layout
            plt.tight_layout()

            # Save chart
            output_path = self.output_dir / 'year_distribution.png'
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            logger.info(f"Year distribution chart saved: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating year distribution chart: {e}")
            return None

    def create_top_directors_chart(self, movies: List[Dict[str, Any]], top_n: int = 10) -> Optional[str]:
        """
        Create a bar chart showing directors with the most Top 250 movies.

        Args:
            movies: List of movie dictionaries
            top_n: Number of top directors to show

        Returns:
            Path to saved chart file, or None if generation fails
        """
        try:
            # Extract directors
            directors = [m.get('director') for m in movies if m.get('director')]

            if not directors:
                logger.warning("No valid director data found")
                return None

            # Count movies per director
            director_counts = Counter(directors)
            top_directors = director_counts.most_common(top_n)

            # Create figure
            fig, ax = plt.subplots(figsize=self.figure_size)

            # Prepare data
            director_names = [d[0] for d in top_directors]
            movie_counts = [d[1] for d in top_directors]

            # Create color gradient for bars
            colors = plt.cm.viridis(range(len(director_names)))

            # Plot horizontal bar chart
            bars = ax.barh(director_names, movie_counts, color=colors)

            # Add value labels on bars
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height() / 2,
                       f'{int(width)}', ha='left', va='center', fontsize=10)

            # Customize chart
            ax.set_xlabel('Number of Movies in Top 250', fontsize=12, fontweight='bold')
            ax.set_ylabel('Director', fontsize=12, fontweight='bold')
            ax.set_title(f'Top {top_n} Directors in Douban Top 250', fontsize=14, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)

            # Invert y-axis to show highest count at top
            ax.invert_yaxis()

            # Adjust layout
            plt.tight_layout()

            # Save chart
            output_path = self.output_dir / 'top_directors.png'
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            logger.info(f"Top directors chart saved: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating top directors chart: {e}")
            return None

    def create_genre_distribution_chart(self, movies: List[Dict[str, Any]]) -> Optional[str]:
        """
        Create a pie chart showing distribution of movie genres.

        Args:
            movies: List of movie dictionaries

        Returns:
            Path to saved chart file, or None if generation fails
        """
        try:
            # Extract all genres (movies can have multiple genres)
            all_genres = []
            for movie in movies:
                genres = movie.get('genres', [])
                if isinstance(genres, list):
                    all_genres.extend(genres)

            if not all_genres:
                logger.warning("No valid genre data found")
                return None

            # Count genres
            genre_counts = Counter(all_genres)

            # Create figure
            fig, ax = plt.subplots(figsize=self.figure_size)

            # Prepare data
            genres = list(genre_counts.keys())
            counts = list(genre_counts.values())

            # Create color palette
            colors = plt.cm.Set3(range(len(genres)))

            # Create explode effect for largest slices
            explode = [0.05 if count > 30 else 0 for count in counts]

            # Plot pie chart
            wedges, texts, autotexts = ax.pie(
                counts,
                labels=genres,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                explode=explode,
                shadow=True
            )

            # Enhance text appearance
            for text in texts:
                text.set_fontsize(11)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')

            # Customize chart
            ax.set_title('Genre Distribution in Douban Top 250', fontsize=14, fontweight='bold')

            # Add legend
            ax.legend(wedges, [f'{g}: {c}' for g, c in zip(genres, counts)],
                     title="Genre (Count)",
                     loc="center left",
                     bbox_to_anchor=(1, 0, 0.5, 1))

            # Adjust layout
            plt.tight_layout()

            # Save chart
            output_path = self.output_dir / 'genre_distribution.png'
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            logger.info(f"Genre distribution chart saved: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating genre distribution chart: {e}")
            return None

    def create_rating_distribution_chart(self, movies: List[Dict[str, Any]]) -> Optional[str]:
        """
        Create a histogram showing distribution of movie ratings.

        Args:
            movies: List of movie dictionaries

        Returns:
            Path to saved chart file, or None if generation fails
        """
        try:
            # Extract ratings
            ratings = [m.get('rating') for m in movies if m.get('rating') is not None]

            if not ratings:
                logger.warning("No valid rating data found")
                return None

            # Create figure
            fig, ax = plt.subplots(figsize=self.figure_size)

            # Plot histogram
            n, bins, patches = ax.hist(ratings, bins=30, edgecolor='black', alpha=0.7)

            # Color the bars based on height
            for i, patch in enumerate(patches):
                patch.set_facecolor(plt.cm.viridis(i / len(patches)))

            # Add mean line
            mean_rating = sum(ratings) / len(ratings)
            ax.axvline(mean_rating, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_rating:.2f}')

            # Customize chart
            ax.set_xlabel('Rating', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Movies', fontsize=12, fontweight='bold')
            ax.set_title('Distribution of Movie Ratings in Douban Top 250', fontsize=14, fontweight='bold')
            ax.legend(fontsize=11)
            ax.grid(axis='y', alpha=0.3)

            # Adjust layout
            plt.tight_layout()

            # Save chart
            output_path = self.output_dir / 'rating_distribution.png'
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            logger.info(f"Rating distribution chart saved: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating rating distribution chart: {e}")
            return None

    def create_country_distribution_chart(self, movies: List[Dict[str, Any]], top_n: int = 10) -> Optional[str]:
        """
        Create a bar chart showing movies by production country.

        Args:
            movies: List of movie dictionaries
            top_n: Number of top countries to show

        Returns:
            Path to saved chart file, or None if generation fails
        """
        try:
            # Extract countries
            countries = [m.get('country') for m in movies if m.get('country')]

            if not countries:
                logger.warning("No valid country data found")
                return None

            # Count movies per country
            country_counts = Counter(countries)
            top_countries = country_counts.most_common(top_n)

            # Create figure
            fig, ax = plt.subplots(figsize=self.figure_size)

            # Prepare data
            country_names = [c[0] for c in top_countries]
            movie_counts = [c[1] for c in top_countries]

            # Plot bar chart
            bars = ax.bar(country_names, movie_counts, color=plt.cm.tab20(range(len(country_names))))

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5,
                       f'{int(height)}', ha='center', va='bottom', fontsize=10)

            # Customize chart
            ax.set_xlabel('Country', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Movies', fontsize=12, fontweight='bold')
            ax.set_title(f'Top {top_n} Countries in Douban Top 250', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)

            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')

            # Adjust layout
            plt.tight_layout()

            # Save chart
            output_path = self.output_dir / 'country_distribution.png'
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

            logger.info(f"Country distribution chart saved: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error creating country distribution chart: {e}")
            return None

    def create_summary_report(self, movies: List[Dict[str, Any]]) -> Optional[str]:
        """
        Create a comprehensive summary report with statistics.

        Args:
            movies: List of movie dictionaries

        Returns:
            Path to saved report file, or None if generation fails
        """
        try:
            report_path = self.output_dir / 'summary_report.txt'

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("DOUBAN TOP 250 MOVIES - SUMMARY REPORT\n")
                f.write("=" * 60 + "\n\n")

                # Basic statistics
                f.write("BASIC STATISTICS\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total Movies: {len(movies)}\n")

                # Rating statistics
                ratings = [m.get('rating') for m in movies if m.get('rating') is not None]
                if ratings:
                    f.write(f"Average Rating: {sum(ratings) / len(ratings):.2f}\n")
                    f.write(f"Highest Rating: {max(ratings):.1f}\n")
                    f.write(f"Lowest Rating: {min(ratings):.1f}\n")

                # Year range
                years = [m.get('year') for m in movies if m.get('year')]
                if years:
                    f.write(f"Year Range: {min(years)} - {max(years)}\n")

                # Top genres
                f.write("\nTOP GENRES\n")
                f.write("-" * 40 + "\n")
                all_genres = []
                for movie in movies:
                    genres = movie.get('genres', [])
                    if isinstance(genres, list):
                        all_genres.extend(genres)
                genre_counts = Counter(all_genres)
                for genre, count in genre_counts.most_common(10):
                    f.write(f"{genre}: {count}\n")

                # Top directors
                f.write("\nTOP DIRECTORS\n")
                f.write("-" * 40 + "\n")
                directors = [m.get('director') for m in movies if m.get('director')]
                director_counts = Counter(directors)
                for director, count in director_counts.most_common(10):
                    f.write(f"{director}: {count}\n")

                # Top countries
                f.write("\nTOP COUNTRIES\n")
                f.write("-" * 40 + "\n")
                countries = [m.get('country') for m in movies if m.get('country')]
                country_counts = Counter(countries)
                for country, count in country_counts.most_common(10):
                    f.write(f"{country}: {count}\n")

                f.write("\n" + "=" * 60 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 60 + "\n")

            logger.info(f"Summary report saved: {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"Error creating summary report: {e}")
            return None

    def generate_all_charts(self, movies: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
        """
        Generate all available charts.

        Args:
            movies: List of movie dictionaries

        Returns:
            Dictionary with chart types as keys and file paths as values
        """
        logger.info("Starting to generate all charts...")

        results = {
            'year_distribution': self.create_year_distribution_chart(movies),
            'top_directors': self.create_top_directors_chart(movies),
            'genre_distribution': self.create_genre_distribution_chart(movies),
            'rating_distribution': self.create_rating_distribution_chart(movies),
            'country_distribution': self.create_country_distribution_chart(movies),
            'summary_report': self.create_summary_report(movies)
        }

        success_count = sum(1 for v in results.values() if v is not None)
        logger.info(f"Chart generation completed: {success_count}/{len(results)} charts created")

        return results


if __name__ == "__main__":
    # Test the chart generator with sample data
    sample_movies = [
        {
            'title': 'The Shawshank Redemption',
            'year': 1994,
            'rating': 9.7,
            'director': 'Frank Darabont',
            'country': 'USA',
            'genres': ['Drama']
        },
        {
            'title': 'The Godfather',
            'year': 1972,
            'rating': 9.3,
            'director': 'Francis Ford Coppola',
            'country': 'USA',
            'genres': ['Crime', 'Drama']
        },
        # Add more sample data for testing...
    ]

    generator = ChartGenerator()
    results = generator.generate_all_charts(sample_movies)

    print("Generated charts:")
    for chart_type, path in results.items():
        print(f"  {chart_type}: {path}")
