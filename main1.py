from fastapi import FastAPI
import asyncio
import time

app = FastAPI()

@app.get("/slow-async", tags= ["학습용"])
async def slow_async(): # async로 했을 때 얼마나 느려지는가(async 방식의 대기 시간 측정)
    await asyncio.sleep(3) #sec
    return {"type": "async", "message": "3초 대기 완료"}

@app.get("/slow-block", tags= ["학습용"])
async def slow_block(): # sync로 했을 때 얼마나 느려지는가(sync 방식의 대기 시간 측정)
    time.sleep(3)
    return {"type": "block", "message": "3초 대기 완료"}

