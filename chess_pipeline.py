"""
Chess.com API Pipeline using dlt hub.
Loads comprehensive chess data from Chess.com API to BigQuery.
Optimized for Cloud Run deployment with GitHub Actions.

Available resources:
    players_profiles - Player profile information
    players_games - Chess games data with filtering by date range
    players_online_status - Current online status of players
    players_archives - Available game archives for players
"""

import dlt
from chess import source
from typing import List, Optional
import os
from datetime import datetime, timedelta
from cloud_helpers import get_project_id, is_cloud_run, print_environment_info


def load(resources: List[str], players: Optional[List[str]] = None, 
         start_month: Optional[str] = None, end_month: Optional[str] = None) -> None:
    """
    Execute a pipeline that loads chess data to BigQuery.
    Optimized for Cloud Run deployment with default BigQuery settings.
    
    Args:
        resources (List[str]): List of resource names to load. Available resources:
            - players_profiles: Player profile information
            - players_games: Chess games data (requires date range)
            - players_online_status: Current online status
            - players_archives: Available game archives
        players (Optional[List[str]]): List of player usernames to fetch data for
        start_month (Optional[str]): Start month in YYYY/MM format for games
        end_month (Optional[str]): End month in YYYY/MM format for games
    
    Returns:
        None: Prints loading information on successful execution.
    """
    # Default players if none provided
    if not players:
        players = ["magnuscarlsen", "rpragchess", "vincentkeymer", "dommarajugukesh"]
    
    # Set default date range if not provided (last 3 months)
    if not start_month or not end_month:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        start_month = start_date.strftime("%Y/%m")
        end_month = end_date.strftime("%Y/%m")
    
    print(f"Loading chess data for players: {players}")
    print(f"Date range: {start_month} to {end_month}")
    print(f"Resources: {resources}")
    
    # Configure pipeline for BigQuery with Cloud Run optimizations
    pipeline = dlt.pipeline(
        pipeline_name="chess_api",
        destination='bigquery',
        dataset_name="chess_data",
        progress="log",  # Enable progress logging
        # Cloud Run optimizations
        full_refresh=False,  # Use incremental loading
        dev_mode=False  # Production mode
    )
    
    # Create the data source
    chess_source = source(
        players=players,
        start_month=start_month,
        end_month=end_month
    )
    
    # Run the pipeline
    load_info = pipeline.run(chess_source.with_resources(*resources))
    
    # Print detailed load information
    print("Pipeline execution completed!")
    print(f"Loaded {len(load_info.load_packages)} package(s)")
    
    for package in load_info.load_packages:
        print(f"\nPackage {package.load_id}:")
        for table_name, table_info in package.schema_update.items():
            print(f"  - {table_name}: {table_info.get('row_count', 'N/A')} rows")


def load_sample_data() -> None:
    """
    Load a small sample of chess data for testing purposes.
    """
    print("Loading sample chess data (Magnus Carlsen games from last month)...")
    
    # Get last month
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    month_str = last_month.strftime("%Y/%m")
    
    load(
        resources=["players_profiles", "players_games", "players_online_status"],
        players=["magnuscarlsen"],
        start_month=month_str,
        end_month=month_str
    )


def load_all_data() -> None:
    """
    Load all available chess data resources for popular players.
    """
    print("Loading all chess data...")
    
    # Popular chess players
    players = [
        "magnuscarlsen", "rpragchess", "vincentkeymer", "dommarajugukesh",
        "hikaru", "danielnaroditsky", "alireza2003", "firouzja2003"
    ]
    
    # Last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    start_month = start_date.strftime("%Y/%m")
    end_month = end_date.strftime("%Y/%m")
    
    load(
        resources=["players_profiles", "players_games", "players_online_status"],
        players=players,
        start_month=start_month,
        end_month=end_month
    )


def cloud_run_handler():
    """
    Cloud Run entry point that loads chess data based on environment variables.
    This function is designed to be called by Cloud Run jobs.
    Automatically detects project ID from Cloud Run environment.
    """
    # Print environment information for debugging
    print_environment_info()
    
    # Get configuration from environment variables
    resources_env = os.getenv("CHESS_RESOURCES", "players_profiles,players_online_status")
    players_env = os.getenv("CHESS_PLAYERS")
    start_month_env = os.getenv("CHESS_START_MONTH")
    end_month_env = os.getenv("CHESS_END_MONTH")
    
    # Parse resources
    resources = [r.strip() for r in resources_env.split(",")]
    
    # Parse players
    players = [p.strip() for p in players_env.split(",")] if players_env else None
    
    # Verify we can detect the project ID
    project_id = get_project_id()
    if not project_id:
        print("⚠️  Warning: Could not automatically detect project ID")
        print("   Make sure you're running in a Google Cloud environment")
    else:
        print(f"✅ Automatically detected project ID: {project_id}")
    
    print(f"Cloud Run execution starting...")
    print(f"Resources: {resources}")
    print(f"Players: {players}")
    print(f"Start month: {start_month_env}")
    print(f"End month: {end_month_env}")
    
    try:
        load(resources, players, start_month_env, end_month_env)
        print("Cloud Run execution completed successfully!")
    except Exception as e:
        print(f"Cloud Run execution failed: {e}")
        raise


if __name__ == "__main__":
    """
    Main function to execute the chess data loading pipeline.
    
    For local development:
    1. Load sample data (Magnus Carlsen from last month) - good for testing
    2. Load all chess data - full dataset for popular players
    3. Load specific resources only
    
    For Cloud Run deployment, use cloud_run_handler() function.
    """
    
    # Check if running in Cloud Run environment
    if is_cloud_run():
        cloud_run_handler()
    else:
        # Local development
        print("🏠 Running in local development mode")
        project_id = get_project_id()
        if project_id:
            print(f"✅ Detected project ID: {project_id}")
        else:
            print("⚠️  No project ID detected - make sure you're authenticated with gcloud")
        
        # Option 1: Load sample data for testing
        load_sample_data()
        
        # Option 2: Uncomment to load all data (this will take a while!)
        # load_all_data()
        
        # Option 3: Uncomment to load specific resources
        # load(["players_profiles", "players_online_status"])
