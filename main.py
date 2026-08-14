import asyncio
import time

from fastapi import FastAPI,HTTPException,status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from external_api import fetch_weather
from schemas import BookCreate, BookResponse, Publisher, WeatherResponse


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")

books = [
 {"id": 1, "title": "파이썬 입문", "author": "김철수", "year": 2021},
 {"id": 2, "title": "FastAPI 실전", "author": "이영희", "year": 2023},
 {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "year": 2022},
 {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "year": 2020},
 {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "year": 2024},
 ]

@app.get("/")
def read_root():
    return {"message":"FastAPI 첫 서버"}


@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/info")
def info():
    return {"name": "도서 관리 API", "version": "0.1.0"}

# 도서의 목록을 제공하는 엔드포인트

@app.get("/books")
def list_books():
    return books


@app.get("/books/search")

def search_books(keyword: str = ""): #search_books 라는 함수 정의 / keyword는 문자열 형태임
    if not keyword:
        return books
    return [b for b in books if keyword in b["title"]]


@app.get("/books/filter")

def filter_books(keyword: str = "", sort: str = ""):
    result = books
    # 리스트 컴프리헨션 - for + if > 리스트
    result = [b for b in result if b['author'] == keyword]

    if sort == "year":
        result = sorted(result, key = lambda b: b["year"])

    return result

@app.get("/books/page")
def page_books(skip: int=0 , limit: int=2):
    return books[skip: skip+limit]


@app.get("/weather", response_model= WeatherResponse)
async def weather(latitude: float= 36.8 , longitude: float = 127.1):
   return await fetch_weather(latitude,longitude)




# 항상 마지막
@app.get("/books/{book_id}")
def read_book(book_id: int):
    for book in books:    # books에서 한 개씩 찾는다.
        if book["id"] == book_id:  # book_id가 == books에 들어있는 아이디와 같다면 (아이디가 다름 -> 무시라서 else가 안 필요하다)
            return book
    return {"error": "not found"}



class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=10)
    author: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1900,le=2026)


class BookResponse(BookCreate):
    id: int


@app.post("/books", response_model = BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    new_id = max([ b["id"] for b in books ], default=0) +1
    # new_book = {"id":new_id, "title" : book.title, "author" : book.author, "year" : book.year}
    new_book = {"id":new_id,**book.model_dump()}
    books.append(new_book)

    return new_book


@app.get("/books", response_model=list[BookResponse])
def list_books():
    return books


# 1. 새로운 책 등록
# 2. 북 목록을 조회
# 3. 내가 등록한 책을 검색




