import asyncio
import os
from app.db.session import SessionLocal
from app.models.clipping import Clipping
from app.api.v1.endpoints.generate import process_clipping_task

async def run_test():
    db = SessionLocal()
    clipping = db.query(Clipping).first()
    if not clipping:
        print("No clipping found!")
        return
    print(f"Processing clipping: {clipping.id}")
    await process_clipping_task(clipping.id, db)
    db.refresh(clipping)
    print(f"Status: {clipping.status}")
    if clipping.status == "failed":
        print("Task failed!")
    else:
        print(f"Success! PNG: {clipping.png_url}, PDF: {clipping.pdf_url}")

if __name__ == "__main__":
    asyncio.run(run_test())
