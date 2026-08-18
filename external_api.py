import httpx

from schemas import WeatherResponse,GoogleBooks
# import requests
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
EXTERNAL_TIMEOUT = float(os.getenv("EXTERNAL_TIMEOUT", "5.0"))

async def fetch_weather(
    latitude: float,
    longitude: float,
) -> WeatherResponse:
    async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m",
            },
        )

        response.raise_for_status()
        data = response.json()

    return WeatherResponse(
        latitude=data["latitude"],
        longitude=data["longitude"],
        temperature=data["current"]["temperature_2m"],
        time=data["current"]["time"],
    )

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

if not GOOGLE_BOOKS_API_KEY :
    print("경고: GOOGLE_BOOKS_API_KEY가 설정되지 않았습니다.")

async def fetch_books(keyword:str, limit: int=5) -> list[GoogleBooks]:
    async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT) as client:
        response = await client.get("https://www.googleapis.com/books/v1/volumes/" , 
                                    params= {
                                        "q":keyword , "maxResults": limit,
                                        "key": GOOGLE_BOOKS_API_KEY,})
        data = response.json()

    result = []
    # GoogleBooks 생성
    for item in data.get('items',[]):
        book_info = item.get('volumeInfo',{}) # 책 1권 정보
        result.append(GoogleBooks(
                        title = book_info.get('title', "제목없음"),
                        authors = book_info.get('authors',[]), # authors 데이터가 리스트기 때문에 없을 때 [] << 공백 처리
                        published_date=book_info.get('publishedDate',"")

                    )
        )

    return result

import os

import httpx
from dotenv import load_dotenv

from schemas import ExternalBook, WeatherResponse

load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

if not GOOGLE_BOOKS_API_KEY:
    print("경고: GOOGLE_BOOKS_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")


async def fetch_books(keyword: str, limit: int = 5) -> list[ExternalBook]:
    async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT) as client:
        response = await client.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": keyword, "maxResults": limit, "key": GOOGLE_BOOKS_API_KEY},
        )
        response.raise_for_status()
        data = response.json()

    result = []
    for item in data.get("items", []):
        info = item.get("volumeInfo", {})
        result.append(
            ExternalBook(
                title=info.get("title", "제목 없음"),
                authors=info.get("authors", []),
                published_date=info.get("publishedDate", ""),
            )
        )
    return result

import json
from pathlib import Path

from schemas import ExternalBook


def load_fallback_books() -> list[ExternalBook]:
    path = Path(__file__).parent / "sample_books.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [ExternalBook(**item) for item in raw]

import asyncio


async def _fetch_titles(client: httpx.AsyncClient, keyword: str) -> dict:
    response = await client.get(
        "https://www.googleapis.com/books/v1/volumes",
        params={"q": keyword, "maxResults": 3, "key": GOOGLE_BOOKS_API_KEY},
    )
    data = response.json()
    titles = [
        item.get("volumeInfo", {}).get("title", "제목 없음")
        for item in data.get("items", [])
    ]
    return {"keyword": keyword, "titles": titles}


async def fetch_books_multi(keywords: list[str]) -> list[dict]:
    async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT * 2) as client:
        return await asyncio.gather(*[_fetch_titles(client, k) for k in keywords])

