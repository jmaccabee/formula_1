from dateutil.parser import parse
from io import BytesIO
import os

import requests

from lxml.html import document_fromstring
import pandas as pd


def update_stats():
    YEARS = [
        2024,
        2023,
        2022,
        2021,
        2020,
    ]
    url_pattern = "https://www.formula1.com/en/results.html/{}/races.html"

    for year_ix, year in enumerate(YEARS):
        year_url = url_pattern.format(year)
        year_res = requests.get(
            year_url,
            headers={
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                # 'cookie': 'consentUUID=6c33b0b6-bfd6-4107-b8e7-2905370fcf4e_30; consentDate=2024-04-07T13:56:17.826Z; _gcl_au=1.1.1562481431.1712498178; minVersion={"experiment":785196033,"minFlavor":"Second Callmi-1.17.1.67.js100"}; minUnifiedSessionToken10=%7B%22sessionId%22%3A%22f8b4450a8b-b9904ca9b0-1c36ac7429-ad5718daaa-e07fcda82c%22%2C%22uid%22%3A%22469616b0d5-8712ee1920-b39cbf0994-f41f8b67a1-ae05159ec2%22%2C%22__sidts__%22%3A1712498397167%2C%22__uidts__%22%3A1712498397167%7D; ecos.dt=1712498402047',
                'pragma': 'no-cache',
                'referer': 'https://www.formula1.com/en/results.html/2024/races/1231',
                'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            },
        )
        year_dom = document_fromstring(year_res.content)
        parsed_race_urls = [
            f"https://formula1.com{url}" 
            for url in set(
                year_dom.xpath(
                    "//table[contains(@class, 'resultsarchive-table')]//a[contains(@href, 'race-result.html')]//@href"
            ))
        ]

        for race_ix, race_url in enumerate(parsed_race_urls):
            print("Fetching race:", race_url)
            race_id = race_url.split("/races/")[1].split("/")[0]
            race_res = requests.get(
                race_url,
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'en-US,en;q=0.9',
                    'cache-control': 'no-cache',
                    # 'cookie': 'consentUUID=6c33b0b6-bfd6-4107-b8e7-2905370fcf4e_30; consentDate=2024-04-07T13:56:17.826Z; _gcl_au=1.1.1562481431.1712498178; minVersion={"experiment":785196033,"minFlavor":"Second Callmi-1.17.1.67.js100"}; minUnifiedSessionToken10=%7B%22sessionId%22%3A%22f8b4450a8b-b9904ca9b0-1c36ac7429-ad5718daaa-e07fcda82c%22%2C%22uid%22%3A%22469616b0d5-8712ee1920-b39cbf0994-f41f8b67a1-ae05159ec2%22%2C%22__sidts__%22%3A1712498397167%2C%22__uidts__%22%3A1712498397167%7D; ecos.dt=1712498402047',
                    'pragma': 'no-cache',
                    'referer': 'https://www.formula1.com/en/results.html/2024/races/1231',
                    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                },
            )
            race_dom = document_fromstring(race_res.content)
            race_date = parse(' '.join(race_dom.xpath("//span[@class='full-date']//text()")))

            table = pd.read_html(BytesIO(race_res.content))[0]
            table["race_id"] = race_id
            table["race_date"] = race_date
            table["race_year"] = race_date.year
            
            target_file = "~/Desktop/f1_stats_v1.csv"
            write_header = ((year_ix + race_ix) == 0)
            table.drop(columns=[c for c in table.columns if "Unnamed" in c]).to_csv(
                target_file,
                mode="a",
                header=write_header,
                index=False,
            )
            

