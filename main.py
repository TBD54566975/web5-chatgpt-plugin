import json
import quart
import quart_cors
from quart import request
import yaml
import os


app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

@app.route("/help/<topic>", methods=['GET'])
async def help_topic(topic):
    try:
        with open(f'content/{topic}.txt', 'r') as file:
            content = file.read()
        explanation, code = content.split('-----', 1)
        return quart.Response(response=json.dumps({"code": code.strip(), "explanation": explanation.strip()}), status=200)
    except FileNotFoundError:
        return quart.Response(response=json.dumps({"error": "Topic not found"}), status=404)
    except Exception as e:
        return quart.Response(response=json.dumps({"error": str(e)}), status=500)


@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.route("/openapi.yaml", methods=['GET'])
async def openapi_spec():
    host = request.headers['Host']
    base_openapi = {
        "openapi": "3.0.1",
        "info": {
            "title": "Web5 Plugin",
            "description": "A plugin that assist users to build web5 applications using the web5 sdk.",
            "version": "v1"
        },
        "servers": [
            {"url": f"http://{host}"}
        ],
        "paths": {},
        "components": {
            "schemas": {
                "instructionResponse": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "a sample piece of code"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "what the sample code does."
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

    return quart.Response(yaml.dump(base_openapi), mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()