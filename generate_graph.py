import os
import openai
import re

openai.api_key = "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"
openai.organization = "org-TUxwYZcwSlYKsglx4uq3SdJO"

def call_chatgpt(initialPrompt, prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[
          {"role": "system", "content": initialPrompt}, 
          {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0,
    )

    return response.choices[0].message['content'].strip()


def search_codebase(root_directory, terms, is_backend, ignore_dirs=["node_modules", "cjs", "test", "__mocks__", "__generated_graphql_types__"]):
    result = []
    pattern = re.compile("|".join(terms))
    ignore_dirs = ignore_dirs if not is_backend else ignore_dirs + ["frontend"]
    context_lines = 3
    snippet = ""

    for root, dirs, files in os.walk(root_directory):
        for dir_to_ignore in ignore_dirs:
            if dir_to_ignore in dirs:
                dirs.remove(dir_to_ignore)  # skip the directory

        for file in files:
            if not file.endswith(".js") and not file.endswith(".jsx") and not file.endswith(".ts") and (not file.endswith(".tsx") or file.endswith(".spec.tsx")):
                continue

            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if pattern.search(line):
                    start = max(i - context_lines, 0)
                    end = min(i + context_lines + 1, len(lines))
                    context = "".join(lines[start:end])
                    if not snippet:
                        snippet = context
                    else:
                        snippet += "\n" + context
            if snippet:
                result.append({"filename": file_path.replace(root_directory + "/", "", 1), "content": snippet})
                snippet = ""
                
    return result





def generate_graph(table_name, column_name, root_directory):
    nodes = []
    edges = []
    visited = set()

    current_terms = [f"{table_name}.{column_name}"]
    current_files = search_codebase(root_directory, current_terms)

    while current_files:
        next_files = []
        next_terms = []

        for current_file in current_files:
            if current_file["filename"] in visited:
                continue

            visited.add(current_file["filename"])

            snippet = current_file["content"][:1000]
            systemPrompt = f"""You are codeGPT, a code navigation tool."""
            prompt = f"""Given a codebase with a React frontend, Hapi and NodeJS backend, and Sequelize ORM connected to a PostgreSQL database, analyze the following code snippet:

 Given two code snippets you should tell me if those two are related. You must return the code snippets that match the query. You can use the following commands:
{snippet}

Filename: {current_file['filename']}

Search term(s): {', '.join(current_terms)}

Should this snippet be added to the graph and what are the next terms to search for?
"""
            response = call_chatgpt(systemPrompt, prompt)
            response = response.split("\n")

            if response[0].lower() == "yes":
                node_data = {
                    "filename": current_file["filename"],
                    "snippet": snippet
                }
                nodes.append(node_data)

                if len(response) > 1:
                    next_terms += response[1].split(", ")

        if next_terms:
            next_files = search_codebase(root_directory, next_terms)

        current_terms = next_terms
        current_files = next_files

    return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    table_name = "users"
    column_name = "email"
    root_directory = "../picnic"

    result = search_codebase(root_directory, [f"isIllegible"], True)

    search_snippets = ""
    for idx, entry in enumerate(result):
        search_snippets += f"{idx}: {entry['filename']}"
        search_snippets += entry['content'] + "\n"

    test_prompt = """Here is a code snippet from a Sequelize model file. 
        I want to find the usages of the isIllegible column in the codebase. So any place reading or writing to that column in the codebase.
   
    Here are some snippets that match our query "isIllegible". Which of those snippets are usages of the "isIllegible" column?
    """ + search_snippets + """
     
    Return the index of the snippets that contain references and an explanation of why you picked them.
    
    """
    print(test_prompt)

    response = call_chatgpt("You are a code navigation assistant", test_prompt)
    print(response)

    # graph_data = generate_graph(table_name, column_name, root_directory)

    # with open("graph.json", "w") as f:
    #     json.dump(graph_data, f, indent=2)
