"""
Pokemon API source for dlt pipeline.
Extracts comprehensive Pokemon data from the Pokemon API and loads it to BigQuery.
Available resources: [pokemon_details, berries, abilities, moves, types]
"""

import typing as t
from typing import Sequence, Iterable, Dict, Any, Optional
import dlt
from dlt.common.typing import TDataItem
from dlt.sources import DltResource
from dlt.sources.helpers import requests
import time
from .settings import (
    POKEMON_LIST_URL, POKEMON_DETAIL_URL, BERRY_LIST_URL, BERRY_DETAIL_URL,
    ABILITY_URL, MOVE_URL, TYPE_URL, DEFAULT_LIMIT, MAX_POKEMON_ID
)


@dlt.resource(write_disposition="replace")
def pokemon_details(limit: Optional[int] = None) -> Iterable[TDataItem]:
    """
    Fetches detailed Pokemon data by iterating through Pokemon IDs.
    Args:
        limit: Maximum number of Pokemon to fetch (default: all)
    Yields:
        dict: Detailed Pokemon data including stats, abilities, moves, etc.
    """
    max_id = min(limit or MAX_POKEMON_ID, MAX_POKEMON_ID)
    
    for pokemon_id in range(1, max_id + 1):
        try:
            url = f"{POKEMON_DETAIL_URL}/{pokemon_id}"
            response = requests.get(url)
            response.raise_for_status()
            
            pokemon_data = response.json()
            
            # Flatten and clean the data for BigQuery
            yield {
                "id": pokemon_data["id"],
                "name": pokemon_data["name"],
                "height": pokemon_data["height"],
                "weight": pokemon_data["weight"],
                "base_experience": pokemon_data["base_experience"],
                "is_default": pokemon_data["is_default"],
                "order": pokemon_data["order"],
                "species": pokemon_data["species"]["name"],
                "types": [t["type"]["name"] for t in pokemon_data["types"]],
                "abilities": [a["ability"]["name"] for a in pokemon_data["abilities"]],
                "moves": [m["move"]["name"] for m in pokemon_data["moves"]],
                "stats": {stat["stat"]["name"]: stat["base_stat"] for stat in pokemon_data["stats"]},
                "sprites": {
                    "front_default": pokemon_data["sprites"].get("front_default"),
                    "back_default": pokemon_data["sprites"].get("back_default"),
                    "front_shiny": pokemon_data["sprites"].get("front_shiny"),
                    "back_shiny": pokemon_data["sprites"].get("back_shiny")
                }
            }
            
            # Rate limiting - be respectful to the API
            time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Pokemon {pokemon_id}: {e}")
            continue


@dlt.resource(write_disposition="replace")
def berries() -> Iterable[TDataItem]:
    """
    Fetches detailed berry data from the Pokemon API.
    Yields:
        dict: Berry data including growth time, size, etc.
    """
    try:
        # First get the list of berries
        response = requests.get(BERRY_LIST_URL)
        response.raise_for_status()
        berry_list = response.json()
        
        # Fetch details for each berry
        for berry_summary in berry_list["results"]:
            try:
                berry_response = requests.get(berry_summary["url"])
                berry_response.raise_for_status()
                berry_data = berry_response.json()
                
                yield {
                    "id": berry_data["id"],
                    "name": berry_data["name"],
                    "growth_time": berry_data["growth_time"],
                    "max_harvest": berry_data["max_harvest"],
                    "natural_gift_power": berry_data["natural_gift_power"],
                    "size": berry_data["size"],
                    "smoothness": berry_data["smoothness"],
                    "soil_dryness": berry_data["soil_dryness"],
                    "firmness": berry_data["firmness"]["name"],
                    "flavors": {flavor["flavor"]["name"]: flavor["potency"] for flavor in berry_data["flavors"]},
                    "item": berry_data["item"]["name"] if berry_data["item"] else None
                }
                
                time.sleep(0.1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching berry {berry_summary['name']}: {e}")
                continue
                
    except requests.exceptions.RequestException as e:
        print(f"Error fetching berry list: {e}")


@dlt.resource(write_disposition="replace")
def abilities() -> Iterable[TDataItem]:
    """
    Fetches Pokemon abilities data.
    Yields:
        dict: Ability data including effect descriptions.
    """
    try:
        response = requests.get(ABILITY_URL)
        response.raise_for_status()
        ability_list = response.json()
        
        for ability_summary in ability_list["results"]:
            try:
                ability_response = requests.get(ability_summary["url"])
                ability_response.raise_for_status()
                ability_data = ability_response.json()
                
                yield {
                    "id": ability_data["id"],
                    "name": ability_data["name"],
                    "is_main_series": ability_data["is_main_series"],
                    "generation": ability_data["generation"]["name"],
                    "effect": ability_data["effect_entries"][0]["effect"] if ability_data["effect_entries"] else None,
                    "short_effect": ability_data["effect_entries"][0]["short_effect"] if ability_data["effect_entries"] else None,
                    "pokemon": [p["pokemon"]["name"] for p in ability_data["pokemon"]]
                }
                
                time.sleep(0.1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching ability {ability_summary['name']}: {e}")
                continue
                
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ability list: {e}")


@dlt.resource(write_disposition="replace")
def moves() -> Iterable[TDataItem]:
    """
    Fetches Pokemon moves data.
    Yields:
        dict: Move data including power, accuracy, type, etc.
    """
    try:
        response = requests.get(MOVE_URL)
        response.raise_for_status()
        move_list = response.json()
        
        for move_summary in move_list["results"]:
            try:
                move_response = requests.get(move_summary["url"])
                move_response.raise_for_status()
                move_data = move_response.json()
                
                yield {
                    "id": move_data["id"],
                    "name": move_data["name"],
                    "accuracy": move_data["accuracy"],
                    "effect_chance": move_data["effect_chance"],
                    "pp": move_data["pp"],
                    "priority": move_data["priority"],
                    "power": move_data["power"],
                    "damage_class": move_data["damage_class"]["name"],
                    "type": move_data["type"]["name"],
                    "generation": move_data["generation"]["name"],
                    "effect": move_data["effect_entries"][0]["effect"] if move_data["effect_entries"] else None,
                    "short_effect": move_data["effect_entries"][0]["short_effect"] if move_data["effect_entries"] else None
                }
                
                time.sleep(0.1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching move {move_summary['name']}: {e}")
                continue
                
    except requests.exceptions.RequestException as e:
        print(f"Error fetching move list: {e}")


@dlt.resource(write_disposition="replace")
def types() -> Iterable[TDataItem]:
    """
    Fetches Pokemon types data.
    Yields:
        dict: Type data including damage relations.
    """
    try:
        response = requests.get(TYPE_URL)
        response.raise_for_status()
        type_list = response.json()
        
        for type_summary in type_list["results"]:
            try:
                type_response = requests.get(type_summary["url"])
                type_response.raise_for_status()
                type_data = type_response.json()
                
                yield {
                    "id": type_data["id"],
                    "name": type_data["name"],
                    "generation": type_data["generation"]["name"],
                    "damage_relations": {
                        "double_damage_from": [d["name"] for d in type_data["damage_relations"]["double_damage_from"]],
                        "double_damage_to": [d["name"] for d in type_data["damage_relations"]["double_damage_to"]],
                        "half_damage_from": [d["name"] for d in type_data["damage_relations"]["half_damage_from"]],
                        "half_damage_to": [d["name"] for d in type_data["damage_relations"]["half_damage_to"]],
                        "no_damage_from": [d["name"] for d in type_data["damage_relations"]["no_damage_from"]],
                        "no_damage_to": [d["name"] for d in type_data["damage_relations"]["no_damage_to"]]
                    },
                    "pokemon": [p["pokemon"]["name"] for p in type_data["pokemon"]]
                }
                
                time.sleep(0.1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching type {type_summary['name']}: {e}")
                continue
                
    except requests.exceptions.RequestException as e:
        print(f"Error fetching type list: {e}")


@dlt.source
def source() -> Sequence[DltResource]:
    """
    The source function that returns all available Pokemon API resources.
    Returns:
        Sequence[DltResource]: A sequence of DltResource objects containing Pokemon data.
    """
    return [pokemon_details, berries, abilities, moves, types]
