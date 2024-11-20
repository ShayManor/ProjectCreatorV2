import json
from enum import Enum
import re

from openai import OpenAI

assistants = {
    1: 'asst_M5oJambUmo3QU4KEFmWNieyX',  # expander
    2: 'asst_8eil2JwBOwOEUSR0lf39Xqnb',  # Game Creator
    3: 'asst_wSPoByRgyfYJn4J7DzxddxLZ',  # photos parser
    4: ''  # photos
}
prompt = """
Instructions: Given a game description, you are going to write the following file to accurately and efficiently build the game instructed to you.
Only return the whole code of the file but only change the methods with TODOs. You are allowed to write and implement other helper methods.
Do not return additional formatting such as markdown blocks.
Ensure the game has a UI, works well, and has all functionality needed.
Ensure the game looks good to play. For example, sudoku should have bars between rows and columns, chess should fit on one page and have black and white squares, and colors when possible should be used.
Ensure everything fits on the screen.
"""
with open('template.txt', 'r') as f:
    prompt += ''.join(f.readlines())
    prompt += '\n Here is the description: \n'

templates = ['init', 'render', 'addEventListeners', 'handleInput', 'update']


class Assistants(Enum):
    EXPANDER = 'asst_M5oJambUmo3QU4KEFmWNieyX'
    CREATOR = 'asst_8eil2JwBOwOEUSR0lf39Xqnb'
    PHOTOS_PARSER = 'asst_wSPoByRgyfYJn4J7DzxddxLZ'


class game:
    def __init__(self, initial_prompt):
        self.image_descriptions = None
        self.expanded_game_prompt = None
        self.initial_game_prompt = initial_prompt

        self.client = OpenAI()

    def generate(self, prompt, assistant):
        assistant = self.client.beta.assistants.retrieve(
            assistant_id=assistant
        )

        thread = self.client.beta.threads.create(
            messages=[{"role": "user", "content": prompt}]
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        if run.status == "completed":
            messages = self.client.beta.threads.messages.list(thread_id=run.thread_id)
            ai_response = messages.data[0].content[0].text.value
            return ai_response

    def generate_o1(self, expanded_prompt):
        response = self.client.chat.completions.create(
            model="o1-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt + expanded_prompt
                        },
                    ],
                }
            ]
        )

        print(response.choices[0].message.content)
        return response.choices[0].message.content

    def sanitize_input(self, data: str) -> str:
        data = data.replace('*', '').split('\n')
        # print(data)
        # if '```' in data and '```' in data[data.index('```')]:
        #     data = re.findall(r'```(.*?)```', data, re.DOTALL)
        # print(data)
        return ''.join(data)

    def generate_image(self, text):
        res = self.client.images.generate(
            prompt=text,
            n=1,
            size="256x256",
        )
        return res.data[0].url

    def expand(self) -> str:
        expanded_game_prompt = self.generate(self.initial_game_prompt, Assistants.EXPANDER.value)
        # print(expanded_game_prompt)
        return expanded_game_prompt

    def parse_photos(self, expanded_game_prompt) -> dict[str, str] | None:
        images = self.generate(expanded_game_prompt, Assistants.PHOTOS_PARSER.value)
        if images == "None":
            return None
        # print(f'initial images are: {images}')
        images = self.sanitize_input(images)
        # print(f'final images are: {images}')
        return json.loads(images)

    def create_photos(self, parsed_photos: dict[str, str]) -> dict[str, str]:
        photos = {}
        for photo in parsed_photos.keys():
            photos[photo] = self.generate_image(photo)
        # print(photos)
        return photos

    def create_game(self, expanded_prompt: str, photos_dict: dict[str, str]) -> str:
        prompt = expanded_prompt + '\n' + str(photos_dict)
        res = self.generate_o1(prompt)
        # print(res)
        return json.loads(self.sanitize_input(res))

    def put(self, lines, text, index):
        return lines[0:index] + text.split('\n') + lines[index:]

    def main(self):
        expanded_prompt = self.expand()
        # print(expanded_prompt)
        expanded_photos = self.parse_photos(expanded_prompt)

        photo_dict = {}
        # print(expanded_photos)
        if expanded_photos != "None" and expanded_photos != '{}' and expanded_photos is not None:
            photo_dict = self.create_photos(expanded_photos)
            with open('game/src/assets/images.json', 'w') as images:
                json.dump(photo_dict, images)

        final_game_code: str = self.create_game(expanded_prompt, photo_dict)
        print(final_game_code)
        with open('game/src/games/test_game.js', 'w') as w:
            w.write(final_game_code)

        # print(game_dict)
        # with open('template.txt', 'r') as f:
        #     lines = ''.join(f.readlines())
        #     for t in templates:
        #         # print(t)
        #         lines.replace(f'// TODO: {t}', game_dict[t])
        #     for t in game_dict.keys():
        #         if t not in templates:
        #             # print(game_dict[t])
        #             lines.replace('// TODO: other', game_dict[t] + '\n' + '// TODO: other' + '\n')
        #     with open('game/src/games/test_game.js', 'w') as w:
        #         print("Final game: " + lines)
        #         w.write(lines)


games = ['Create me a sodoku game with a gui', 'Create me chess with 2 players', 'Create me a maze game with a gui']
# for g in games:
#     game(g).main()
game('Create me chess with 2 players').main()
