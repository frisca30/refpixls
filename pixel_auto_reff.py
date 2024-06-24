import aiohttp
import asyncio
from bs4 import BeautifulSoup
import random
import string
from datetime import datetime


def print_welcome_message():
    print(r"""
          
█     █ █  █ ▄▄▄▄▄ █  █ ▄▄▄▄▄
█ ▀ ▀ █ █  █ █ ▄▄█ █  █ █▄▄▄█
█  ▀  █ █▄▄█ █  ▄  █▄▄█ █
          """)
    print("Pixelverse Web Auto Register")
    print("Update Link: https://github.com/frisca30/")
    print("Update Link: https://github.com/frisca30/\n")
    print("Belikan saya kopi :) 0881 0260 1020 05 DANA\n\n")



headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json, text/plain, */*',
  'Authorization': '',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
  'Origin': 'https://dashboard.pixelverse.xyz',
  'Referer': 'https://dashboard.pixelverse.xyz/',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site':'same-site',
  'cache-control': 'no-cache'

}
async def randstr(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def function_get_link(session, email, domain):
    url = f"https://generator.email/{domain}/{email}"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "accept-encoding": "gzip, deflate, br",
        "cookie": f"_ga=GA1.2.659238676.1567004853; _gid=GA1.2.273162863.1569757277; embx=%5B%22{email}%40{domain}%22%2C%22hcycl%40nongzaa.tk%22%5D; _gat=1; io=io=tIcarRGNgwqgtn40O{await randstr(3)}; surl={domain}%2F{email}",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
    }
    attempts = 0
    max_attempts = 5
    while attempts < max_attempts:
        try:
            async with session.get(url, headers=headers, timeout=10) as response:  # Set a reasonable timeout
                if response.status == 200:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    src = soup.select_one('#email-table > div.e7m.row.list-group-item > div.e7m.col-md-12.ma1 > div.e7m.mess_bodiyy.plain > p')
                    if src is None:
                        print(f"\033[91m[{datetime.now().strftime('%H:%M:%S')}] No verification code found on attempt {attempts + 1}.\033[0m")
                        attempts += 1
                        await asyncio.sleep(2 ** attempts)  # Exponential backoff
                        continue
                    number = ''.join(filter(str.isdigit, src.text))
                    return number
                else:
                    print(f"\033[91m[{datetime.now().strftime('%H:%M:%S')}] HTTP error {response.status} on attempt {attempts + 1}.\033[0m")
                    attempts += 1
                    await asyncio.sleep(2 ** attempts)  # Exponential backoff
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Attempt {attempts + 1} failed: {str(e)}")
            attempts += 1
            await asyncio.sleep(2 ** attempts)  # Exponential backoff
    return None  # or raise an exception or handle as needed


async def make_request(session, url, payload, headers):
    async with session.post(url, json=payload, headers=headers) as response:
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            content = await response.json()
            if response.status == 429:
                print(f"\033[91m[{datetime.now().strftime('%H:%M:%S')}] Too many requests. Waiting for 20 seconds...")
                await asyncio.sleep(20)  # Delay for 1 minute
                return {'tokens': {'access': None}}  # Optionally retry or handle as needed
            if response.status == 400 and content.get('message') == 'Provided email has blacklisted domain':
                print(f"\033[91m[{datetime.now().strftime('%H:%M:%S')}] Email domain is blacklisted.")
                await asyncio.sleep(5)
                return {'tokens': {'access': None}}  # Handle specific error message
            return content  # Return the JSON content directly
        else:
            content = await response.text()
        
            return content # Return a dictionary with a None token if unexpected content type
        
async def register_user(session, email, domain, otp_payload, referral_payload, referral_url, i, domains):
    otp_response = await make_request(session, 'https://api.pixelverse.xyz/api/otp/request', otp_payload, headers)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Trying to register using email => {email}")

    otp = None
    start_time = datetime.now()
   
    while not otp and (datetime.now() - start_time).seconds < 30:
        print(f"\033[93m[{datetime.now().strftime('%H:%M:%S')}] Waiting for verification code...\033[0m")
        otp = await function_get_link(session, email.split('@')[0], domain)
        if otp:
            print(f"\033[92m[{datetime.now().strftime('%H:%M:%S')}] Verification code: {otp}\033[0m")
        else:
            print(f"\033[91m[{datetime.now().strftime('%H:%M:%S')}] No verification code found on attempt {(datetime.now() - start_time).seconds // 10 + 1}")

    if not otp:
        print(f"\033[91m[{datetime.now().strftime('%H:%M:%S')}] Failed to retrieve OTP. Skipping...")
        return False  # Return False to indicate failure

    access_token = await make_request(session, 'https://api.pixelverse.xyz/api/auth/otp', {'email': email, 'otpCode': otp}, headers)
    if access_token is None or access_token['tokens']['access'] is None:
        print(f"\033[91m[{datetime.now().strftime('%H:%M:%S')}] Failed to retrieve access token.")
        return False  # Return False to indicate failure

    # Ensure headers are properly set
    auth_headers = headers.copy()
    auth_headers['Authorization'] = f"Bearer {access_token['tokens']['access']}"

    referral_response = await session.put(referral_url, json=referral_payload, headers=auth_headers)
    if referral_response.status == 400 and 'blacklisted' in referral_response.text:
        print(f"\033[91m[{datetime.now().strftime('%H:%M:%S')}] Email domain is blacklisted. Trying a new domain...")
        domains.remove(domain)  # Remove the blacklisted domain from the list
        return False  # Indicate failure to handle blacklisted domain
    print(f"\033[92m[{datetime.now().strftime('%H:%M:%S')}] Sukses referral ke {i}\033[0m")
    return True  # Return True to indicate success

async def fetch_domains(session, url, maildom):
    domains = []
    for i in range(maildom):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Mengambil domain ({i+1}/{maildom})")
        async with session.get(url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            domain_elements = soup.select('div.tt-dataset-typeahead_as3gsdr p')
            for element in domain_elements:
                domain = element.get_text()
                if domain not in domains:
                    domains.append(domain)
        await asyncio.sleep(3)  # Delay 5 seconds between requests
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Total domain: {len(domains)}")
    return domains

async def main():
    successful_referrals = 0
    referral_code = input("Referral Code: ")
    jumlah = int(input("Number of Referrals: "))
    use_custom_domain = input("Use custom domain? (y/n): ")

    domains = []
    if use_custom_domain.lower() == 'y':
        custom_domains = input("Enter domain names separated by comma: ")
        domains = [domain.strip() for domain in custom_domains.split(',')]
    else:
        maildom = int(input("Number of Domains (default: 20): "))
        url = "https://generator.email/"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': None
        }
        async with aiohttp.ClientSession() as session:
            domains = await fetch_domains(session, url, maildom)

    async with aiohttp.ClientSession() as session:
        for i in range(1, jumlah + 1):
            while True:
                print(f"\033[93m[{datetime.now().strftime('%H:%M:%S')}] Mencoba daftar yang ke {i}\033[0m")
                if not domains:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No more domains available, program exit.")
                    return  # Exit the program if no domains are left
                domain = random.choice(domains)
                name = ''.join(random.choices(string.ascii_letters, k=5))
                email = f"{name}@{domain}"
                otp_payload = {'email': email}
                referral_payload = {'referralCode': referral_code}
                referral_url = f'https://api.pixelverse.xyz/api/referrals/set-referer/{referral_code}'

                success = await register_user(session, email, domain, otp_payload, referral_payload, referral_url, i, domains)
                if success:
                    successful_referrals += 1
                    break  # Break the loop if registration is successful
                else:
                    domains.remove(domain)  # Remove the blacklisted domain from the list
            
            await asyncio.sleep(5)
    print(f"\033[92m[{datetime.now().strftime('%H:%M:%S')}] Sukses ngereff total {successful_referrals}\033[0m")
print_welcome_message()
if __name__ == '__main__':
    asyncio.run(main())