import asyncio
import time
import httpx

from fastapi import FastAPI,HTTPException,status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from external_api import fetch_weather, fetch_books, fetch_books_multi,load_fallback_books
from schemas import BookCreate, BookResponse, Publisher, WeatherResponse, GoogleBooks, ExternalBook



tags_metadata = [
    {"name": "도서", "description": "도서 등록, 조회, 검색"},
    {"name": "외부 연동", "description": "Google Books와 날씨 API 연동"},
    {"name": "시스템", "description": "서버 상태 확인"},
]



app = FastAPI(
    title="도서 관리 API 랄라라~~",
    description="""
도서를 등록·조회하고, 외부 서비스에서 도서 정보와 날씨를 가져오는 API입니다.

FastAPI 입문 과정 실습용으로 제작되었습니다.
""",
    version="1.0.0",
    contact={"name": "박서윤", "email": "bagppyun@gmail.com"},
)
app.mount("/static", StaticFiles(directory="static"), name="static")



books = [
 {"id": 1, "title": "파이썬 입문", "author": "김철수", "tags": ["초보자"], "year": 2021},
 {"id": 2, "title": "FastAPI 실전", "author": "이영희", "tags": ["초보자"],"year": 2023},
 {"id": 3, "title": "파이썬 웹개발", "author": "김철수", "tags": ["초보자"], "year": 2022},
 {"id": 4, "title": "데이터 분석 기초", "author": "박민수", "tags": ["초보자"], "year": 2020},
 {"id": 5, "title": "FastAPI로 배우는 백엔드", "author": "이영희", "tags": ["초보자"],"year": 2024},
 ]

@app.get("/", tags=["시스템"], summary="루트 조회")
def read_root():
    return {"message":"FastAPI 첫 서버"}


@app.get("/health", tags=["시스템"], summary="상태 확인")
def health():
    return {"status": "ok"}

@app.get("/info", tags=["시스템"], summary="정보 조회")
def info():
    return {"name": "도서 관리 API", "version": "0.1.0"}



# 도서의 목록을 제공하는 엔드포인트

@app.get("/books", response_model= list[BookResponse], tags=["도서"], summary="도서 목록 조회")
def list_books():
    return books


@app.get("/books/search", tags=["도서"], summary="도서 검색")
def search_books(keyword: str = ""): #search_books 라는 함수 정의 / keyword는 문자열 형태임
    if not keyword:
        return books
    return [b for b in books if keyword in b["title"]]


@app.get("/books/filter", tags=["도서"], summary="도서 필터링")
def filter_books(keyword: str = "", sort: str = ""):
    result = books
    # 리스트 컴프리헨션 - for + if > 리스트
    result = [b for b in result if b['author'] == keyword]

    if sort == "year":
        result = sorted(result, key = lambda b: b["year"])

    return result

@app.get("/books/page", tags=["도서"], summary="도서 페이징 조회")
def page_books(skip: int=0 , limit: int=2):
    return books[skip: skip+limit]


@app.get("/weather", response_model= WeatherResponse, tags=["외부 연동"], summary="날씨 조회")
async def weather(latitude: float= 36.8 , longitude: float = 127.1):
   return await fetch_weather(latitude,longitude)



from external_api import fetch_books, fetch_weather, load_fallback_books

@app.get(
    "/books/external",
    response_model=list[ExternalBook],
    tags=["외부 연동"],
    summary="Google Books 검색",
    response_description="검색된 도서 목록",
)
async def search_external_books(keyword: str, limit: int = 5, fallback: bool = False):
    """
    Google Books에서 도서를 검색합니다.

    - **keyword**: 검색어. 한국어도 가능합니다
    - **limit**: 가져올 개수. 기본 5
    - **fallback**: true이면 외부 API 실패 시 예비 데이터를 반환합니다

    외부 서비스에 의존하므로 502, 504가 발생할 수 있습니다.
    """
    try:
        return await fetch_books(keyword, limit)
    except httpx.TimeoutException:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.HTTPStatusError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
    except httpx.RequestError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")


@app.post("/books/from-external", response_model=BookResponse, status_code=201, tags=["도서"], summary="외부 도서 등록",
          responses={409: {"description": "이미 등록된 제목입니다"}})
def create_from_external(book: ExternalBook):
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")

    year = 2000
    if book.published_date[:4].isdigit():
        year = int(book.published_date[:4])

    new_id = max([b["id"] for b in books], default=0) + 1
    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.authors[0] if book.authors else "미상",
        "year": year,
        "tags": ["외부검색"],
        "publisher": None,
    }
    books.append(new_book)
    return new_book


# 항상 마지막
@app.get("/books/{book_id}",response_model=BookResponse,tags=["도서"], summary="도서 단건 조회",
    responses={404: {"description": "해당 번호의 도서를 찾을 수 없음"}},)

def read_book(book_id: int):
    for book in books:    # books에서 한 개씩 찾는다.
        if book["id"] == book_id:  # book_id가 == books에 들어있는 아이디와 같다면 (아이디가 다름 -> 무시라서 else가 안 필요하다)
            return book
    raise HTTPException(status_code=404, detail= "우리 책이 아니에요.")



@app.post("/books", 
          response_model = BookResponse, 
          status_code=status.HTTP_201_CREATED,
          tags=["도서"], summary="도서 등록",
          response_description= "등록된 도서 정보"
          )
def create_book(book: BookCreate):
    """
    새 도서를 내 목록에 등록합니다.

    - **title**: 1자 이상 100자 이하. 앞뒤 공백은 자동 제거됩니다
    - **author**: 1자 이상 50자 이하
    - **year**: 1900 이상 2100 이하
    - **tags**: 선택. 문자열 목록
    - **publisher**: 선택. 출판사 정보

    같은 제목이 이미 있으면 409를 반환합니다.
    """
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")
    new_id = max([ b["id"] for b in books ], default=0) +1
    # new_book = {"id":new_id, "title" : book.title, "author" : book.author, "year" : book.year}
    new_book = {"id":new_id,**book.model_dump()}
    books.append(new_book)

    return new_book