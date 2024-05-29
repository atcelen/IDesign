import base64
import requests
import json
import numpy as np
import re
import argparse


# TODO : OpenAI API Key
api_key = "YOUR_API_KEY"

# TODO : Path to your image
image_path_1 = "FIRST_IMAGE_PATH.png"
image_path_2 = "SECOND_IMAGE_PATH.png"

# TODO : User preference Text
user_preference = "USER_PREFERNCE_TEXT"

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

example_json ="""
{
  "realism_and_3d_geometric_consistency": {
    "grade": 8,
    "comment": "The renders appear to have appropriate 3D geometry and lighting that is fairly consistent with real-world expectations. The proportions and perspective look realistic."
  },
  "functionality_and_activity_based_alignment": {
    "grade": 7,
    "comment": "The room includes a workspace, sleeping area, and living area as per the user preference. The L-shaped couch facing the bed partially meets the requirement for watching TV comfortably. However, there does not appear to be a TV depicted in the render, so it's not entirely clear if the functionality for TV watching is fully supported."
  },
  "layout_and_furniture": {
    "grade": 7,
    "comment": "The room has a bed that’s not centered and with space at the foot, and a large desk with a chair. However, it's unclear if the height of the bed meets the user's preference, and the layout does not clearly show the full-length mirror in relation to the wardrobe, so its placement in accordance to user preferences is uncertain."
  },
  "color_scheme_and_material_choices": {
    "grade": 9,
    "comment": "The room adheres to a light color scheme with blue and white tones as preferred by the user, without a nautical feel. The bed and other furniture choices are aligned with the color scheme specified."
  },
  "overall_aesthetic_and_atmosphere": {
    "grade": 8,
    "comment": "The room's general aesthetic is bright, clean, and relatively minimalistic, which could align with the user's preference for a light color scheme and a modern look. The chandelier is present as opposed to bright, hospital-like lighting."
  }
}
"""

# Getting the base64 string
base64_image_1 = encode_image(image_path_1)
base64_image_2 = encode_image(image_path_2)


headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": f"""
          Give a grade from 1 to 10 or unknown to the following room renders based on how well they correspond together to the user preference (in triple backquotes) in the following aspects: 
          - Realism and 3D Geometric Consistency
          - Functionality and Activity-based Alignment
          - Layout and furniture  
          - Color Scheme and Material Choices
          - Overall Aesthetic and Atmosphere         
          User Preference:
          ```{user_preference}```
          Return the results in the following JSON format:
          ```json
          {example_json}
          ```
          """
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image_1}"
          }
        },
        {
          "type": "image_url",
          "image_url": {
            "url" : f"data:image/jpeg;base64,{base64_image_2}"
          }
        }
      ]
    }
  ],
  "max_tokens": 1024
}
grades = {
   "realism_and_3d_geometric_consistency": [],
   "functionality_and_activity_based_alignment": [],
   "layout_and_furniture": [],
   "color_scheme_and_material_choices": [],
   "overall_aesthetic_and_atmosphere": []
}
for _ in range(3):
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    grading_str = response.json()["choices"][0]["message"]["content"]
    print(grading_str)
    print("-" * 50)
    pattern = r'```json(.*?)```'
    matches = re.findall(pattern, grading_str, re.DOTALL)
    json_content = matches[0].strip() if matches else None
    if json_content is None:
        grading = json.loads(grading_str)
    else:
        grading = json.loads(json_content)
    for key in grades:
        grades[key].append(grading[key]["grade"])
#Save the mean and std of the grades
for key in grades:
    grades[key] = {"mean": round(sum(grades[key])/len(grades[key]), 2), "std": round(np.std(grades[key]), 2)}
#Save the grades
with open(f"{'_'.join(image_path_1.split('_')[:-1])}_grades.json", "w") as f:
    json.dump(grades, f)     
