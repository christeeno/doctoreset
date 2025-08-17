from __future__ import annotations
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import google
from dotenv import load_dotenv
from api import HealthAssistantFnc
from prompts import WELCOME_MESSAGE, INSTRUCTIONS, LOOKUP_PATIENT_MESSAGE, SYMPTOM_COLLECTION_MESSAGE, SYMPTOM_FOLLOWUP_MESSAGE, CONVERSATION_COMPLETION_MESSAGE, REPORT_GENERATION_MESSAGE
import os

load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    
    model = google.beta.realtime.RealtimeModel(
        model="gemini-2.0-flash-exp",
        instructions=INSTRUCTIONS,
        voice="Puck",
        temperature=0.8,
        
    )
    assistant_fnc = HealthAssistantFnc()
    assistant = MultimodalAgent(model=model, fnc_ctx=assistant_fnc)
    assistant.start(ctx.room)
    
    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="assistant",
            content=WELCOME_MESSAGE
        )
    )
    session.response.create()
    
    # Conversation phase tracking
    conversation_phase = "info_collection"  # phases: info_collection, symptoms, completion
    symptoms_collected = False
    
    @session.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        nonlocal conversation_phase, symptoms_collected
        
        if isinstance(msg.content, list):
            msg.content = "\n".join("[image]" if isinstance(x, llm.ChatImage) else x for x in msg)
        
        # Check if consultation is complete
        if assistant_fnc.is_consultation_complete():
            # Consultation is already complete, just acknowledge
            session.conversation.item.create(
                llm.ChatMessage(
                    role="assistant",
                    content="Your consultation has been completed and your report has been generated. Thank you!"
                )
            )
            session.response.create()
            return
            
        if assistant_fnc.has_patient():
            handle_query(msg, conversation_phase, symptoms_collected)
        else:
            find_profile(msg)
        
    def find_profile(msg: llm.ChatMessage):
        session.conversation.item.create(
            llm.ChatMessage(
                role="system",
                content=LOOKUP_PATIENT_MESSAGE(msg.content)
            )
        )
        session.response.create()
        
    def handle_query(msg: llm.ChatMessage, phase: str, symptoms_collected: bool):
        nonlocal conversation_phase
        
        # Determine conversation phase and appropriate response
        if phase == "info_collection" and assistant_fnc.has_patient():
            # Patient info is complete, transition to symptom collection
            conversation_phase = "symptoms"
            session.conversation.item.create(
                llm.ChatMessage(
                    role="system",
                    content=f"{SYMPTOM_COLLECTION_MESSAGE} User message: {msg.content}"
                )
            )
        elif phase == "symptoms":
            # Check if user wants to end consultation or continue with symptoms
            user_content = msg.content.lower()
            if any(phrase in user_content for phrase in ["that's all", "nothing else", "done", "complete", "finish", "end consultation"]):
                # User wants to complete consultation
                conversation_phase = "completion"
                session.conversation.item.create(
                    llm.ChatMessage(
                        role="system",
                        content=f"{CONVERSATION_COMPLETION_MESSAGE} User message: {msg.content}"
                    )
                )
            else:
                # Continue collecting symptoms
                current_symptoms = assistant_fnc.get_symptoms()
                if "No symptoms" in current_symptoms:
                    # First symptom collection
                    session.conversation.item.create(
                        llm.ChatMessage(
                            role="system",
                            content=f"Collect the patient's symptoms. User message: {msg.content}"
                        )
                    )
                else:
                    # Follow-up symptom questions
                    session.conversation.item.create(
                        llm.ChatMessage(
                            role="system",
                            content=f"{SYMPTOM_FOLLOWUP_MESSAGE(assistant_fnc._symptoms)} User message: {msg.content}"
                        )
                    )
        elif phase == "completion":
            # Handle completion phase - check if user confirms or wants to add more
            user_content = msg.content.lower()
            if any(phrase in user_content for phrase in ["yes", "generate", "complete", "done", "finish"]):
                # User confirms completion, generate report
                session.conversation.item.create(
                    llm.ChatMessage(
                        role="system",
                        content=f"{REPORT_GENERATION_MESSAGE} Please call the end_consultation function to generate the report."
                    )
                )
            else:
                # User wants to add more information, go back to symptoms
                conversation_phase = "symptoms"
                session.conversation.item.create(
                    llm.ChatMessage(
                        role="system",
                        content=f"Continue collecting symptoms or information. User message: {msg.content}"
                    )
                )
        else:
            # Default handling
            session.conversation.item.create(
                llm.ChatMessage(
                    role="user",
                    content=msg.content
                )
            )
        
        session.response.create()
    
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))