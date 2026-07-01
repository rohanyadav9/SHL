import requests
import time

from bs4 import BeautifulSoup

from storage import Storage
from agent import analyze

############################################################
# CONFIG
############################################################

storage = Storage()

URLS = [

    "https://www.shl.com/products/assessments/",

    "https://www.shl.com/products/assessments/behavioral-assessments/",

    "https://www.shl.com/products/assessments/behavioral-assessments/global-skills-assessment-gsa/",

    "https://www.shl.com/products/assessments/behavioral-assessments/universal-competency-framework/",

    "https://www.shl.com/products/assessments/behavioral-assessments/realistic-job-and-culture-previews-rjp/",

    "https://www.shl.com/products/assessments/behavioral-assessments/situation-judgement-tests-sjt/",

    "https://www.shl.com/products/assessments/assessment-and-development-centers/",

    "https://www.shl.com/products/assessments/personality-assessment/",

    "https://www.shl.com/products/assessments/personality-assessment/shl-occupational-personality-questionnaire-opq/",

    "https://www.shl.com/products/assessments/personality-assessment/shl-motivation-questionnaire-mq/",

    "https://www.shl.com/products/assessments/cognitive-assessments/",

    "https://www.shl.com/products/assessments/skills-and-simulations/",

    "https://www.shl.com/products/assessments/skills-and-simulations/technical-skills/",

    "https://www.shl.com/products/assessments/skills-and-simulations/coding-simulations/",

    "https://www.shl.com/products/assessments/skills-and-simulations/language-evaluation/",

    "https://www.shl.com/products/assessments/skills-and-simulations/call-center-simulations/",

    "https://www.shl.com/products/assessments/skills-and-simulations/business-skills/",

    "https://www.shl.com/products/assessments/job-focused-assessments/",

    "https://www.shl.com/solutions/talent-acquisition/volume-hiring/contact-center-hiring/",

    "https://www.shl.com/solutions/talent-acquisition/volume-hiring/retail-hiring/",

    "https://www.shl.com/solutions/talent-acquisition/volume-hiring/manufacturing-hiring/",

    "https://www.shl.com/solutions/talent-acquisition/graduate/",

    "https://www.shl.com/solutions/talent-acquisition/professional/",

    "https://www.shl.com/solutions/talent-acquisition/manager/"

]

############################################################
# BROWSER HEADERS
############################################################

headers = {

    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36",

    "Accept":
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/webp,*/*;q=0.8",

    "Accept-Language":
        "en-US,en;q=0.9",

    "Connection":
        "keep-alive",

    "Upgrade-Insecure-Requests":
        "1",

    "Referer":
        "https://www.shl.com/"

}

############################################################
# CLEAN HTML
############################################################


def clean_html(html):

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(

        [

            "script",

            "style",

            "svg",

            "noscript",

            "iframe"

        ]

    ):

        tag.decompose()

    return str(soup)

############################################################
# MAIN LOOP
############################################################

for index, url in enumerate(URLS):

    print()

    print("=" * 60)

    print(f"{index+1}/{len(URLS)}")

    print(url)

    if storage.is_completed(url):

        print("Already completed.")

        continue

    try:

        ####################################################
        # DOWNLOAD
        ####################################################

        response = requests.get(

            url,

            headers=headers,

            timeout=60

        )

        if response.status_code != 200:

            raise Exception(

                f"Status {response.status_code}"

            )

        ####################################################
        # CLEAN
        ####################################################

        html = clean_html(

            response.text

        )

        ####################################################
        # GEMINI
        ####################################################

        result = analyze(

            url,

            html

        )

        ####################################################
        # NORMALIZE
        ####################################################

        page = {

            "id":

                storage.get_next_id(),

            "url":

                url,

            "title":

                result["title"],

            "page_type":

                result["page_type"],

            "summary":

                result["summary"],

            "parent":

                result["parent"],

            "children":

                result["children"],

            "knowledge":

                result["knowledge"],

            "metadata":{

                "crawl_time":

                    time.strftime(

                        "%Y-%m-%d %H:%M:%S"

                    ),

                "model":

                    "gemini-2.5-flash",

                "status":

                    "success"

            }

        }

        ####################################################
        # SAVE
        ####################################################

        storage.save_page(page)

        storage.mark_completed(url)

        print("Saved.")

    except Exception as e:

        storage.mark_failed(

            url,

            str(e)

        )

        print(e)

print()

print(storage.stats())