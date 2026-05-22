import requests
import sqlite3
import time

def test_clipping_flow():
    base_url = "https://mohitroyal-newsflow-backend.hf.space/api/v1"
    
    # 1. Login
    print("1. Logging in...")
    login_payload = {
        "email": "mohithroyal16450@gmail.com",
        "password": "password123"
    }
    response = requests.post(f"{base_url}/auth/login", json=login_payload)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
        
    token = response.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Trigger Clipping Generation
    print("2. Triggering clipping generation on template 'rti_express'...")
    generation_payload = {
        "headline": "Scope Resolution Verification",
        "articleContent": "Python's global variable shadow scopes have been successfully resolved and tested.",
        "language": "en",
        "tone": "formal",
        "templateId": "rti_express",
        "publicationName": "NewsCraft Technical",
        "publicationDate": "Wednesday, May 20, 2026",
        "layoutColumns": 3,
        "fontFamily": "playfair"
    }
    
    gen_res = requests.post(f"{base_url}/generate/", json=generation_payload, headers=headers)
    if gen_res.status_code != 200:
        print(f"Generation request failed: {gen_res.text}")
        return
        
    clipping_data = gen_res.json()["data"]
    clipping_id = clipping_data["id"]
    print(f"Generation started successfully. Clipping ID: {clipping_id}")
    
    # 3. Poll Database for Status
    print("3. Polling database for background task status...")
    conn = sqlite3.connect('newscraft.db')
    cursor = conn.cursor()
    
    max_attempts = 15
    for attempt in range(1, max_attempts + 1):
        cursor.execute("SELECT status, png_url, pdf_url FROM clippings WHERE id = ?", (clipping_id.replace("-", ""),))
        row = cursor.fetchone()
        
        # If not found by raw hex UUID, try with hyphenated UUID
        if not row:
            cursor.execute("SELECT status, png_url, pdf_url FROM clippings WHERE id = ?", (clipping_id,))
            row = cursor.fetchone()
            
        if row:
            status, png, pdf = row
            print(f"Attempt {attempt}/{max_attempts}: Status is '{status}'")
            if status == "completed":
                print("==============================================")
                print("SUCCESS! Background generation completed successfully!")
                print(f"PNG URL: {png}")
                print(f"PDF URL: {pdf}")
                print("==============================================")
                conn.close()
                return
            elif status == "failed":
                print("FAILED! Background task failed.")
                conn.close()
                return
        else:
            print(f"Attempt {attempt}/{max_attempts}: Clipping not found in DB yet.")
            
        time.sleep(2)
        
    print("Timeout: Background task took too long.")
    conn.close()

if __name__ == '__main__':
    test_clipping_flow()
