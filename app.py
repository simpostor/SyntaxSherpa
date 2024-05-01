from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
import os
from dotenv import load_dotenv
import chainlit as cl
import csv
from typing import Dict, Optional

load_dotenv()  # Load environment variables from .env file

secret_key = os.getenv("CHAINLIT_AUTH_SECRET")


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    with open('users.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                # You may want to return the user's role or any other metadata
                return cl.User(identifier=username, metadata={"role": row['role'], "provider": "database"})
    return None

# @cl.oauth_callback
# def oauth_callback(
#     provider_id: str,
#     token: str,
#     raw_user_data: Dict[str, str],
#     default_user: cl.User,
# ) -> Optional[cl.User]:
#     # Check if the OAuth provider is Google
#     if provider_id == "google":
#         # Extract the user's email domain from the raw user data
#         user_email = raw_user_data.get("email", "")
#         email_domain = user_email.split("@")[-1]

#         # Check if the user's email domain matches the allowed domain
#         if email_domain == "dypatil.edu":
#             # Allow access for users with email domain "dypatil.edu"
#             return default_user

#     # Deny access for all other users
#     return None
    
@cl.on_chat_start
async def on_chat_start():
    model = Ollama(model="SyntaxSherpa")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a very knowledgeable AI Model which provides accurate and eloquent answers to all questions.",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
