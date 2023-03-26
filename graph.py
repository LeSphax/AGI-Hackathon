import re
import openai
import os
import json
import subprocess
import sys


openai.api_key = "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"
openai.organization = "org-TUxwYZcwSlYKsglx4uq3SdJO"

id = 0


def find_top_level_variable(file_path, line_number):
    result = subprocess.run(
        ["node", "find_variable.js", file_path, str(line_number)],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()

def call_chatgpt(initialPrompt, prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4", 
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

def print_color(text, color):
    colors = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }
    if color not in colors:
        print(text)
    else:
        print(colors[color] + text + colors['reset'])

def search_codebase(root_directory, terms, path_matches, source_id, ignore_dirs=["node_modules", "cjs", "test", "__mocks__", "db", "__generated_graphql_types__"]):
    result = []
    pattern = re.compile("|".join(terms))
    ignore_dirs = ignore_dirs
    snippet = ""

    for root, dirs, files in os.walk(root_directory):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]  # modified line

        for file in files:
            if not file.endswith(".js") and not file.endswith(".jsx") and not file.endswith(".ts") and (not file.endswith(".tsx") or file.endswith(".spec.tsx")):
                continue
            match = True
            for path_match in path_matches:
                if not path_match in root and not path_match in file:
                  match = False
            
            if not match:
               continue
            
            # print_color(file, "blue")

            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                lines = f.readlines()

            
            line_indices = []
            last_snippet = ""
            for i, line in enumerate(lines):
                if pattern.search(line):
                    line_indices.append(i)
                    snippet = find_top_level_variable(file_path, i)
                    if snippet != last_snippet:
                      global id
                      result.append({"filename": file_path.replace(root_directory + "/", "", 1), "source_id": source_id, "id": id, "line_number": i, "content": snippet, "snippet": '\n'.join(snippet.split('\n')[:3])})
                      id += 1
                      last_snippet = snippet
                
    return result

model_prompt = lambda column, table, snippets: f"""Here is a code snippet from a Sequelize model file. 

{snippets}

Is "{column}" an attribute of the {table} model?
Just answer with "Yes" or "No".
"""

controllers_prompt = lambda column, table, snippets: f"""Here is a code snippet from an API controller file. 

{snippets}

Is "{column}" an attribute of the {table} API controller?
Just answer with "Yes" or "No".
"""

actions_prompt = lambda column, table, snippets: f"""Here is a code snippet from a Redux action file. 

{snippets}

Is this action calling the {table} API controller?

This is an example of an action calling the 

This is the function used to create an API action:

export function createApiAction<R extends any = any, F extends AsyncApiActionFn<R> = AsyncApiActionFn<any>, P extends any = any>(
  type: string,
  endpoint: ResolveType<string, F>,
  requestOptions: ApiActionRequestOptions<F> = defaultRequestOptions,
  actionPayloadCreator: ((...args: Parameters<F>) => P) | null = null,
  nextActions?: ResolveType<NextActions<R> | undefined, F>
)

This is an example of using this function to call the concept api controller:

export const loadTnmCategoryConcepts = createApiAction(
  LOAD_TNM_CATEGORY_CONCEPTS,
  ApiEndpoints[ApiObjects.CONCEPT],
  {{
    method: SEARCH,
    query: () => ({{count: Object.values(TnmCategoryConcepts).length}}), // needed since default is 20
    payload: () => ({{conceptFragments: Object.values(TnmCategoryConcepts)}})
  }}
);

This is an example of an action calling the deleted_prediction_fields controller:

  const _loadDeletedPredictionFields = createApiAction(
    LOAD_DELETED_PREDICTION_FIELDS,
    ApiEndpoints[ApiObjects.DELETED_PREDICTION_FIELD],
    {{
      method: SEARCH,
      query: () => {{
        return {{include: 'words'}};
      }},
      payload: values => values
    }},
    values => values,
    [nextAction]
  );

  dispatch(_loadDeletedPredictionFields(values));

Just answer with "Yes" or "No".
"""

def check_if_valid_snippets(results, prompt_function, column_name, table_name):
  valid_results = []
  for result in results:
    snippet = result['content']
    prompt = prompt_function(column_name, table_name.capitalize(), snippet)
    # print_color(snippet, "yellow")
    response = call_chatgpt("You are a helpful code navigation assistant", prompt)
    print_color(response, "green")
    if "yes" in response.lower():
      valid_results.append(result)
  return valid_results

PROMPTS = {
   "models": model_prompt,
   "controllers": controllers_prompt,
   "actions": actions_prompt,
  #  "selectors": selectors_prompt
}

def iteration(root_directory, last_node, step, column_name, table_name):
    if last_node is not None:
      print("->", last_node["filename"])
    patterns = [column_name] if step != "actions" else [table_name.upper(), table_name.capitalize()]
    path_patterns = [table_name, step] if step != "actions" else ["action"]
    results = search_codebase(root_directory, patterns, path_patterns, last_node["id"] if last_node is not None else None)
    # for res in results:
    #   print_color(str(res), "blue")
    valid_results = check_if_valid_snippets(results, PROMPTS[step], column_name, table_name)

    return valid_results

def update_graph(nodes, result):
  nodes += result
  data = {"nodes": nodes}
  with open("graph.json", "w") as f:
      json.dump(data, f, indent=2)

if __name__ == "__main__":
  nodes = []
  root_directory = "../picnic/packages"
  column_name = sys.argv[1] 
  table_name = sys.argv[2]

  result = iteration(root_directory, None, "models", column_name, table_name)
  update_graph(nodes, result)
  result = iteration(root_directory, result[0], "controllers", column_name, table_name)
  update_graph(nodes, result)
  result = iteration(root_directory, result[0], "actions", column_name, table_name)
  update_graph(nodes, result)

  for node in nodes:
     print(node["filename"])

          
