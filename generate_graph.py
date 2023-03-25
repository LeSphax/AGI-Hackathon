import os
import openai
import re

openai.api_key = "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"

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

    test_prompt = """You are codeGPT, a code navigation tool. Your output should only contain digits separated by newlines, no explanation, no words.
Given a codebase with a React frontend, Hapi and NodeJS backend, and Sequelize ORM connected to a PostgreSQL database, analyze the following code snippet:

Here is a code snippet containing the declaration for the *isIllegible* variable we are interested in:

module.exports = function(sequelize, DataTypes) {
  const attributes = {
    id: {type: DataTypes.UUID, primaryKey: true},
    word: DataTypes.STRING,
    predictedWord: DataTypes.STRING,
    predictionBot: DataTypes.STRING,
    confidence: DataTypes.FLOAT,
    boundingBoxX: {type: DataTypes.FLOAT, min: 0, max: 1},
    boundingBoxY: {type: DataTypes.FLOAT, min: 0, max: 1},
    boundingBoxW: {type: DataTypes.FLOAT, min: 0, max: 1},
    boundingBoxH: {type: DataTypes.FLOAT, min: 0, max: 1},
    inlineStyleRanges: DataTypes.JSONB,
    correctedAt: DataTypes.DATE,
    *isIllegible: {type: DataTypes.BOOLEAN, defaultValue: false},*
    isHandwriting: {type: DataTypes.BOOLEAN, defaultValue: false}
  };

  return sequelizeHelper.define(sequelize, 'Word', attributes, {
    schema: 'ocr',
    classMethods: {
      initialize(models) {
        sequelizeHelper.addRelations(this, models, [
          ['belongsTo', models.PdfPage],
          ['belongsTo', models.TrialRun],
          ['belongsTo', models.User],
          ['belongsToMany', models.Field, {through: models.FieldWord}]
        ]);
      },
      getWordsByPosition(
        models,
        pdfPageId,
        startX,
        startY,
        endX,
        endY,
        trialRunId,
        {transaction, attributes} = {}
      ) {
        return models.Word.findAll({
          attributes,
          where: {
            id: models.sequelize.literal(`id IN (
              SELECT id FROM ocr.words
              WHERE pdf_page_id = :pdfPageId
                AND trial_run_id IS NOT DISTINCT FROM :trialRunId
                AND BOX(
                  POINT(bounding_box_x, -bounding_box_y),
                  POINT(bounding_box_x + bounding_box_w, -(bounding_box_y + bounding_box_h))
                ) && BOX(
                  POINT(:startX, -(:startY)),
                  POINT(:endX, -(:endY))
                )
   
    Here are some snippets that match our query "isIllegible":
    """ + search_snippets + """
    Tell me which snippets contain references to the variable in the first snippet.

    A reference could be:
    - Any usage of that specific variable. Not another variable with the same name.
     
    Return the index of the snippets that contain references and an explanation of why you picked them.
    
    """
    print(test_prompt)

    call_chatgpt()

    # graph_data = generate_graph(table_name, column_name, root_directory)

    # with open("graph.json", "w") as f:
    #     json.dump(graph_data, f, indent=2)
