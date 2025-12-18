# import livekit.agents
# print(dir(livekit.agents))

# @server.rtc_session()
# async def my_agent(ctx: JobContext):
#     metadata = json.loads(ctx.job.metadata)
#     user_id = metadata["user_id"]
#     user_name = metadata["user_name"]
#     user_phone = metadata["user_phone"]
#     user_address = metadata["user_address"]
#     print(f"User ID: {user_id}, User Name: {user_name}, User Phone: {user_phone}, User Address: {user_address}")
#     return "Hello, how can I help you today?"


import json
from livekit.agents import JobContext
from models import read_rows_from_sqlite

from livekit.plugins import (
    openai,
    elevenlabs,
    silero,
    deepgram,
    cartesia,
    turn_detector,
    noise_cancellation,
    groq,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit import agents
from livekit.agents import  Agent, ChatContext, AgentSession #, agentserver
from dotenv import load_dotenv
load_dotenv()

class Assistant(Agent):
    def __init__(self, chat_ctx: ChatContext) -> None:
        super().__init__(chat_ctx=chat_ctx, instructions="You are a helpful voice AI assistant.")

# server = AgentServer()

# @server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    # Simple lookup, but you could use a database or API here if needed
    rows = read_rows_from_sqlite("data/data.sqlite3")
    metadata = json.loads(rows[0])
    user_name = metadata["User_name"]
    print(f"User Name: {user_name}")

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"), 
        vad=silero.VAD.load(),
        #turn_detection=MultilingualModel(),  )
        #turn_detection=MultilingualModel(verbose=True),
        #noise_cancellation=noise_cancellation.BVC(),
    )

    initial_ctx = ChatContext()
    initial_ctx.add_message(role="assistant", content=f"The user's name is {user_name}.")

    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=initial_ctx),
        # ... room_options, etc.
    )

    await session.generate_reply(
        instructions=f"Greet the user by name and offer your assistance.{user_name}"
    )



if __name__ == "__main__":
    #server.run(my_agent)
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=my_agent,initialize_process_timeout=120.0 ))