import requests
import time


def fetch_articles_newsapi(topic, num_articles, api_key):

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": topic,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": num_articles,
        "apiKey": api_key
    }

    headers = {
        "User-Agent": "NeuralDigest/1.0"
    }

    last_error = None

    # Try up to 3 times
    for attempt in range(3):

        try:

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=(10, 45)
            )

            if response.status_code != 200:
                raise Exception(
                    f"NewsAPI error: "
                    f"{response.status_code} - "
                    f"{response.text}"
                )

            data = response.json()

            if data.get("status") != "ok":
                raise Exception(
                    data.get(
                        "message",
                        "Unknown NewsAPI error"
                    )
                )

            return data.get("articles", [])

        except requests.exceptions.RequestException as e:

            last_error = e

            print(
                f"NewsAPI connection attempt "
                f"{attempt + 1}/3 failed: {e}"
            )

            if attempt < 2:
                time.sleep(2)

    raise Exception(
        f"Could not connect to NewsAPI after 3 attempts. "
        f"Last error: {last_error}"
    )