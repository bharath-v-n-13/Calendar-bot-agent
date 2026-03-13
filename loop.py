import os
import logging
from datetime import datetime
import google.generativeai as genai
from skills import add_task, list_tasks, delete_task, search_events, save_note, list_notes, get_datetime
from memory import conversation_history

logger = logging.getLogger(__name__)

# Fallback on initialization 
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

MAX_HISTORY = 20
MAX_STEPS = 8

SYSTEM_PROMPT = f"""You are a personal productivity assistant on Telegram.
Help users manage tasks directly in their Google Calendar, save notes, and stay organised.
Always use a tool when the request maps to one. When a user asks you to add an event or a task, 
construct a natural language query for Google Calendar's QuickAdd and pass it to add_task, keeping their dates intact.
Be concise and friendly. Use Telegram markdown (* bold, _ italic).
Current UTC Time is: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"""

TOOLS = genai.protos.Tool(function_declarations=[
    genai.protos.FunctionDeclaration(
        name="add_task",
        description="Add a new task or event to the user's Google Calendar. Pass the natural language string (e.g. 'Lunch with Bob tomorrow at 12pm'). Make sure you mention any known timezone explicitly.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={"task": genai.protos.Schema(type=genai.protos.Type.STRING, description="Task natural language string")},
            required=["task"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="list_tasks",
        description="List all upcoming events/tasks from the user's Google Calendar.",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={})
    ),
    genai.protos.FunctionDeclaration(
        name="delete_task",
        description="Delete an event or task from Google Calendar. Pass the name/description of the event to delete.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={"task_name": genai.protos.Schema(type=genai.protos.Type.STRING, description="Name or partial name of the task to delete")},
            required=["task_name"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="search_events",
        description="Search for upcoming festivals, holidays, or specific events across all user calendars.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={"query": genai.protos.Schema(type=genai.protos.Type.STRING, description="What to search for, e.g., 'festival', 'Diwali', 'meeting'")},
            required=["query"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="save_note",
        description="Save a quick note for the user.",
        parameters=genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={"note": genai.protos.Schema(type=genai.protos.Type.STRING, description="Note content")},
            required=["note"]
        )
    ),
    genai.protos.FunctionDeclaration(
        name="list_notes",
        description="List all saved notes.",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={})
    ),
    genai.protos.FunctionDeclaration(
        name="get_datetime",
        description="Get the current date and time.",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={})
    ),
])

def _execute_tool(name, args_dict, user_id):
    if name == "add_task":      return add_task(user_id, args_dict.get("task", ""))
    if name == "list_tasks":    return list_tasks(user_id)
    if name == "delete_task":   return delete_task(user_id, args_dict.get("task_name", ""))
    if name == "search_events": return search_events(user_id, args_dict.get("query", ""))
    if name == "save_note":     return save_note(user_id, args_dict.get("note", ""))
    if name == "list_notes":    return list_notes(user_id)
    if name == "get_datetime":  return get_datetime()
    return "Unknown skill."

def run_agent(user_id, user_message):
    history = conversation_history.setdefault(user_id, [])
    if len(history) > MAX_HISTORY:
        history[:] = history[-MAX_HISTORY:]

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
        tools=[TOOLS]
    )
    chat = model.start_chat(history=history)

    for step in range(MAX_STEPS):
        response = chat.send_message(user_message if step == 0 else "continue")
        
        if not response.candidates or not response.candidates[0].content.parts:
            return "No valid response from agent."
            
        part = response.candidates[0].content.parts[0]

        if hasattr(part, "function_call") and part.function_call.name:
            fn = part.function_call
            
            # safely extract args
            args_dict = {}
            if hasattr(fn, "args"):
                for k in fn.args:
                    args_dict[k] = fn.args[k]

            result = _execute_tool(fn.name, args_dict, user_id)
            logger.info(f"[Step {step+1}] {fn.name} → {result}")

            response2 = chat.send_message(
                genai.protos.Content(parts=[
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fn.name,
                            response={"result": result}
                        )
                    )
                ])
            )
            final = response2.text
            history.append({"role": "user",  "parts": [user_message]})
            history.append({"role": "model", "parts": [final]})
            return final

        final = response.text
        history.append({"role": "user",  "parts": [user_message]})
        history.append({"role": "model", "parts": [final]})
        return final

    return "Couldn't complete that — please try again."
