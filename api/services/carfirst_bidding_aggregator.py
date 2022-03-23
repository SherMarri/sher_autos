from http.client import HTTPException
from datetime import datetime
import json
import os
from typing import Any, Dict, Text
import urllib.parse
from services.exceptions import AuctionRequestException
from utils.curl_util import exec_curl


class BiddingAggregator:
    """Calls Carfirst dealer API to aggregate bidding results."""

    def __init__(self) -> None:
        auth_token = os.environ.get("AUTH_TOKEN")
        if not auth_token:
            raise ValueError("AUTH_TOKEN not found in env vars.")
        self._current_auth_token = auth_token

    def fetch_upcoming_auctions(self):
        """Fetches upcoming auctions from Carfirst API."""
        try:
            job_id = self._generate_job_id(job_type="upcoming_auctions")
            filter = {}
            screen = "home-upcoming"
            segment = "home-upcoming"
            command = self._generate_curl_command(filter, segment, screen)
            response_body, status_code = exec_curl(command)
            if status_code != 200:
                raise HTTPException(
                    f"API request failed with response {response_body}."
                )
            self._store_response(job_id, response_body)
        except Exception as ex:
            raise AuctionRequestException(str(ex))

    def fetch_live_auctions(self):
        """Fetches live auctions from Carfirst API."""
        try:
            job_id = self._generate_job_id(job_type="live_auctions")
            filter = {"show_sold_cars": False}
            screen = "home-latest"
            segment = "home-latest"
            command = self._generate_curl_command(filter, segment, screen)
            response_body, status_code = exec_curl(command)
            if status_code != 200:
                raise HTTPException(
                    f"API request failed with response {response_body}."
                )
            self._store_response(job_id, response_body)
        except Exception as ex:
            raise AuctionRequestException(str(ex))

    def _generate_job_id(self, job_type: Text) -> str:
        timestamp = int(datetime.now().timestamp())
        job_id = f"{job_type}-{timestamp}"
        return job_id

    def _generate_curl_command(
        self, filter: Dict[Text, Any], segment: Text, screen: Text
    ) -> str:
        """Returns a curl command for the request."""
        filter_encoded = urllib.parse.quote(json.dumps(filter))
        referer_url = f"-H 'Referer: https://dealer.carfirst.com/auctions/{screen}?filter={filter_encoded}'"

        command = (
            (
                """curl 'https://dealer.carfirst.com/dealer-api/auctions\?filter=%%FILTER%%&order_by=start-desc&offset=0&segment=%%SEGMENT%%&screen=%%SCREEN%%&count=12' \
                -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0' \
                -H 'Accept: */*' \
                -H 'Accept-Language: en-US,en;q=0.5' \
                -H 'Accept-Encoding: gzip, deflate, br' \
                -H 'api-version: 119' \
                -H 'authorization: Bearer %%AUTH_TOKEN%%' \
                %%REFERER%% \
                -H 'client-language: en-PK' \
                -H 'client-platform: web' \
                -H 'client-version: 3.6' \
                -H 'config-version: 03f1692cc6d8a7b8a734b9b4eeb82335' \
                -H 'newrelic: eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjE1MTIwNjciLCJhcCI6IjE4MDEwMzcxNTgiLCJpZCI6ImRmM2RlNTVhMjlmZDhjMWQiLCJ0ciI6IjRhMmUwNWQ1OTEwMGM2ZGY0MGM3NTEyYzZlODUyNTMwIiwidGkiOjE2NDc5NDUyNDYyNzMsInRrIjoiMTcwNTIyMiJ9fQ==' \
                -H 'request-id: 6446cf39-4dc3-4692-aebb-ee8ef3200997' \
                -H 'traceparent: 00-4a2e05d59100c6df40c7512c6e852530-df3de55a29fd8c1d-01' \
                -H 'tracestate: 1705222@nr=0-1-1512067-1801037158-df3de55a29fd8c1d----1647945246273' \
                -H 'Connection: keep-alive' \
                -H 'Cookie: _ga=GA1.2.770926628.1633515534; __exponea_etc__=04e45ed1-7f79-4e14-9e17-9eda27be9539; lang=en-PK; onap=17fb039509cx2a9dbf5e-3-17fb0f9b691x4a299b97-67-1647947046; lqstatus=1647946041||||; laquesis=; laquesisff=; laquesissu=; WZRK_G=3f68036080724f6d88ec00dd60ae310f; session=eyJ0b2tlbiI6ImV5SmhiR2NpT2lKSVV6VXhNaUlzSW5SNWNDSTZJa3BYVkNKOS5leUpwWkNJNklqVmxOMkptWXpnMExUWmxZVGt0TkdKak55MDROREJrTFdRNE1tSXdaRE5qTnpVM1pTSXNJbVZ0WVdsc0lqb2ljMmhsY21GMWRHOXRiMkpwYkdVdGEyaHBJaXdpWTI5MWJuUnllU0k2SWxCTElpd2laM0p2ZFhCeklqcGJJbVJsWVd4bGNpNXdheUpkTENKdFlYaEJiVzkxYm5SQ2FXUnpJanB1ZFd4c0xDSnpkR0YwZFhNaU9pSmhZM1JwZG1VaUxDSmtaV0ZzWlhKRFlYUmxaMjl5ZVNJNmJuVnNiQ3dpWlhoMFpXNWtjeUk2ZTMwc0ltbGhkQ0k2TVRZME56a3lPVEF6T0N3aVpYaHdJam94TmpRNE5UTXpPRE00TENKcGMzTWlPaUpHY205dWRHbGxjaUJEWVhJZ1IzSnZkWEFpTENKemRXSWlPaUoxYzJWeUluMC5HR2hMSUFrQ1h6TnMtdjV0V05aVUxSTXdYSU9wVVJhWVhIVl9zbGxqTjJSYTJVd3FkRFAxMWMxd1NtVHQ5YkNGOHEwNFp4T3dvdWlJczZIWGtHSjVKdyIsInVzZXJJZCI6IjVlN2JmYzg0LTZlYTktNGJjNy04NDBkLWQ4MmIwZDNjNzU3ZSIsImVtYWlsIjoic2hlcmF1dG9tb2JpbGUta2hpIn0=; session.sig=yMZPdg7VDbkLNWJ981QfPO6aHUI; WZRK_S_696-588-KW6Z=%7B%22p%22%3A26%2C%22s%22%3A1647933264%2C%22t%22%3A1647945245%7D; ak_bmsc=E6F97B8A8646E9C50A823141D13F2313~000000000000000000000000000000~YAAQfDB7XESuo5x/AQAAkYotsQ/yXj1/utbkU+NpGyY0K56db8ScHaDgUDPogmhqMBBUoO3psTBZckAQIl9UvLP/SFK2NVUEHMpC++tF1AsXThAYBEilKabUA3RjNqxGuyf9LL8G6ylnOlUkX8XJ7CoVAYvxg2seiyhsCQH/zDv/QCPs43aCZriUMKgZbYkzFFOenzwOAxPvgrCSX7pvvoe+aady5M9929ySfdq8hLQGhYbo2jb06DBaPfOJGF9Cm9OWJxUjUfWFLZp79rCKAIFatlJ4mXlRbmvuPV/6McYRO4DZJH63WsFb+xokzPt/WdLr9FKL2mwc0dVOiHZ3Nh7DnHmo2akC9Glr1T3c5b/8bjHoJ3c15pH/WkOApOKagY4gygdkLfqln3RSYw==; bm_sv=A06B86624A903DCECD927E4D53E88B81~SHbZ6fLe8GBrt67K0UHaimrd0F/QyviaJuruCqRIB3BtQlk4kYUqG0Y1xU1u+Vqv5aBCsdW8d3ONq/wgKe+mQse1ydvH7u8RthfyLEwukLK1rla/nCVxzjIBgc0uXkHw3ann6iDgJnIeFK9L5xpwmBtGClNPZn6oDlSSxpK02ow=; mp_7ec2d8df0e608f341cf44d644223a5fb_mixpanel=%7B%22distinct_id%22%3A%20%225e7bfc84-6ea9-4bc7-840d-d82b0d3c757e%22%2C%22%24device_id%22%3A%20%2217fb0395b443cc-026d9121f64795-7f22675d-1fa400-17fb0395b457f5%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22%24user_id%22%3A%20%225e7bfc84-6ea9-4bc7-840d-d82b0d3c757e%22%7D' \
                -H 'Sec-Fetch-Dest: empty' \
                -H 'Sec-Fetch-Mode: cors' \
                -H 'Sec-Fetch-Site: same-origin' \
                -H 'Cache-Control: max-age=0' \
                --compressed \
                -H 'TE: trailers'"""
            )
            .replace("%%AUTH_TOKEN%%", self._current_auth_token)
            .replace("%%REFERER%%", referer_url)
            .replace(
                "%%FILTER%%",
                filter_encoded,
            )
            .replace(
                "%%SEGMENT%%",
                segment,
            )
            .replace(
                "%%SCREEN%%",
                screen,
            )
        )
        return command

    def _store_response(self, job_id: Text, data: Text):
        """Stores response based on the job_id in a json file."""
        json_data: Dict[Text, Any] = json.loads(data)
        if json_data.get("total") == 0:
            return
        with open(f"data/{job_id}.json", "w") as file:
            file.write(data)
