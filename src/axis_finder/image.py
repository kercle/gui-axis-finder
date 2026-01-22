import io
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image


class ImageMetadata:
    def __init__(self, path: Path, width: int, height: int):
        self.path = path
        self.width = width
        self.height = height


def list_images(img_dir: Path) -> list[ImageMetadata]:
    img_paths = []

    for path in img_dir.glob("*.jpg"):
        img_w, img_h = Image.open(path).size

        if img_paths:
            expected_w = img_paths[0].width
            expected_h = img_paths[0].height

            if img_w != expected_w or img_h != expected_h:
                print(f"Skipping image {path} due to size mismatch.")
                continue

        img_paths.append(ImageMetadata(path, img_w, img_h))

    return sorted(img_paths, key=lambda x: x.path.name)


def image_to_jpeg_bytes(image, quality=90):
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def load_cropped_image(
    img_path: Path,
    center: Tuple[int, int],
    crop_size: Tuple[int, int],
) -> np.ndarray:
    img_gray = np.array(Image.open(img_path).convert("L"), dtype=np.int16)

    crop_x_start = max(0, center[0] - crop_size[0] // 2)
    crop_x_end = min(img_gray.shape[1], center[0] + crop_size[0] // 2)
    crop_y_start = max(0, center[1] - crop_size[1] // 2)
    crop_y_end = min(img_gray.shape[0], center[1] + crop_size[1] // 2)

    img_gray = img_gray[
        crop_y_start:crop_y_end,
        crop_x_start:crop_x_end,
    ]

    return img_gray.astype(np.uint8)


def draw_images(
    img_a_path: Path,
    img_b_path: Path,
    center: Tuple[int, int],
    crop_size: Tuple[int, int],
    show_diff: bool = True,
    invert_colors: bool = False,
    color_map: str = "yellow-blue",
) -> Image.Image:
    img_a_gray = load_cropped_image(img_a_path, center, crop_size).astype(np.int16)
    if invert_colors:
        img_a_gray = 255 - img_a_gray

    if not show_diff:
        return image_to_jpeg_bytes(Image.fromarray(img_a_gray.astype(np.uint8)))

    img_b_gray = load_cropped_image(img_b_path, center, crop_size).astype(np.int16)
    if invert_colors:
        img_b_gray = 255 - img_b_gray

    img_diff = img_a_gray - img_b_gray[::, ::-1]

    if color_map == "yellow-blue":
        c1, c2, c3 = 2, 0, 1
    elif color_map == "red-cyan":
        c1, c2, c3 = 0, 1, 2
    elif color_map == "magenta-green":
        c1, c2, c3 = 1, 2, 0
    else:
        raise ValueError(f"Unknown color map: {color_map}")

    overlap_image = np.zeros((*img_a_gray.shape, 3), dtype=np.uint8)
    overlap_image[..., c1] = img_diff.clip(min=0)
    overlap_image[..., c2] = (-img_diff).clip(min=0)
    overlap_image[..., c3] = overlap_image[..., c2]

    return image_to_jpeg_bytes(Image.fromarray(overlap_image))
