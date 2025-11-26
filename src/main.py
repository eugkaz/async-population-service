import sys
import asyncio
from src.db import DatabaseManager
from src.scrapers import ScraperFactory
from src.config import config

async def get_data():
    db = DatabaseManager()
    await db.init_models()
    
    try:
        scraper = ScraperFactory.get_scraper(config.DATA_SOURCE)
        data = await scraper.fetch_data()
        
        if not data:
            print("No data found.")
            return

        await db.clear_data_by_source(config.DATA_SOURCE)
        await db.save_countries(data, config.DATA_SOURCE)
        
    except Exception as e:
        print(f"Error getting data: {e}")
    finally:
        await db.close()

async def print_data():
    db = DatabaseManager()
    try:
        stats = await db.get_aggregated_stats(config.DATA_SOURCE)
        
        if not stats:
            print(f"No data found for source: {config.DATA_SOURCE}. Please run 'get_data' first.")
            return

        print(f"\nPopulation Statistics (Source: {config.DATA_SOURCE})")
        print("=" * 60)
        
        for row in stats:
            region = row.region
            total_pop = row.total_pop
            max_country = row.largest_country
            max_pop = row.largest_pop
            min_country = row.smallest_country
            min_pop = row.smallest_pop

            print(f"Region: {region}")
            print(f"Total Population: {total_pop:,}")
            print(f"Largest Country: {max_country} ({max_pop:,})")
            print(f"Smallest Country: {min_country} ({min_pop:,})")
            print("-" * 40)
            
    except Exception as e:
        print(f"Error printing data: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/main.py [get_data|print_data]")
        sys.exit(1)

    command = sys.argv[1]
    
    if command == "get_data":
        asyncio.run(get_data())
    elif command == "print_data":
        asyncio.run(print_data())
    else:
        print(f"Unknown command: {command}")