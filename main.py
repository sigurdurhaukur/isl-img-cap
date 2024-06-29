from wikimedia import WikipediaAPI
from utils import get_paths, clear_dir
import pandas as pd
from datasets import load_dataset
from PIL import Image

api = WikipediaAPI()
clear_dir(api.save_path)
api.get_n_random_images(n=10, split=0.2)


dataset = load_dataset("imagefolder", data_dir=api.save_path)

