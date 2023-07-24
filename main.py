import json
import os
import flask
from flask import Flask, request, send_file, Response
from flask_cors import CORS
import yaml
import openai

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
    query = request.args.get('query')
    messages = [{"role": "system", "content": "You are a helpful web5 assistant that provides code examples and explanations. Please don't invent APIs. Code examples should be surrounded with markdown backticks to make presentation easy."},
                {"role": "user", "content": "Following is a question from the developer.tbd.website about web5: " + query}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=get_chat_functions(),
        function_call="auto",
    )
    response_message = response["choices"][0]["message"]

    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]
        with open(f'content/{function_name}.txt', 'r') as file:
            content = file.read()
        _, code = content.split('-----', 1)
        function_response = code
        messages.append(response_message)
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )


        def stream():
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True
            )
            for line in completion:
                chunk = line['choices'][0].get('delta', {}).get('content', '')
                if chunk:                    
                    if chunk.endswith("\n"):
                        yield 'data: %s|CR|\n\n' % chunk.rstrip()                    
                    else:
                        yield 'data: %s\n\n' % chunk                    

        
        return flask.Response(stream(), mimetype='text/event-stream')        

    else:
        print("Unable to answer")
        def stream():
            yield "data: Unable to provide a relevant answer at this time.\n\n"
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
                    "description": explanation.strip(),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
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
    main()
