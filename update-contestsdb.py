import json
import uuid

from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from bs4 import BeautifulSoup


def fetch_atcoder_contests() -> list[dict]:

    URL = "https://atcoder.jp/contests"

    contests = []

    response = requests.get(URL)

    if response.ok:

        html = response.content.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find_all(id="contest-table-upcoming")[0].find_all("tr")

        for row in table[1:]:
            
            """
            >>> print(row)
            <tr>
            <td class="text-center"><a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20220827T2100&amp;p1=248" target="blank"><time class="fixtime fixtime-full">2022-08-27 21:00:00+0900</time></a></td>
            <td>
            <span aria-hidden="true" data-placement="top" data-toggle="tooltip" title="Algorithm">Ⓐ</span>
            <span class="user-blue">◉</span>
            <a href="/contests/abc266">AtCoder Beginner Contest 266</a>
            </td>
            <td class="text-center">01:40</td>
            <td class="text-center"> - 1999</td>
            </tr>
            """

            title = row.contents[3].contents[5].contents[0]
            url = f"https://atcoder.jp{row.contents[3].contents[5].get('href')}"
            start_time = datetime.strptime(row.contents[1].contents[0].contents[0].contents[0], "%Y-%m-%d %H:%M:%S%z").astimezone(ZoneInfo("Asia/Kolkata"))
            hours, minutes = map(int, row.contents[5].contents[0].split(":"))
            end_time = start_time + timedelta(minutes=minutes, hours=hours)
            duration = end_time - start_time

            contests.append({                
                "id": uuid.uuid4().hex,
                "platform": "AtCoder",
                "title": title,
                "url": url,
                "start_time": start_time.isoformat(),
                "duration": duration.seconds
            })

    return contests


def fetch_codechef_contests() -> list[dict]:

    URL = "https://www.codechef.com/api/list/contests/all"

    payload = {
        "sort_by": "START",
        "sorting_order": "asc",
    }

    contests = []

    response = requests.get(URL, params=payload)

    if response.ok:

        response = response.json()
        contests_data = response["present_contests"] + response["future_contests"]

        for data in contests_data:
            
            """
            >>> print(data)
            {
                'contest_code': 'START54', 
                'contest_name': 'Starters 54 (Rated for Div 2, 3 & 4)', 
                'contest_start_date': '31 Aug 2022  20:00:00', 
                'contest_end_date': '31 Aug 2022  23:00:00', 
                'contest_start_date_iso': '2022-08-31T20:00:00+05:30', 
                'contest_end_date_iso': '2022-08-31T23:00:00+05:30', 
                'contest_duration': '180', 
                'distinct_users': 0
            }
            """

            try:
                title = data["contest_name"]
                url   = f"https://www.codechef.com/{data['contest_code']}"
                start_time = datetime.fromisoformat(data["contest_start_date_iso"])
                end_time   = datetime.fromisoformat(data["contest_end_date_iso"])
                duration   = end_time - start_time
            except:
                continue

            contests.append({                
                "id": uuid.uuid4().hex,
                "platform": "CodeChef",
                "title": title,
                "url": url,
                "start_time": start_time.isoformat(),
                "duration": duration.seconds
            })

    return contests


def fetch_codeforces_contests() -> list[dict]:

    URL = "https://codeforces.com/api/contest.list"

    contests = []

    response = requests.get(URL)

    if response.ok:

        response = response.json()
        contests_data = response["result"]

        for data in contests_data:
            
            """
            >>> print(data)
            {
                'id': 1723, 
                'name': 'ICPC 2022 Online Challenge powered by HUAWEI - Problem 1', 
                'type': 'IOI', 
                'phase': 'BEFORE', 
                'frozen': False, 
                'durationSeconds': 1296000, 
                'startTimeSeconds': 1663200000, 
                'relativeTimeSeconds': -1747109
            }
            """

            title = data["name"]
            url   = f"https://codeforces.com/contests/{data['id']}"
            start_time = datetime.fromtimestamp(float(data["startTimeSeconds"]), tz=ZoneInfo("Asia/Kolkata"))
            end_time   = start_time + timedelta(seconds=float(data["durationSeconds"]))
            if end_time <= datetime.now(tz=ZoneInfo("Asia/Kolkata")): 
                continue # include ongoing and upcoming contests only                           
            duration   = end_time - start_time

            contests.append({                
                "id": uuid.uuid4().hex,
                "platform": "Codeforces",
                "title": title,
                "url": url,
                "start_time": start_time.isoformat(),
                "duration": duration.seconds
            })

    return contests


def fetch_geeksforgeeks_contests() -> list[dict]:

    URL = "https://practiceapi.geeksforgeeks.org/api/vr/events/"

    payload = {
        "type": "contest",
        "sub_type": "upcoming"
    }

    contests = []

    response = requests.get(URL, params=payload)

    if response.ok:

        response = response.json()
        contests_data = response["results"]["upcoming"]

        for data in contests_data:
            
            """
            >>> print(data)
            {
                'slug': 'interview-series-65', 
                'start_time': '2022-08-28T19:00:00', 
                'end_time': '2022-08-28T20:30:00', 
                'banner': {
                    'mobile_url': 'https://media.geeksforgeeks.org/img-practice/banner/interview-series-65-1661154000-mobile.png', 
                    'desktop_url': 'https://media.geeksforgeeks.org/img-practice/banner/interview-series-65-1661154005-desktop.png'
                }, 
                'name': 'Interview Series - 65', 
                'status': 'upcoming', 
                'time_diff': {
                    'days': 0, 
                    'hours': 4, 
                    'mins': 8, 
                    'secs': 13
                }, 
                'type': 3, 
                'date': 'August 28, 2022', 
                'time': '07:00 PM'
            }
            """

            title = data["name"]
            url   = f"https://practice.geeksforgeeks.org/contest/{data['slug']}"
            start_time = datetime.fromisoformat(data["start_time"]).astimezone(ZoneInfo("Asia/Kolkata"))
            end_time   = datetime.fromisoformat(data["end_time"]).astimezone(ZoneInfo("Asia/Kolkata"))
            duration   = end_time - start_time

            contests.append({                
                "id": uuid.uuid4().hex,
                "platform": "GeeksforGeeks",
                "title": title,
                "url": url,
                "start_time": start_time.isoformat(),
                "duration": duration.seconds
            })

    return contests


def fetch_leetcode_contests() -> list[dict]:

    URL  = "https://leetcode.com/graphql"

    body = """
    {
        allContests {
            title
            titleSlug
            startTime
            duration
        }
    }
    """

    contests = []

    response = requests.get(URL, json={"query" : body})

    if response.ok:

        response = response.json()
        contests_data = response["data"]["allContests"]
        
        for data in contests_data:

            """
            >>> print(data)
            {
                'title': 'Biweekly Contest 86',
                'titleSlug': 'biweekly-contest-94',
                'startTime': 1662215400, 
                'duration': 5400
            }
            """

            title = data["title"]
            url   = f"https://leetcode.com/contest/{data['titleSlug']}"
            start_time = datetime.fromtimestamp(int(data["startTime"])).astimezone(ZoneInfo("Asia/Kolkata"))
            end_time = start_time + timedelta(seconds=int(data["duration"]))
            if end_time <= datetime.now(tz=ZoneInfo("Asia/Kolkata")): 
                continue # include ongoing and upcoming contests only 
            duration = end_time - start_time

            contests.append({                
                "id": uuid.uuid4().hex,
                "platform": "LeetCode",
                "title": title,
                "url": url,
                "start_time": start_time.isoformat(),
                "duration": duration.seconds
            })

    return contests

contests = (
    fetch_atcoder_contests() + 
    fetch_codechef_contests() +
    fetch_codeforces_contests() +
    fetch_geeksforgeeks_contests() +
    fetch_leetcode_contests()
)

with (Path(__file__).parent / "contests").open("w") as f:
    json.dump(contests, f)

with (Path(__file__).parent / "contests.json").open("w") as f:
    json.dump(contests, f, indent=4)
