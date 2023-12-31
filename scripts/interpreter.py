import json
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
from queries import get_itinerary



class Interpreter:

    def __init__(self, user_message: str):

        load_dotenv() 
        self.client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

        self.assistant = self.client.beta.assistants.retrieve(os.getenv("ASSISTANT_ID"))
        self.thread = self.client.beta.threads.create()
        self.thread_id = self.thread.id
        self.assistant_id = self.assistant.id


        message = self.client.beta.threads.messages.create(
        thread_id=self.thread.id,
        role="user",
        content=user_message
    )
        

    def run(self):
        
        # Create a new run for the given thread and assistant
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )

        # Loop until the run status is either "completed" or "requires_action"
        while run.status == "in_progress" or run.status == "queued":
            time.sleep(1)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=run.id
            )

            # At this point, the status is either "completed" or "requires_action"
            if run.status == "completed":
                return self.client.beta.threads.messages.list(
                thread_id=self.thread_id
                )
            if run.status == "requires_action":
                print(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
                # generated_python_code = json.loads(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)['code']
                result = get_itinerary(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments)
                run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=self.thread_id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                            "output": result,
                        },
                    ]
                )


    def get_response(self):
        
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        for thread_message in messages.data:
            for content in thread_message.content:
                print(content.text.value)
                response = content.text.value
                break
            break
        return response

#bot = Interpreter("I want to fly from MXP to USH")
#bot.run()
#print("sleeping 10")
#time.sleep(10)
#bot.get_response()
