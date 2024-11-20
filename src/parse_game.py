import json
from enum import Enum

from openai import OpenAI

assistants = {
    1: 'asst_M5oJambUmo3QU4KEFmWNieyX',  # expander
    2: 'asst_8eil2JwBOwOEUSR0lf39Xqnb',  # Game Creator
    3: 'asst_wSPoByRgyfYJn4J7DzxddxLZ',  # photos parser
    4: ''  # photos
}


class Assistants(Enum):
    EXPANDER = 1
    CREATOR = 2
    PHOTOS_PARSER = 3


class game:
    def __init__(self, initial_prompt):
        self.image_descriptions = None
        self.expanded_game_prompt = None
        self.initial_game_prompt = initial_prompt

        self.client = OpenAI()

    def generate(self, prompt, num: int):
        assistant = self.client.beta.assistants.retrieve(
            assistant_id=assistants[num]
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

    def sanitize_input(self, data: str) -> str:
        data = data.replace('*', '').split('\n')
        if '```' in data[0] or '```' in data[-1]:
            data = data[1:-1]
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
        print(expanded_game_prompt)
        return expanded_game_prompt

    def parse_photos(self, expanded_game_prompt) -> dict[str, str] | None:
        images = self.generate(expanded_game_prompt, Assistants.PHOTOS_PARSER.value)
        if images == "None":
            return None
        print(f'initial images are: {images}')
        images = self.sanitize_input(images)
        print(f'final images are: {images}')
        return json.loads(images)

    def create_photos(self, parsed_photos: dict[str, str]) -> dict[str, str]:
        photos = {}
        for photo in parsed_photos.keys():
            photos[photo] = self.generate_image(photo)
        # print(photos)
        return photos

    def create_game(self, expanded_prompt: str, photos_dict: dict[str, str]) -> dict[str, str]:
        prompt = expanded_prompt + '\n' + str(photos_dict)
        res = self.generate(prompt, Assistants.CREATOR.value)
        print(res)
        return json.loads(self.sanitize_input(res))

    def main(self):
        expanded_prompt = self.expand()
        print(expanded_prompt)
        expanded_photos = self.parse_photos(expanded_prompt)

        photo_dict = {}
        print(expanded_photos)
        if expanded_photos != "None" and expanded_photos != '{}' and expanded_photos is not None:
            photo_dict = self.create_photos(expanded_photos)
            with open('game/src/assets/images.json', 'w') as images:
                json.dump(photo_dict, images)

        game_dict = self.create_game(expanded_prompt, photo_dict)
        print(game_dict)


games = ['Create me a sodoku game with a gui', 'Create me chess with 2 players', 'Create me a maze game with a gui']
for g in games:
    game(g).main()
game('Create me a sodoku game with a gui').main()
