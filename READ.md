This project is a game/program generator that uses chatGPT to take a game idea and writes the program.<br />
Here is how:
- The first pass examines the project, determining the best way to create the project
- The next pass writes the architecture
- Then, every file is populated with the data of other files
- Then a readME is written

Structure:
web-games-hub/
├── server.js
├── package.json
└── src/
    ├── index.html
    ├── main.js
    ├── loader.js
    ├── baseGame.js
    ├── assets/
    │   └── css/
    │       └── styles.css
    └── games/
        └── exampleGame.js
