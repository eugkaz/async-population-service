from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func, text
from src.config import config
from src.models import Base, CountryStats

class DatabaseManager:
    def __init__(self):
        self.engine = create_async_engine(config.DATABASE_URL, echo=False)
        self.SessionLocal = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def init_models(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def clear_data_by_source(self, source: str):
        async with self.SessionLocal() as session:
            await session.execute(
                text("DELETE FROM country_stats WHERE source = :source"), 
                {"source": source}
            )
            await session.commit()

    async def save_countries(self, countries: list[dict], source: str):
        async with self.SessionLocal() as session:
            objects = [
                CountryStats(
                    name=c['name'],
                    region=c['region'],
                    population=c['population'],
                    source=source
                ) for c in countries
            ]
            session.add_all(objects)
            await session.commit()
            print(f"Saved {len(objects)} records from {source}.")

    async def get_aggregated_stats(self, source: str):
        async with self.SessionLocal() as session:
            stmt = select(
                CountryStats.region,
                func.sum(CountryStats.population).label("total_pop"),
                func.array_agg(
                    CountryStats.name.op('ORDER BY')(CountryStats.population.desc())
                )[1].label("largest_country"),
                func.max(CountryStats.population).label("largest_pop"),
                func.array_agg(
                    CountryStats.name.op('ORDER BY')(CountryStats.population.asc())
                )[1].label("smallest_country"),
                func.min(CountryStats.population).label("smallest_pop")
            ).where(
                CountryStats.source == source
            ).group_by(
                CountryStats.region
            ).order_by(
                text("total_pop DESC")
            )

            result = await session.execute(stmt)
            return result.fetchall()

    async def close(self):
        await self.engine.dispose()