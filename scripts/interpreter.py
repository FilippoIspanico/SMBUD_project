from openai import OpenAI
import os
from dotenv import load_dotenv



class Interpreter:

    def __init__(self):

        load_dotenv() 
     
        self.client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))


        print(self.client)
        completion = self.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
            {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
        ]
        )

        print(completion.choices[0].message)


interpreter = Interpreter()