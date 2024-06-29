import requests
import os
from PIL import Image
import re
from tqdm import tqdm
import json


class WikipediaAPI:
    def __init__(self, save_path="wikimedia", lang="is"):
        self.save_path = save_path
        self.train_path = f"{self.save_path}/train"
        self.val_path = f"{self.save_path}/val"
        self.lang = lang
        self.url = f"https://{lang}.wikipedia.org/w/api.php"

        self.init_dirs()

    def init_dirs(self):

        os.makedirs(self.save_path, exist_ok=True)
        os.makedirs(self.train_path, exist_ok=True)
        os.makedirs(self.val_path, exist_ok=True)

    def remove_markdown(self, text):
        if not text:
            return ""

        # Remove headers
        text = re.sub(
            r"^\s{0,3}(#{1,6})\s*(.*?)\s*#*\s*(\n|$)", r"\2\n", text, flags=re.MULTILINE
        )

        # Remove horizontal rules
        text = re.sub(r"^\s{0,3}([*\-=_] *){3,}\s*$", "", text, flags=re.MULTILINE)

        # Remove images
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

        # Remove links
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)

        # Remove emphasis (bold, italic, strikethrough)
        text = re.sub(r"(\*|_){1,3}([^*_]+?)\1{1,3}", r"\2", text)
        text = re.sub(r"~~(.*?)~~", r"\1", text)

        # Remove inline code
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # Remove blockquotes
        text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.MULTILINE)

        # Remove code blocks
        text = re.sub(r"```[a-z]*\n[\s\S]*?\n```", "", text)
        text = re.sub(r"`{3}[^`]*`{3}", "", text)

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Remove reference-style links
        text = re.sub(r"\[([^\]]+)\]\[[^\]]+\]", r"\1", text)
        text = re.sub(r"\[[^\]]+\]:\s*[^\s]+", "", text)

        return text.strip()

    def get_random_image(self, id=0, split=None):
        if split is None:
            split = self.train_path

        # Parameters for getting a random page
        params = {
            "format": "json",
            "action": "query",
            "generator": "random",
            "grnnamespace": 6,  # Namespace 6 is for files (images, media, etc.)
            "grnlimit": 1,
        }

        # Make the request to get a random image page
        response = requests.get(self.url, params=params)
        random_page = response.json()

        # Extract the page id
        page_id = next(iter(random_page["query"]["pages"]))

        # Get the image details
        params = {
            "format": "json",
            "action": "query",
            "prop": "imageinfo",
            "iiprop": "url|comment|canonicaltitle",
            "pageids": page_id,
        }

        # Make the request to get image details
        response = requests.get(self.url, params=params)
        image_details = response.json()

        url = image_details["query"]["pages"][page_id]["imageinfo"][0]["url"]
        description = image_details["query"]["pages"][page_id]["imageinfo"][0][
            "comment"
        ]
        filename = image_details["query"]["pages"][page_id]["imageinfo"][0][
            "canonicaltitle"
        ]

        # clean description
        pattern = r"\|\s*myndlýsing\s*=\s*(.*?)(?:\n|\|)"
        description = re.search(pattern, description, re.DOTALL)
        if match := description:
            description = match.group(1)

        filename = filename.split("/")[-1]
        filetypes = [".jpg", ".jpeg", ".png"]
        if not any(filetype in filename for filetype in filetypes) or not description:
            return self.get_random_image(id=id, split=split)

        # Download the image
        save_filename = f"{id}.{filename.split('.')[-1]}".replace("Mynd:", "")

        path = f"{split}/{save_filename}"

        os.system(f"wget -q -O {path} {url}")
        img_path = self.convert_to_jpg(img_path=path, id=id, save_path=split)

        # Save metadata
        metadata = {
            "file_name": img_path.split("/")[-1],
            "text": self.remove_markdown(description.replace("'", "").replace('"', "")),
        }

        self.save_metadata(split, str(metadata))

    def save_metadata(self, path, metadata):
        with open(f"{path}/metadata.jsonl", "a", encoding="utf-8") as f:
            jsonl = json.dumps(metadata, ensure_ascii=False)

            # jsonl hack
            jsonl = jsonl[1:-1]
            jsonl = jsonl.replace("'", '"')
            f.write(jsonl + "\n")

    def convert_to_jpg(self, img_path, id=0, save_path="."):
        save_path = f"{save_path}/{id}.jpg"
        # convert to jpg
        if img_path.split(".")[-1] != "jpg":
            img = Image.open(img_path)
            img = img.convert("RGB")
            img.save(save_path)
            os.remove(img_path)

        return save_path

    def get_n_random_images(self, n=10, split=None):
        for i in tqdm(range(n), desc="Downloading images"):
            if split is not None and i >= n * split:
                self.get_random_image(id=i)
            else:
                self.get_random_image(id=i, split=self.val_path)


if __name__ == "__main__":
    api = WikipediaAPI()
    for i in tqdm(range(20)):
        api.get_random_image(id=i)
