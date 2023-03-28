# AGI-Hackathon

Pretty often while working on a codebase you want to understand how a piece of data flows through the system.
So the idea here is to generate a graph of code snippets to easily visualize how things flow and to be able to navigate back to files easily.

You'll need the following dependencies to run:
`pip install tkinter`
`pip install openai`

`python main.py` runs the graph UI from a graph.json file

`python graph.py column_name table_name` creates the graph.json file from the picnichealth repository (hardcoded in the file). 

I didn't really manage to go for a general approach yet so the current approach is very specific to the picnichealth repository.

Ideally with the right prompting you would have less domain knowledge and GPT-4 could navigate the codebase by itself to create the graph.
