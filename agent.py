import json
import os

from dotenv import load_dotenv
from google import genai

############################################################
# LOAD ENV
############################################################

load_dotenv()

API_KEY = os.getenv("API_KEY")

if API_KEY is None:
    raise Exception("GEMINI_API_KEY not found")

MODEL = os.getenv("MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=API_KEY)

############################################################
# PROMPT
############################################################

PROMPT = """
You are building a structured knowledge database
for the SHL Assessment Catalog.

You will receive:

1. Current page URL.
2. Raw HTML of the page.

Your task is NOT to summarize the website.

Your task is to understand ONLY THIS PAGE.

Ignore:

- Navigation
- Header
- Footer
- Cookie banner
- Contact
- Login
- Careers
- Privacy
- Resources
- Unrelated SHL products

Return ONLY valid JSON.

Schema:

{
"title":"",
"page_type":"",
"summary":"",

"parent":"",

"children":[
{
"title":"",
"url":""
}
],

"knowledge":{

"overview":"",

"important_points":[

],

"features":[

],

"benefits":[

],

"faq":[
{
"question":"",
"answer":""
}
],

"metadata":{

"duration":"",
"remote_testing":"",
"adaptive":"",
"languages":"",
"job_levels":"",
"assessment_type":""

}

}

}

Rules:

page_type must be one of

category
assessment
landing_page
solution
other

Only include child pages that are genuine
sub-pages of the current page.

Ignore navigation duplicates.

Return ONLY JSON.

"""

############################################################
# JSON CLEANER
############################################################


def clean_json(text):

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    if text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()

############################################################
# VALIDATOR
############################################################


def validate(result):

    defaults = {

        "title": "",

        "page_type": "",

        "summary": "",

        "parent": "",

        "children": [],

        "knowledge": {

            "overview": "",

            "important_points": [],

            "features": [],

            "benefits": [],

            "faq": [],

            "metadata": {}

        }

    }

    for key in defaults:

        if key not in result:

            result[key] = defaults[key]

    if "knowledge" not in result:

        result["knowledge"] = defaults["knowledge"]

    return result

############################################################
# GEMINI
############################################################


def analyze(url, html):

    payload = f"""

CURRENT URL

{url}

========================

RAW HTML

{html[:150000]}

"""

    response = client.models.generate_content(

        model=MODEL,

        contents=[
            PROMPT,
            payload
        ]

    )

    answer = clean_json(response.text)

    try:

        data = json.loads(answer)

    except Exception:

        print(answer)

        raise Exception("Gemini returned invalid JSON")

    return validate(data)