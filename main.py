import requests
import random

def get_random_wikipedia_image(language='is'):
    # Define the URL for the Wikipedia API
    url = f"https://{language}.wikipedia.org/w/api.php"

    # Parameters for the API request
    params = {
        "action": "query",
        "format": "json",
        "list": "random",
        "grnnamespace": "6",  # Namespace for images
        "grnlimit": "1"  # Number of random images to retrieve
    }

    # Make the API request
    try:
        response = requests.get(url, params=params)
        random_page = response.json()

        page_id = next(iter(random_page['query']['pages']))

        params = {
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "iiprop": "url|comment|canonicaltitle",
            "pageids": page_id
        }

        response = requests.get(url, params=params)
        image_info = response.json()

        return image_info

    except requests.exceptions.RequestException as e:
        print("Error fetching random image:", e)
        return None

# Example usage:
random_image_url = get_random_wikipedia_image()
print(random_image_url)
