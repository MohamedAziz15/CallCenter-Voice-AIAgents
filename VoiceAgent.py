import logging
import asyncio
from dotenv import load_dotenv

logger = logging.getLogger("dlai-agent")
logger.setLevel(logging.INFO)

from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, RoomInputOptions,WorkerOptions, jupyter#,inference 

from livekit.plugins import (
    openai,
    elevenlabs,
    silero,
    deepgram,
    cartesia,
    turn_detector,
    noise_cancellation,
    groq,
    google,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
load_dotenv()

from livekit_plugins_googlesr import GoogleSTT

class Assistant(Agent):
    Arabic_Drive_thru_prompt = """
أنت مساعد ذكاء اصطناعي تم إنشاؤك بواسطة Deepgram وتعمل كموظف طلبات في خدمة السيارات (Drive-Thru). 
يتم نطق إجاباتك بصوت بشري باستخدام اللغة العربية. 
اجعل جميع ردودك قصيرة لا تتجاوز 2 إلى 3 جمل، ووجّه المحادثة دائمًا نحو أخذ طلب العميل.

قائمة المشروبات التي تعمل بها:
• قهوة - 3 دولارات
• لاتيه - 4 دولارات
• قهوة فرنسية - 3 دولارات
• شاي - 2 دولار
• ماء - 1 دولار

عند التفاعل مع العميل، اتبع الإرشادات التالية:
1. رحّب بالعميل واطلب منه تحديد طلبه.
2. استمع جيدًا إلى ما يقوله العميل.
3. رد بطريقة مناسبة، مع توجيه الحديث دائمًا نحو إكمال عملية الطلب.
4. إذا طلب العميل أحد المنتجات، أكد طلبه واسأله إن كان يرغب في شيء آخر.
5. إذا طرح العميل سؤالًا غير متعلق بالطلبات، وجّهه بلطف إلى قائمة المشروبات المتاحة.
6. عندما يُشير العميل إلى أنه انتهى من الطلب، أعد ذكر الطلب بالكامل للتأكيد.
7. بعد تأكيد الطلب، أخبر العميل أن طلبه قد تم تأكيده، ووجّهه إلى نافذة الاستلام.

تذكّر أن تكون إجاباتك مختصرة ومركّزة على عملية الطلب فقط. 
لا تدخل في محادثات جانبية أو مواضيع غير ضرورية لإتمام الطلب.
"""

    Drive_thru_prompt = """You are an AI created by Deepgram, working as a drive-thru order taker. Your responses will be spoken aloud through a voice  using arabic language. Keep all responses to 2-3 sentences maximum and always redirect the conversation towards taking the customer's order.

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
        super().__init__(instructions=Assistant.Arabic_Drive_thru_prompt)

async def entrypoint(ctx: agents.JobContext):

    session = AgentSession(
        # stt=deepgram.STT(model="nova-3", language="multi"),
        
        # llm=groq.LLM(model="llama3-8b-8192"),
        # # llm=openai.LLM(model="gpt-4o-mini"),
        # tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
        # tts=elevenlabs.TTS(
        # model="elevenlabs/eleven_turbo_v2_5", 
        # #voice="Xb7hH8MSUJpSbSDYk0k2", 
        # language="ar"),


        stt=GoogleSTT(language="ar-EG"),
        #llm=google.LLM(model="google/gemini-2.5-flash-lite"),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        #Fast as inference is done on the client side but egyption arabic is not well supported.
        #tts=elevenlabs.TTS(model="eleven_flash_v2_5", language="ar"),
        #Very slow as inference is done on the server side but egyption arabic is better.
        tts = google.beta.GeminiTTS(
                                    model="gemini-2.5-flash-preview-tts",
                                    voice_name="Charon",  
                                    instructions="Speak in a friendly and engaging tone in Egyption arabic language.",
                                                                 ),
        vad=silero.VAD.load(),
        # turn_detection=MultilingualModel(),  # Disabled: EOU model doesn't support ar-EG
    )
    
    await session.start(
            room=ctx.room,
            agent=Assistant(),
            # room_input_options=RoomInputOptions(
            #     # LiveKit Cloud enhanced noise cancellation
            #     # - If self-hosting, omit this parameter
            #     # - For telephony applications, use `BVCTelephony` for best results
            #     noise_cancellation=noise_cancellation.BVC(), 
            # ),
        )

    await ctx.connect()

    await session.generate_reply(
            instructions=Assistant.Arabic_Drive_thru_prompt
        )

if __name__ == "__main__":
    # Configure WorkerOptions with increased timeout for model initialization
    # initialize_process_timeout: Time in seconds to wait for process initialization
    # Increased to 120 seconds to allow VAD and turn detection models to download/load
    worker_options = agents.WorkerOptions(
       entrypoint_fnc=entrypoint,
       initialize_process_timeout=120.0  # 2 minutes to allow model loading
    )
    agents.cli.run_app(worker_options)



