"""
Pokemon API Pipeline using dlt hub.
Loads comprehensive Pokemon data from the Pokemon API to BigQuery.

Available resources:
    pokemon_details - Detailed Pokemon data with stats, abilities, moves
    berries - Berry data with growth properties
    abilities - Pokemon abilities with effects
    moves - Pokemon moves with power, accuracy, type
    types - Pokemon types with damage relations
"""

import dlt
from pokemon import source
from typing import List, Optional
import os
from datetime import datetime, timedelta
from cloud_helpers import get_project_id, is_cloud_run, print_environment_info


def load(resources: List[str], pokemon_limit: Optional[int] = None) -> None:
    """
    Execute a pipeline that loads Pokemon data to BigQuery.
    Optimized for Cloud Run deployment with default BigQuery settings.
    
    Args:
        resources (List[str]): List of resource names to load. Available resources:
            - pokemon_details: Detailed Pokemon data (can be limited)
            - berries: Berry data
            - abilities: Pokemon abilities
            - moves: Pokemon moves
            - types: Pokemon types
        pokemon_limit (Optional[int]): Limit number of Pokemon to fetch (for testing)
    
    Returns:
        None: Prints loading information on successful execution.
    """
    # Configure pipeline for BigQuery with Cloud Run optimizations
    pipeline = dlt.pipeline(
        pipeline_name="pokemon_api",
        destination='bigquery',
        dataset_name="pokemon_data",
        progress="log",  # Enable progress logging
        # Cloud Run optimizations
        full_refresh=False,  # Use incremental loading
        dev_mode=False  # Production mode
    )
    
    # Create source with optional Pokemon limit
    pokemon_source = source()
    
    # If pokemon_details is requested and limit is specified, configure it
    if "pokemon_details" in resources and pokemon_limit:
        pokemon_source = pokemon_source.with_resources(
            pokemon_details=pokemon_source.resources["pokemon_details"].add_limit(pokemon_limit)
        )
    
    # Run the pipeline
    load_info = pipeline.run(pokemon_source.with_resources(*resources))
    
    # Print detailed load information
    print("Pipeline execution completed!")
    print(f"Loaded {len(load_info.load_packages)} package(s)")
    
    for package in load_info.load_packages:
        print(f"\nPackage {package.load_id}:")
        for table_name, table_info in package.schema_update.items():
            print(f"  - {table_name}: {table_info.get('row_count', 'N/A')} rows")


def load_sample_data() -> None:
    """
    Load a small sample of Pokemon data for testing purposes.
    """
    print("Loading sample Pokemon data (first 10 Pokemon)...")
    load(["pokemon_details"], pokemon_limit=10)


def load_all_data() -> None:
    """
    Load all available Pokemon data resources.
    """
    print("Loading all Pokemon data...")
    resources = ["pokemon_details", "berries", "abilities", "moves", "types"]
    load(resources)


def cloud_run_handler():
    """
    Cloud Run entry point that loads Pokemon data based on environment variables.
    This function is designed to be called by Cloud Run jobs.
    Automatically detects project ID from Cloud Run environment.
    """
    # Print environment information for debugging
    print_environment_info()
    
    # Get configuration from environment variables
    resources_env = os.getenv("POKEMON_RESOURCES", "pokemon_details")
    pokemon_limit_env = os.getenv("POKEMON_LIMIT")
    
    # Parse resources
    resources = [r.strip() for r in resources_env.split(",")]
    
    # Parse limit if provided
    pokemon_limit = int(pokemon_limit_env) if pokemon_limit_env else None
    
    # Verify we can detect the project ID
    project_id = get_project_id()
    if not project_id:
        print("⚠️  Warning: Could not automatically detect project ID")
        print("   Make sure you're running in a Google Cloud environment")
    else:
        print(f"✅ Automatically detected project ID: {project_id}")
    
    print(f"Cloud Run execution starting...")
    print(f"Resources: {resources}")
    print(f"Pokemon limit: {pokemon_limit}")
    
    try:
        load(resources, pokemon_limit)
        print("Cloud Run execution completed successfully!")
    except Exception as e:
        print(f"Cloud Run execution failed: {e}")
        raise


if __name__ == "__main__":
    """
    Main function to execute the Pokemon data loading pipeline.
    
    For local development:
    1. Load sample data (first 10 Pokemon) - good for testing
    2. Load all Pokemon data - full dataset
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
        # load(["pokemon_details", "berries"])
