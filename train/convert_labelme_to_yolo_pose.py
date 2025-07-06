import json
import os
from glob import glob
from PIL import Image

keypoints_order = ['Nose', 'Left Eye', 'Right Eye', 'Left Ear', 'Right Ear',
                   'Left Shoulder', 'Right Shoulder', 'Left Elbow', 'Right Elbow',
                   'Left Wrist', 'Right Wrist']

label_map = {name: idx for idx, name in enumerate(keypoints_order)}

def convert_labelme_to_yolo(json_file, img_dir, out_dir):
    with open(json_file) as f:
        data = json.load(f)

    img_path = os.path.join(img_dir, os.path.basename(json_file).replace('.json', '.jpg'))
    if not os.path.exists(img_path):
        print(f"Image not found: {img_path}")
        return
    img = Image.open(img_path)
    W, H = img.size

    kpts = [(0.0, 0.0, 0) for _ in range(len(keypoints_order))]
    xs, ys = [], []

    for shape in data['shapes']:
        label = shape['label']
        if label not in label_map:
            continue
        x, y = shape['points'][0]
        xi = x / W
        yi = y / H
        kpts[label_map[label]] = (xi, yi, 2)
        xs.append(xi)
        ys.append(yi)

    if not xs or not ys:
        return

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min

    line = f"0 {x_center} {y_center} {width} {height} "
    for x, y, v in kpts:
        line += f"{x} {y} {v} "

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, os.path.basename(json_file).replace('.json', '.txt'))
    with open(out_path, 'w') as f:
        f.write(line.strip())

def convert_folder(json_dir, img_dir, out_dir):
    json_files = glob(os.path.join(json_dir, '*.json'))
    for jf in json_files:
        convert_labelme_to_yolo(jf, img_dir, out_dir)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_dir', required=True, help='Path to LabelMe JSON folder')
    parser.add_argument('--img_dir', required=True, help='Path to image folder')
    parser.add_argument('--out_dir', required=True, help='Path to save YOLO txt labels')
    args = parser.parse_args()
    convert_folder(args.json_dir, args.img_dir, args.out_dir)
