from PIL import Image, ImageDraw, ImageFont
import random
import json

PAGE_W, PAGE_H = 1024, 1448
LEFT_MARGIN = 80
RIGHT_MARGIN = 80
TOP_MARGIN = 60
BLOCK_SPACING = 30
COLUMN_GAP = 40
SAFE_BOTTOM = PAGE_H - 120 # keep some space at bottom

FONTS = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Times.ttc",
    "/System/Library/Fonts/Avenir.ttc",
    "/Library/Fonts/Arial.ttf",
    "/Library/Fonts/Courier New.ttf"
] # random font for variety

CLASSES = { # classes we want to annotate
    "title": 1,
    "header": 2,
    "footer": 3,
    "text": 4,
}

JOURNAL_PREFIXES = [ # for headers
    "Journal of", "Proceedings of", "Transactions on",
    "International Journal of", "Annals of", "Foundations of",
    "Advances in", "Review of"
]

JOURNAL_TOPICS = [ # headers
    "Machine Learning", "Artificial Intelligence", "Neural Computation",
    "Information Theory", "Cognitive Systems", "Applied Statistics",
    "Computational Linguistics", "Pattern Recognition", "Data Science"
]

TITLE_TOPICS = [
    "Neural Networks", "Language Models", "Document Layout Analysis",
    "Vision Transformers", "Representation Learning",
    "Reinforcement Learning", "Data Augmentation",
    "Text Classification", "Image Segmentation", "Prompt Engineering"
]

TITLE_METHODS = [
    "Self-Supervision", "Contrastive Learning", "Transformer Models",
    "Few-Shot Learning", "Synthetic Data", "LoRA Adapters",
    "Multimodal Reasoning", "Uncertainty Estimation"
]

TITLE_ADJECTIVES = [
    "Robust", "Efficient", "Scalable", "Interpretable",
    "Generalizable", "Adaptive", "Lightweight"
]

TITLE_STRUCTURES = [
    "A Study on {topic} Using {method}",
    "{adj} {topic} for {method}",
    "{topic}: A {adj} Approach to {method}",
    "Learning {topic} with {method}",
    "Understanding {topic} Through {method}"
]

def random_title():
    pattern = random.choice(TITLE_STRUCTURES)
    return pattern.format(
        topic=random.choice(TITLE_TOPICS),
        method=random.choice(TITLE_METHODS),
        adj=random.choice(TITLE_ADJECTIVES),
    )


def random_journal_name():
    return f"{random.choice(JOURNAL_PREFIXES)} {random.choice(JOURNAL_TOPICS)}"

def random_footer_text(): # for footers
    choices = [
        f"Page {random.randint(1,40)}",
        f"doi:10.10{random.randint(10,99)}/{random.randint(1000,9999)}",
        f"Vol. {random.randint(1,20)}, No. {random.randint(1,12)}",
        f"ISSN {random.randint(1000,9999)}-{random.randint(1000,9999)}",
    ]
    return random.choice(choices)

def random_font(size):
    for _ in range(10):
        try:
            return ImageFont.truetype(random.choice(FONTS), size=size)
        except:
            continue
    return ImageFont.load_default()

def draw_wrapped_text(draw, x, y, max_w, text, font, line_spacing=5):
    words = text.split()
    lines = []
    current = []

    for w in words:
        current.append(w)
        test_line = " ".join(current)
        if draw.textlength(test_line, font=font) > max_w:
            current.pop()
            lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))

    cur_y = y
    for line in lines:
        draw.text((x, cur_y), line, font=font, fill="black")
        bbox = font.getbbox(line)
        cur_y += (bbox[3]-bbox[1]) + line_spacing

    height = cur_y - y
    return [x, y, max_w, height]


def draw_boxes(img, annotations):
    debug = img.copy()
    draw = ImageDraw.Draw(debug)
    for ann in annotations:
        x, y, w, h = ann["bbox"]
        cls_name = [k for k,v in CLASSES.items() if v==ann["class_id"]][0]
        draw.rectangle([x,y,x+w,y+h], outline="red", width=3)
        draw.text((x,y-12), cls_name, fill="red")
    return debug


def generate_page(out_img, out_json):

    img = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    draw = ImageDraw.Draw(img)
    annotations = []

    one_or_two_col = random.choice([1,2])

    cursor_y = TOP_MARGIN
    full_width = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN


    elements = ["title", "header", "text_blocks", "footer"]
    random.shuffle(elements)

    for elem in elements:
        if elem == "title":
            title_text = random_title()
            title_font = random_font(36)
            bbox = draw_wrapped_text(draw, LEFT_MARGIN, cursor_y, full_width, title_text, title_font)
            annotations.append({"class_id": CLASSES["title"], "bbox": bbox})
            cursor_y = bbox[1] + bbox[3] + BLOCK_SPACING

        if elem == "header":
            header_text = random_journal_name()
            header_font = random_font(22)
            bbox = draw_wrapped_text(draw, LEFT_MARGIN, cursor_y, full_width, header_text, header_font)
            annotations.append({"class_id": CLASSES["header"], "bbox": bbox})
            cursor_y = bbox[1] + bbox[3] + BLOCK_SPACING

        if elem == "text_blocks":
            PAR = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                   "Vestibulum accumsan, tortor vitae dictum sagittis, massa sem porta libero, "
                   "vitae blandit magna lacus non nisl. Praesent vel sapien non arcu facilisis volutpat. "
                   "Fusce id lorem et sapien auctor pellentesque. ")

            num_blocks = random.randint(3,5)

            if one_or_two_col == 1:
                # one column type
                for _ in range(num_blocks):
                    if cursor_y > SAFE_BOTTOM - 200:
                        break
                    block_text = " ".join([PAR]* random.randint(2,4))
                    font = random_font(22)
                    bbox = draw_wrapped_text(draw, LEFT_MARGIN, cursor_y, full_width, block_text, font)
                    annotations.append({"class_id": CLASSES["text"], "bbox": bbox})
                    cursor_y = bbox[1] + bbox[3] + BLOCK_SPACING

            else: # two column type
                col_w = (full_width - COLUMN_GAP) // 2
                left_y = cursor_y
                right_y = cursor_y
                for _ in range(num_blocks):
                    text = " ".join([PAR]*random.randint(2,3))
                    font = random_font(22)
                    target_col = random.choice(["L","R"])
                    if target_col == "L":
                        if left_y < SAFE_BOTTOM - 200:
                            bbox = draw_wrapped_text(draw, LEFT_MARGIN, left_y, col_w, text, font)
                            annotations.append({"class_id": CLASSES["text"], "bbox": bbox})
                            left_y = bbox[1] + bbox[3] + BLOCK_SPACING
                    else:
                        right_x = LEFT_MARGIN + col_w + COLUMN_GAP
                        if right_y < SAFE_BOTTOM - 200:
                            bbox = draw_wrapped_text(draw, right_x, right_y, col_w, text, font)
                            annotations.append({"class_id": CLASSES["text"], "bbox": bbox})
                            right_y = bbox[1] + bbox[3] + BLOCK_SPACING

                cursor_y = max(left_y, right_y)
        if elem == "footer":
            footer_text = random_footer_text()
            footer_font = random_font(20)
            if cursor_y > PAGE_H - 80:
                cursor_y = PAGE_H - 80
            bbox = draw_wrapped_text(draw, LEFT_MARGIN, cursor_y, full_width, footer_text, footer_font)
            annotations.append({"class_id": CLASSES["footer"], "bbox": bbox})
            cursor_y = bbox[1] + bbox[3] + BLOCK_SPACING

    img.save(out_img)

    debug_img = draw_boxes(img, annotations)
    debug_img.save(out_img.replace(".png","_debug.png"))

    with open(out_json, "w") as f:
        json.dump({
            "file_name": out_img,
            "width": PAGE_W,
            "height": PAGE_H,
            "annotations": annotations
        }, f, indent=2)

if __name__ == "__main__":
    generate_page("sample_page.png", "sample_page.json")
    print("Generated sample_page.png, sample_page_debug.png, sample_page.json")
