# AGI-Hackathon

Pretty often while working on a codebase you want to understand how a piece of data flows through the system.
So the idea here is to generate a graph of code snippets to easily visualize how things flow and to be able to navigate back to files easily.

main.py runs the graph UI from a graph.json file
graph.py creates the graph.json file from a repository. 
I didn't really manage to go for a general approach yet so the current approach is very specific to the picnichealth repository.

Ideally with the right prompting you would have less domain knowledge and GPT-4 could navigate the codebase by itself to create the graph.
