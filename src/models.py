from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class CountryStats(Base):
    __tablename__ = "country_stats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    population = Column(BigInteger, nullable=False)
    source = Column(String, nullable=False, index=True)

    def __repr__(self):
        return f"<Country(name={self.name}, region={self.region}, pop={self.population})>"