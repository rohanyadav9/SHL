import json
import os
from datetime import datetime


class Storage:

    def __init__(self):

        self.output_dir = "output"

        self.database_file = os.path.join(
            self.output_dir,
            "database.json"
        )

        self.progress_file = os.path.join(
            self.output_dir,
            "progress.json"
        )

        os.makedirs(self.output_dir, exist_ok=True)

        self.database = self.load_database()

        self.progress = self.load_progress()

    ############################################################
    # DATABASE
    ############################################################

    def load_database(self):

        if not os.path.exists(self.database_file):

            return {
                "pages": []
            }

        with open(self.database_file, "r", encoding="utf8") as f:

            return json.load(f)

    def save_database(self):

        with open(
            self.database_file,
            "w",
            encoding="utf8"
        ) as f:

            json.dump(
                self.database,
                f,
                indent=4,
                ensure_ascii=False
            )

    ############################################################
    # PROGRESS
    ############################################################

    def load_progress(self):

        if not os.path.exists(self.progress_file):

            return {

                "completed": [],

                "failed": []

            }

        with open(
            self.progress_file,
            "r",
            encoding="utf8"
        ) as f:

            return json.load(f)

    def save_progress(self):

        with open(
            self.progress_file,
            "w",
            encoding="utf8"
        ) as f:

            json.dump(
                self.progress,
                f,
                indent=4,
                ensure_ascii=False
            )

    ############################################################
    # CHECK IF URL ALREADY DONE
    ############################################################

    def is_completed(self, url):

        for item in self.progress["completed"]:

            if item["url"] == url:

                return True

        return False

    ############################################################
    # SAVE PAGE
    ############################################################

    def save_page(self, page):

        if self.page_exists(page["url"]):

            return

        self.database["pages"].append(page)

        self.save_database()

    ############################################################
    # PAGE EXISTS
    ############################################################

    def page_exists(self, url):

        for page in self.database["pages"]:

            if page["url"] == url:

                return True

        return False

    ############################################################
    # COMPLETE
    ############################################################

    def mark_completed(self, url):

        self.progress["completed"].append({

            "url": url,

            "status": "success",

            "time": datetime.now().isoformat()

        })

        self.save_progress()

    ############################################################
    # FAILED
    ############################################################

    def mark_failed(self, url, reason):

        self.progress["failed"].append({

            "url": url,

            "status": "failed",

            "reason": str(reason),

            "time": datetime.now().isoformat()

        })

        self.save_progress()

    ############################################################
    # GET NEXT ID
    ############################################################

    def get_next_id(self):

        return len(self.database["pages"]) + 1

    ############################################################
    # FIND PAGE
    ############################################################

    def find_page(self, url):

        for page in self.database["pages"]:

            if page["url"] == url:

                return page

        return None

    ############################################################
    # UPDATE HIERARCHY
    ############################################################

    def update_hierarchy(
        self,
        current_url,
        children
    ):

        page = self.find_page(current_url)

        if page is None:

            return

        page["children"] = children

        self.save_database()

    ############################################################
    # STATS
    ############################################################

    def stats(self):

        return {

            "pages":

                len(self.database["pages"]),

            "completed":

                len(self.progress["completed"]),

            "failed":

                len(self.progress["failed"])

        }