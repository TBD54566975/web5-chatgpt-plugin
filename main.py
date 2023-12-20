import json
import os
import flask
from flask import Flask, request, send_file, Response
from flask_cors import CORS
import yaml
from openai import OpenAI
from usage_cost_tracker import UsageCostTracker

client = OpenAI()
usage_cost_tracker = UsageCostTracker()

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

@app.route("/help/<topic>", methods=['GET'])
def help_topic(topic):
    try:
        with open(f'content/{topic}.txt', 'r') as file:
            content = file.read()
        explanation, code = content.split('-----', 1)
        return Response(response=json.dumps({"code": code.strip(), "explanation": explanation.strip()}), status=200, mimetype='application/json')
    except FileNotFoundError:
        return Response(response=json.dumps({"error": "Topic not found"}), status=404, mimetype='application/json')
    except Exception as e:
        return Response(response=json.dumps({"error": str(e)}), status=500, mimetype='application/json')


@app.route("/logo.png", methods=['GET'])
def plugin_logo():
    filename = 'logo.png'
    return send_file(filename, mimetype='image/png')

@app.route("/.well-known/ai-plugin.json", methods=['GET'])
def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return Response(text, mimetype="application/json")

@app.route("/openapi.yaml", methods=['GET'])
def openapi_spec():
    base_openapi = {
        "openapi": "3.0.1",
        "info": {
            "title": "Web5 assistant",
            "description": "An assistant for helping build web5 applications using the web5 sdk.",
            "version": "v1"
        },
        "servers": [
            {"url": f"https://chatgpt.tbddev.org"}
        ],
        "paths": {},
        "components": {
            "schemas": {
                "instructionResponse": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "a sample piece of code or explanation."
                        },
                        "explanation": {
                            "type": "string",
                            "description": "what the sample code does or explanation is for."
                        }
                    }
                }
            }
        }
    }

    for filename in os.listdir('content'):
        if filename.endswith('.txt'):
            topic = filename[:-4]
            with open(f'content/{filename}', 'r') as file:
                explanation, _ = file.read().split('-----', 1)
                base_openapi['paths'][f'/help/{topic}'] = {
                    "get": {
                        "operationId": f"help{topic.capitalize()}",
                        "summary": explanation.strip(),
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/instructionResponse"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

    return Response(yaml.dump(base_openapi), mimetype="text/yaml")




@app.route("/ask_chat", methods=['GET'])
def ask_chat_route():
    usage_cost_tracker.check_usage_costs()

    query = request.args.get('query')

    messages = [{"role": "system", "content": "you are a helpful assistant to find the best names that match what knowledge is being asked for. Return only a list of matching names as requested."},
               {"role": "user", "content": "I will provide you lists of json objects which map a name of a piece of knowledge to a description. You then take a question from the website developer.tbd.website and return a list of names that best the question, 2 to 3 ideally."},
               {"role": "assistant", "content": "Got it."},
               {"role": "user", "content": "[{'name': 'frog_eyes', 'description': 'describes the nature of frog eyes'], {'name': 'cat_hair', 'description': 'learn about cat hair here. See cats for more detail.'], {'name': 'cats', 'description': 'some base knowledge about cats']"},
               {"role": "assistant", "content": "What is your question?"},
               {"role": "user", "content": "what do I do about too much cat hair?"},
               {"role": "assistant", "content": "cats,cat_hair"},
               {"role": "user", "content": "ok good. Now I will provide you with some JSON again to do it with that new data set."},
               {"role": "assistant", "content": "Got it."},
               {"role" : "user",  "content" : str(get_chat_functions())},
               {"role": "assistant", "content": "What is your question?"},
               {"role": "user", "content": query},
               ]

    response = client.chat.completions.create(model="gpt-4-1106-preview",
    messages=messages)
    usage_cost_tracker.compute_response_costs(response)

    response_message = response.choices[0].message
    csv_list = response_message.content
    print("csv_list", csv_list)


    csv_list = csv_list.split(',')

    # build up knowledge base
    knowledge = ''

    for item in csv_list:
        try:
            with open(f'content/{item.strip()}.txt', 'r') as file:
                content = file.read()
        except FileNotFoundError:
            print(f"No file found for {item.strip()}")
            knowledge = ''
            break

        _, code = content.split('-----', 1)
        knowledge += f"{item}:\n\n{code}\n\n"



    messages = [{"role": "system", "content": "You are a helpful assistant that provides code examples and explanations when context is provided. Please don't invent APIs. Code examples should be surrounded with markdown backticks to make presentation easy."},
            {"role": "user", "content": "Please don't hallucinate responses if you don't know what the API is, stick to the content you know. Also remember code examples should be surrounded with markdown backticks to make presentation easy."},
            {"role": "assistant", "content": "Got it."},
            {"role": "user", "content": "Context:\n " +  knowledge},
            {"role": "assistant", "content": "OK, what is your question?"},
            {"role": "user", "content": "Following is a question from the developer.tbd.website: " + query}]


    def stream():
        response_tokens = 0
        
        if knowledge == '':
            yield 'data: Sorry, I don\'t know about that topic. Please try again.\n\n'
            return
        completion = client.chat.completions.create(model="gpt-3.5-turbo-16k",
        messages=messages,
        stream=True)
        usage_cost_tracker.compute_messages_cost(messages, "gpt-3.5-turbo-16k")
        for line in completion:
            print(line.choices[0])
            chunk = line.choices[0].delta.content
            if chunk:
                response_tokens += usage_cost_tracker.count_tokens(chunk)

                if chunk.endswith("\n"):
                    yield 'data: %s|CR|\n\n' % chunk.rstrip()
                else:
                    yield 'data: %s\n\n' % chunk

        # Post process the response to add the cost    
        usage_cost_tracker.compute_tokens_cost(response_tokens, "gpt-3.5-turbo-16k", is_output=True)

    return flask.Response(stream(), mimetype='text/event-stream')


def get_chat_functions():
    functions = []
    for filename in os.listdir('content'):
        if filename.endswith('.txt'):
            topic = filename[:-4]
            with open(f'content/{filename}', 'r') as file:
                explanation, _ = file.read().split('-----', 1)
                functions.append({
                    "name": f"{topic}",
                    "description": explanation.strip()
                })

    return functions

def main():
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    if debug_mode:
        app.run(debug=debug_mode, host="0.0.0.0", port=5003)
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    #ask_chat_route()
    main()
