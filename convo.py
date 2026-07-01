import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


class ConversationManager:

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("API_KEY")
        )

        self.model = "gemini-2.5-flash"

        with open(
            "output/catalog_map.json",
            "r",
            encoding="utf8"
        ) as f:
            self.catalog = json.load(f)

        with open(
            "output/database.json",
            "r",
            encoding="utf8"
        ) as f:
            self.database = json.load(f)

        with open(
            "prompts/orchestrator.txt",
            "r",
            encoding="utf8"
        ) as f:
            self.system_prompt = f.read()

        with open(
            "prompts/responder.txt",
            "r",
            encoding="utf8"
        ) as f:
            self.responder_prompt = f.read()

        self.sessions = {}

    ##########################################################
    # SESSION
    ##########################################################

    def create_session(self):

        import uuid

        session_id = str(uuid.uuid4())

        self.sessions[session_id] = []

        return session_id

    ##########################################################

    def reset_session(self, session_id):

        if session_id in self.sessions:

            del self.sessions[session_id]

    ##########################################################

    def get_history(self, session_id):

        return self.sessions.get(session_id, [])

    ##########################################################

    def add_message(
        self,
        session_id,
        role,
        content
    ):

        self.sessions[session_id].append(

            {

                "role": role,

                "content": content

            }

        )

    ##########################################################
    # PROMPT
    ##########################################################

    def build_prompt(

        self,

        session_id,

        user_message

    ):

        history = self.get_history(session_id)

        prompt = self.system_prompt

        prompt += "\n\n"

        prompt += "=============================\n"
        prompt += "CATALOG MAP\n"
        prompt += "=============================\n\n"

        prompt += json.dumps(

            self.catalog,

            indent=2

        )

        prompt += "\n\n"

        prompt += "=============================\n"
        prompt += "CONVERSATION HISTORY\n"
        prompt += "=============================\n\n"

        for msg in history:

            prompt += f"{msg['role']}: {msg['content']}\n"

        prompt += "\n"

        prompt += "User: "

        prompt += user_message

        return prompt

    ##########################################################
    # GEMINI
    ##########################################################

    def ask_orchestrator(

        self,

        session_id,

        user_message

    ):

        prompt = self.build_prompt(

            session_id,

            user_message

        )

        response = self.client.models.generate_content(

            model=self.model,

            contents=prompt

        )

        text = response.text.strip()

        if text.startswith("```json"):

            text = text[7:]

        if text.endswith("```"):

            text = text[:-3]

        return json.loads(text)

    ##########################################################
    # CHAT
    ##########################################################
    
    def get_assessments(self,urls):

        pages=[]

        for url in urls:

            for page in self.database["pages"]:

                if page["url"]==url:

                    pages.append(page)

                    break

        return pages


    def ask_responder(self,session_id,pages):

        prompt=self.responder_prompt

        prompt+="\n\nConversation History\n\n"

        for msg in self.get_history(session_id):

            prompt+=f"{msg['role']}: {msg['content']}\n"

        prompt+="\nAssessment Pages\n\n"

        prompt+=json.dumps(
            pages,
            indent=2
        )

        response=self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        text=response.text.strip()

        if text.startswith("```json"):
            text=text[7:]

        if text.endswith("```"):
            text=text[:-3]

        return json.loads(text)
    

    def chat(self, session_id, user_message):

        if session_id not in self.sessions:

            self.sessions[session_id] = []

        self.add_message(
            session_id,
            "user",
            user_message
        )

        result = self.ask_orchestrator(
            session_id,
            user_message
        )

        if not result["ready"]:

            self.add_message(
                session_id,
                "assistant",
                result["question"]
            )

            return {
                "question": result["question"],
            }

        pages = self.get_assessments(
            [
                x["url"]
                for x in result["candidate_assessments"]
            ]
        )

        reply = self.ask_responder(
            session_id,
            pages
        )

        self.add_message(
            session_id,
            "assistant",
            reply["reply"]
        )

        return {
            "status": "ready",
            "message": reply["reply"]
        }