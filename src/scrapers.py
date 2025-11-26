import aiohttp
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import re

class BaseScraper(ABC):
    @abstractmethod
    async def fetch_data(self) -> list[dict]:
        pass
    
    def get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

class WikipediaScraper(BaseScraper):
    URL = "https://en.wikipedia.org/w/index.php?title=List_of_countries_and_dependencies_by_population_(United_Nations)&oldid=1215058959"

    async def fetch_data(self) -> list[dict]:
        print(f"Fetching data from Wikipedia ({self.URL})...")
        async with aiohttp.ClientSession() as session:
            async with session.get(self.URL, headers=self.get_headers()) as response:
                if response.status != 200:
                    print(f"Error: Failed to fetch page. Status: {response.status}")
                    return []
                html = await response.text()

        soup = BeautifulSoup(html, 'lxml')
        

        tables = soup.find_all('table', {'class': 'wikitable'})
        
        target_table = None
        for t in tables:
            headers = t.get_text().lower()
            if "location" in headers and "2023" in headers:
                target_table = t
                break
        
        if not target_table:
            if tables:
                target_table = tables[0]
            else:
                print("Error: No 'wikitable' found.")
                return []

        data = []
        rows = target_table.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            
            if len(cols) < 5:
                continue
            
            try:
                country_name = cols[0].get_text(strip=True)
                country_name = re.sub(r'\[.*?\]', '', country_name)
                region = cols[4].get_text(strip=True)
                pop_str = cols[2].get_text(strip=True)
                pop_clean = re.sub(r'[^\d]', '', pop_str)
                
                if not pop_clean:
                    continue
                
                population = int(pop_clean)
                if "World" in country_name:
                    continue

                data.append({
                    'name': country_name,
                    'region': region,
                    'population': population
                })
            except (ValueError, IndexError) as e:
                continue
                
        print(f"Parsed {len(data)} countries from Wikipedia.")
        return data

class StatisticsTimesScraper(BaseScraper):
    URL = "https://statisticstimes.com/demographics/countries-by-population.php"

    async def fetch_data(self) -> list[dict]:
        print(f"Fetching data from StatisticsTimes ({self.URL})...")
        async with aiohttp.ClientSession() as session:
            async with session.get(self.URL, headers=self.get_headers()) as response:
                 if response.status != 200:
                    print(f"Error: Failed to fetch page. Status: {response.status}")
                    return []
                 html = await response.text()

        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table', {'id': 'table_id'})
        
        if not table:
            print("Error: Could not find table with id 'table_id'.")
            return []
        
        data = []
        rows = table.find('tbody').find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
            
            try:
                country_name = cols[1].get_text(strip=True)
                region = cols[4].get_text(strip=True)
                pop_str = cols[2].get_text(strip=True)
                population = int(re.sub(r'[^\d]', '', pop_str))

                data.append({
                    'name': country_name,
                    'region': region,
                    'population': population
                })
            except (ValueError, IndexError):
                continue

        print(f"Parsed {len(data)} countries from StatisticsTimes.")
        return data

class ScraperFactory:
    @staticmethod
    def get_scraper(source_type: str) -> BaseScraper:
        if source_type == "WIKIPEDIA":
            return WikipediaScraper()
        elif source_type == "STATISTICS_TIMES":
            return StatisticsTimesScraper()
        else:
            raise ValueError(f"Unknown source type: {source_type}")
