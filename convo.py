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


        self.sessions = {}

    ##########################################################
    # SESSION
    ##########################################################

    def create_session(self):

        import uuid

        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {

            "messages": [],

            "mode": "discovery",

            "selected_assessments": [],

            "family": None

        }

        return session_id

    ##########################################################

    def reset_session(self, session_id):

        if session_id in self.sessions:

            del self.sessions[session_id]

    ##########################################################

    def get_history(self, session_id):

        return self.sessions[session_id]["messages"]

    ##########################################################

    def add_message(
        self,
        session_id,
        role,
        content
    ):

        self.sessions[session_id]["messages"].append({

            "role": role,

            "content": content

        })

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
    def chat(self,session_id,user_message):

        if session_id not in self.sessions:

            self.sessions[session_id] = {

                "messages": [],

                "mode": "discovery",

                "selected_assessments": [],

                "family": None

            }

        state=self.sessions[session_id]

        self.add_message(
            session_id,
            "user",
            user_message
        )

    ##################################################
    # DISCOVERY MODE
    ##################################################

        if state["mode"]=="discovery":

            result=self.ask_orchestrator(
                session_id,
                user_message
            )

            if not result["ready"]:

                self.add_message(
                    session_id,
                    "assistant",
                    result["question"]
                )

                return{
                    "status":"clarify",
                    "message":result["question"]
                }

            state["mode"]="consultation"

            state["family"]=result["family"]

            state["selected_assessments"]=result["candidate_assessments"]

            self.add_message(
                session_id,
                "assistant",
                result["reply"]
            )

            return{
                "status":"ready",
                "message":result["reply"]
            }

    ##################################################
    # CONSULTATION MODE
    ##################################################

        return self.consultation_chat(
            session_id,
            user_message
    )

    def consultation_chat(self,session_id,user_message):

        state=self.sessions[session_id]

        prompt="""

            You are an SHL Recruitment Consultant.

            The user has already received an assessment recommendation.

            Continue the conversation naturally.

            Answer follow-up questions.

            Do not restart the interview.

            Do not ask clarification questions again unless the user completely changes the hiring requirement.

            Selected Assessment Family:

        """

        prompt+=state["family"]

        pages=[]

        for assessment in state["selected_assessments"]:

            url=assessment["url"]

            for page in self.database["pages"]:

                if page["url"]==url:

                    pages.append(page)

                    break

        prompt+="\n\nAssessment Details\n\n"

        prompt+=json.dumps(
            pages,
            indent=2
        )

        prompt+="\n\nConversation\n\n"

        for msg in state["messages"]:

            prompt+=f"{msg['role']}: {msg['content']}\n"

        response=self.client.models.generate_content(

            model=self.model,

            contents=prompt

        )

        answer=response.text.strip()

        self.add_message(
            session_id,
            "assistant",
            answer
        )

        return{

            "status":"ready",

            "message":answer

        }