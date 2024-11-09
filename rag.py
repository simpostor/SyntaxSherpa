from typing import List
from typing import Optional
import csv
import PyPDF2
from io import BytesIO
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
import os
from dotenv import load_dotenv
import chainlit as cl
import csv
from typing import Dict, Optional

from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import (
    ConversationalRetrievalChain,
)
#from langchain_community.llms import Ollama
from langchain.docstore.document import Document
from langchain_community.llms import Ollama

from langchain_community.chat_models import ChatOllama
from typing import Dict, Optional
from langchain.memory import ChatMessageHistory, ConversationBufferMemory

import chainlit as cl
import os
from dotenv import load_dotenv
import asyncio

# Define the inactivity timeout in seconds
INACTIVITY_TIMEOUT = 300  # 5 minutes

# Variable to track the last activity time
last_activity_time = 0                                  


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

@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    if provider_id == "google":
        user_email = raw_user_data.get("email", "")
        email_domain = user_email.split("@")[-1]

        if email_domain == "dypatil.edu":
            return default_user
    if provider_id == "github":
        user_email = raw_user_data.get("email", "")
        email_domain = user_email.split("@")[-1]

        if email_domain == "dypatil.edu":
            return default_user
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

    # Deny access for all other users
    return None
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

@cl.on_chat_start
async def on_chat_start():
    user = cl.user_session.get("user")
    chat_profile = cl.user_session.get("chat_profile")
    if chat_profile == "Sherpa Query":
        # System prompt for Sherpa Query chat profile
        system_prompt = "You are the Sherpa Query assistant. You give very concise answers to queries."
        
        # Entire processing logic for Sherpa Query
        files = None

        # Wait for the user to upload a file
        while files is None:
            files = await cl.AskFileMessage(
                content="Please upload framework documentation in pdf format to begin processing!",
                accept=["application/pdf"],
                max_size_mb=100,
                timeout=180,
            ).send()

        file = files[0]
        print(file)

        msg = cl.Message(content=f"Processing `{file.name}`...")
        await msg.send()

        # Read the PDF file
        pdf = PyPDF2.PdfReader(file.path)
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text()

        # Split the text into chunks
        texts = text_splitter.split_text(pdf_text)

        # Create a metadata for each chunk
        metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]

        # Create a Chroma vector store
        embeddings = OllamaEmbeddings(model="SyntaxSherpa")
        docsearch = await cl.make_async(Chroma.from_texts)(
            texts, embeddings, metadatas=metadatas
        )

        message_history = ChatMessageHistory()

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            chat_memory=message_history,
            return_messages=True,
        )

        # Create a chain that uses the Chroma vector store
        chain = ConversationalRetrievalChain.from_llm(
            ChatOllama(model="llama3"),
            chain_type="stuff",
            retriever=docsearch.as_retriever(),
            memory=memory,
            return_source_documents=True,
        )

        # Let the user know that the system is ready
        msg.content = f"`{file.name}` Processing done ask away your questions"
        await msg.update()

        cl.user_session.set("chain", chain)
 
    else:
        if chat_profile == "SyntaxSherpa":
            # System prompt for SyntaxSherpa chat profile
            await cl.Message(content="Welcome to Coding Assistant! My name is Syntax Sherpa and I'm here to help you with all your coding queries. Feel free to ask anything related to programming.").send()

            model = Ollama(model="SyntaxSherpa")
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "You are Syntax Sherpa, a coding AI that provides accurate, helpful responses to coding queries."),
                    MessagesPlaceholder(variable_name="history"),
                    ("human", "{question}"),
                ]
            )
            
            runnable = lambda chat_history: prompt | model | StrOutputParser()
            cl.user_session.set("runnable", runnable)


            system_prompt = "You are SyntaxSherpa, an AI coding copilot model. You give very concise answers to queries."
            
            # You can place the relevant processing code for SyntaxSherpa here if required in the future.



@cl.on_message
async def main(message: cl.Message):
    chat_profile = cl.user_session.get("chat_profile")
    
    if chat_profile == "Sherpa Query":
        chain = cl.user_session.get("chain")  # type: ConversationalRetrievalChain
        cb = cl.AsyncLangchainCallbackHandler()

        res = await chain.ainvoke(message.content, callbacks=[cb])
        answer = res["answer"]
        source_documents = res["source_documents"]  # type: List[Document]

        text_elements = []  # type: List[cl.Text]

        if source_documents:
            for source_idx, source_doc in enumerate(source_documents):
                source_name = f"source_{source_idx}"
                # Create the text element referenced in the message
                text_elements.append(
                    cl.Text(content=source_doc.page_content, name=source_name)
                )
            source_names = [text_el.name for text_el in text_elements]

            if source_names:
                answer += f"\nSources: {', '.join(source_names)}"
            else:
                answer += "\nNo sources found"

        await cl.Message(content=answer, elements=text_elements).send()
    else:
        runnable = cl.user_session.get("runnable")  # type: Runnable
        chat_history = cl.user_session.get("chat_history", [])  # Get chat history

        msg = cl.Message(content="")

        async for chunk in runnable(chat_history).astream(
            {"question": message.content, "history": chat_history},  # Pass chat history
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            await msg.stream_token(chunk)

        await msg.send()

        # Update chat history in user session
        chat_history.append({"role": "user", "content": message.content})
        cl.user_session.set("chat_history", chat_history)

@cl.set_chat_profiles
async def chat_profile():
    return [
        
        cl.ChatProfile(
            name="SyntaxSherpa",
            markdown_description="Coding Copilot",
            #icon="https://example.com/syntax_sherpa_icon.png",
        ),
        cl.ChatProfile(
            name="Sherpa Query",
            markdown_description="Framework Documentation Query",
            # icon="https://example.com/sherpa_ai_icon.png",
        ),
    ]