import httpx

from schemas import WeatherResponse,GoogleBooks

async def fetch_weather(
    latitude: float,
    longitude: float,
) -> WeatherResponse:
    async with httpx.AsyncClient(timeout=5.0) as client:
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

import requests
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

if not GOOGLE_BOOKS_API_KEY :
    print("경고: GOOGLE_BOOKS_API_KEY가 설정되지 않았습니다.")

async def fetch_books(keyword:str, limit: int=5) -> list[GoogleBooks]:
    async with httpx.AsyncClient() as client:
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

