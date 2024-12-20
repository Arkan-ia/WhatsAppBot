# --------------------------------------------------------------
# Import Modules
# --------------------------------------------------------------

import os
import json
import openai
from dotenv import load_dotenv

from src.utils.open_ai_tools import get_notify_payment_mail_tool, get_store_user_data_tool, notify_payment_mail, store_user_data

# --------------------------------------------------------------
# Load OpenAI API Token From the .env File
# --------------------------------------------------------------

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# --------------------------------------------------------------
# Include Multiple Functions
# --------------------------------------------------------------

def ask_and_reply(prompt):
    """Give LLM a given prompt and get an answer."""

    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        tools=[get_notify_payment_mail_tool(), get_store_user_data_tool()],
    )

    output = completion.choices[0].message
    print(output)
    return output


user_prompt = "Hola, me llamo Johan David Lozano Leiva, johan@gmail.com, tengo diabetes"

# Get info for the next prompt
output = ask_and_reply(user_prompt)
print("output: ", output)

if output.tool_calls:
    for tool_call in output.tool_calls:
        print("Calling function....: ", tool_call.function.name)

        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if function_name == "notify_payment_mail":
            notify_payment_mail()

        elif function_name == "store_user_data":
            store_user_data("400692489794103", "573142968931", args)


