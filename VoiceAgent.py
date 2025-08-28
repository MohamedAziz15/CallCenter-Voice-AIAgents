import logging

from dotenv import load_dotenv

logger = logging.getLogger("dlai-agent")
logger.setLevel(logging.INFO)

from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, RoomInputOptions,WorkerOptions, jupyter

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
load_dotenv()


class Assistant(Agent):
    Drive_thru_prompt = """You are an AI created by Deepgram, working as a drive-thru order taker. Your responses will be spoken aloud through a voice interface. Keep all responses to 2-3 sentences maximum and always redirect the conversation towards taking the customer's order.

Here is the menu you will be working with:
• coffee - $3
• latte - $4
• french coffee - $3
• tea - $2
• water - $1


When interacting with a customer, follow these guidelines:
1. Greet the customer and ask for their order.
2. Listen to the customer's input.
3. Respond appropriately to the customer's input, always steering the conversation towards completing their order.
4. If the customer orders an item, confirm their selection and ask if they would like anything else.
5. If the customer asks a question not related to ordering, politely redirect them to the menu items.
6. Once the customer indicates they are finished ordering, repeat their complete order for confirmation.
7. After confirming the order, inform the customer that their order is confirmed and direct them to the pickup kiosk.

Remember to keep your responses concise and focused on taking the order. Do not engage in unrelated conversations or provide information beyond what's necessary for completing the order."""
    def __init__(self) -> None:
        super().__init__(instructions=Assistant.Drive_thru_prompt)

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=groq.LLM(model="llama3-8b-8192"),
        # llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    
    await session.start(
            room=ctx.room,
            agent=Assistant(),
            room_input_options=RoomInputOptions(
                # LiveKit Cloud enhanced noise cancellation
                # - If self-hosting, omit this parameter
                # - For telephony applications, use `BVCTelephony` for best results
                noise_cancellation=noise_cancellation.BVC(), 
            ),
        )

    await ctx.connect()

    await session.generate_reply(
            instructions=Assistant.Drive_thru_prompt
            #instructions="Greet the user and offer your assistance."
        )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
