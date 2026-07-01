import json
import os

from dotenv import load_dotenv
from google import genai

###########################################################
# CONFIG
###########################################################

load_dotenv()

client = genai.Client(
    api_key=os.getenv("API_KEY")
)

MODEL = "gemini-2.5-flash"

DATABASE = "output/database.json"

OUTPUT = "output/catalog_map.json"

###########################################################
# LOAD DATABASE
###########################################################

with open(DATABASE, "r", encoding="utf8") as f:
    database = json.load(f)

pages = database["pages"]

###########################################################
# FIND FAMILY PAGES
###########################################################

family_pages = []

for page in pages:

    if page["page_type"] == "category":

        family_pages.append(page)

###########################################################
# PROMPT
###########################################################

PROMPT = """
You are building the navigation brain for an AI Recruitment Consultant.

The final users DO NOT know SHL terminology.

They think in business problems.

For every assessment family produce ONLY a small amount
of knowledge that helps the Conversation Manager decide
whether this family is relevant.

DO NOT explain assessments.

DO NOT explain products.

DO NOT copy paragraphs.

Return JSON ONLY.

Schema

{

"name":"",

"summary":"",

"business_problems":[

],

"typical_roles":[

],

"clarification_questions":[

],

"children":[

{
"title":"",
"url":""
}

]

}

Rules

summary:
Maximum 2 sentences.

business_problems:
Business language only.

Examples

teamwork

leadership

software hiring

graduate hiring

coding ability

communication

NOT

behavioral assessment

personality assessment

typical_roles:

Examples

Software Engineer

Graduate

Sales Executive

Customer Support

clarification_questions

Maximum 5

Only questions that help narrow
the user's hiring requirement.

Children should contain only title and url.

Return JSON only.
"""

###########################################################
# BUILD
###########################################################

catalog = {

    "families":[

    ]

}

for page in family_pages:

    print()

    print("Building")

    print(page["title"])

    payload = {

        "title":page["title"],

        "summary":page["summary"],

        "knowledge":page["knowledge"],

        "children":page["children"]

    }

    response = client.models.generate_content(

        model=MODEL,

        contents=[
            PROMPT,
            json.dumps(payload,indent=2)
        ]

    )

    text = response.text.strip()

    if text.startswith("```json"):
        text=text[7:]

    if text.endswith("```"):
        text=text[:-3]

    catalog["families"].append(

        json.loads(text)

    )

###########################################################
# SAVE
###########################################################

with open(

    OUTPUT,

    "w",

    encoding="utf8"

) as f:

    json.dump(

        catalog,

        f,

        indent=4,

        ensure_ascii=False

    )

print()

print("Done.")

print("Families:",len(catalog["families"]))