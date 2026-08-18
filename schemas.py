from pydantic import BaseModel, Field

class Publisher(BaseModel):
    name: str = Field(default="출판났네", min_length = 1, max_length= 100,
                    description="출판사명",
                    examples=["민음사"])
    city: str = Field(default="고양",
                    description="출판사 소재지",
                    examples=["파주"])


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100,
        description="도서 제목",
        examples=["처음 시작하는 FastAPI"])
    author: str = Field(min_length=1, max_length=50, 
        description="도서 저자",
        examples=["홍길동"])
    year: int = Field(ge=1900, le=2026, 
        description="출판 연도",
        examples=["2024"])
    tags: list[str] = Field(default_factory=list,
        description="도서 태그 목록",
        examples=["python","web"])
    publisher: Publisher | None = Field(default= None, description="출판사 정보")


    def strip_title(cls, v: str) -> str:
        v = v.strip()
        # 공백문자열 체크
        if not v:
            raise ValueError("제목은 공백일 수 없습니다")

        return v


class BookResponse(BookCreate):
    id: int


class WeatherResponse(BaseModel):
    latitude:float
    longitude:float
    temperature:float
    time: str

class GoogleBooks(BaseModel):
    title: str
    authors: list[str] = Field(default_factory= list)
    published_date: str = ""

class ExternalBook(BaseModel):
    title: str
    authors: list[str] = Field(default_factory=list)
    published_date: str = ""




