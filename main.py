import openai
import base64
import time
import re
import json
import math
import os

from screen_shotter import window_capture
from mouse_controller import move_mouse, click_mouse, press_and_hold_mouse

# client = openai.OpenAI(api_key="anything", base_url="http://127.0.0.1:4000")
# model = "anthropic.claude-3-5-sonnet-20241022-v2:0"
client = openai.OpenAI(api_key=os.environ.get("ALIYUN_API_KEY"),
                       base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
model = "qwen-vl-max"

def find_topest_platform_position(bounding_boxes):
    topest_pos = 100000
    topest_idx = -1
    for bounding_box in bounding_boxes:
        if bounding_box["label"] != "platform":
            continue
        if bounding_box["bbox"][1] < topest_pos:
            topest_pos = bounding_box["bbox"][1]
            topest_idx = bounding_boxes.index(bounding_box)
    return bounding_boxes[topest_idx]["bbox"]

def get_pawn_position(bounding_boxes):
    for bounding_box in bounding_boxes:
        if bounding_box["label"] == "pawn":
            return bounding_box["bbox"]
    return None

def check_bounding_boxes(bounding_boxes):
    pawn_count = 0
    number_count = 0
    platform_count = 0
    topest_platform_y_position = 100000
    pawn_y_position = 0
    for bounding_box in bounding_boxes:
        if bounding_box["label"] == "number":
            number_count += 1
            if bounding_box["bbox"][0] < 100 or bounding_box["bbox"][0] > 130:
                return "Number is not in the upper left corner"
        if bounding_box["label"] == "pawn":
            pawn_count += 1
            pawn_y_position = bounding_box["bbox"][1]
        if bounding_box["label"] == "platform":
            if bounding_box["bbox"][1] < topest_platform_y_position:
                topest_platform_y_position = bounding_box["bbox"][1]
            platform_count += 1
            if bounding_box["bbox"][2] - bounding_box["bbox"][0] >  500 or bounding_box["bbox"][3] - bounding_box["bbox"][1] > 500:
                return "Platform is too large. Try to split it into smaller parts."
    if pawn_count != 1:
        return "Pawn count is not 1"
    if number_count != 1:
        return "Number count is not 1"
    if platform_count < 1:
        return "Platform count is less than 1"
    if topest_platform_y_position >= pawn_y_position - 5:
        return "Topest platform is below the pawn. There must be another platform on the upper left or upper right corner of the pawn. Please search carefully."
    return "Valid bounding boxes"

def get_distance(bbox1, bbox2):
    center1 = [(bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2]
    center2 = [(bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2]
    return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)

def get_bounding_boxes(encoded_image, additional_messages=None):
    messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/jpeg;base64," + encoded_image
                        },
                    },
                    {
                        "type": "text",
                        "text": "Detect all objects in the image and output the bbox coordinates in JSON format."
                        "Here is the instruction:"
                        "The output should be a list of objects, each object should contain the following information:"
                        "1. The bounding box of the object in the form of [x1, y1, x2, y2]."
                        "2. The label of the object. The label should be one of the following: pawn, number, platform"
                        "The number object always on the upper left corner of the image."
                        "There is only one pawn in the image."
                        "There is only one number in the image."
                        "Some object may be has similar color with the background, please search carefully."
                        "Do not output comments in json format."
                    },
                ]
    }]
    if additional_messages:
        for additional_message in additional_messages:
            print(additional_message)
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": additional_message
                        }
                    ]
                }
            )
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=messages,
    )
    text_response = response.choices[0].message.content
    print(text_response)
    try:
        json_response = re.search(r'```json(.*)```', text_response, re.DOTALL).group(1)
    except AttributeError:
        return None
    print(json_response)
    bounding_boxes = json.loads(json_response)
    return bounding_boxes

step_number = 0
while True:
    step_number += 1
    image_path = f"/path/to/screen_shot_dir/{step_number}.png"
    additional_messages = []
    while True:
        # Capture the iPhone screen
        window_capture(window_name="iPhone Mirroring", image_path=image_path)
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        bounding_boxes = get_bounding_boxes(encoded_image, additional_messages)
        print(f"Step {step_number}: {bounding_boxes}")
        check_result = check_bounding_boxes(bounding_boxes)
        if check_result == "Valid bounding boxes":
            break
        additional_messages.append(f"Your answer: {json.dumps(bounding_boxes)} is error. {check_result}")
        print("Invalid bounding boxes")
    topest_platform_position = find_topest_platform_position(bounding_boxes)
    print(f"Topest platform: {topest_platform_position}")

    pawn_position = get_pawn_position(bounding_boxes)
    print(f"Pawn position: {pawn_position}")

    distance = get_distance(pawn_position, topest_platform_position)
    print(f"Distance: {distance}")

    # Move mouse to the iPhone screen
    move_mouse(100, 100)
    # Transform the distance to the press and hold time
    press_and_hold_mouse(distance/700)
    time.sleep(3)