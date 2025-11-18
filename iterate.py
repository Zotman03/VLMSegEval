import os
from data_generation import generate_page

def generate_dataset(num_pages, out_dir):
    os.makedirs(f"{out_dir}/images", exist_ok=True)
    os.makedirs(f"{out_dir}/labels", exist_ok=True)

    for i in range(num_pages):
        img_path = f"{out_dir}/images/page_{i:05d}.png"
        json_path = f"{out_dir}/labels/page_{i:05d}.json"
        generate_page(img_path, json_path)
        print(f"{i + 1} documents generated")

generate_dataset(8000, "synthetic_dataset/train")
generate_dataset(1000, "synthetic_dataset/val")
generate_dataset(1000, "synthetic_dataset/test")
