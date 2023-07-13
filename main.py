import json
import quart
import quart_cors
from quart import request
import yaml
import os


app = quart_cors.cors(quart.Quart(__name__), allow_origin=["https://chat.openai.com", "http://localhost:3000"])

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

    return quart.Response(yaml.dump(base_openapi), mimetype="text/yaml")


@app.route("/ask_chat", methods=['GET'])
def ask_chat_route():
    query = request.args.get('query')
    resp = ask_chat(query)
    if resp:
        return quart.Response(response=resp, status=200) #quart.Response(response=json.dumps({"answer": resp}), status=200)
    else:
        return quart.Response(response="Unable to provide a relevant answer at this time.", status=500)

def ask_chat(query):
    import openai

    messages = [{"role": "system", "content": "You are a helpful web5 assistant that provides code examples and explanations. Please don't invent APIs. Code examples should be surrounded with markdown backticks to make presentation easy."},
                {"role": "user", "content": "Following is a question from the developer.tbd.website about web5: " + query}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=get_chat_functions(),
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]

    # check if GPT wanted to call a function
    if response_message.get("function_call"):

        print("-----> GPT wants to call a function " + str(response_message["function_call"]))

        function_name = response_message["function_call"]["name"]

        with open(f'content/{function_name}.txt', 'r') as file:
            content = file.read()
        _, code = content.split('-----', 1)

        function_response = code

        # send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
        )  # get a new response from GPT where it can see the function response

        second_response_message = second_response['choices'][0]['message']
        if second_response_message.get("function_call"):
            print("<-----> second function call desired (NOT IMPLEMENTED) " + str(second_response_message["function_call"]))
            
            

        return second_response['choices'][0]['message']['content']   
    
    # by default we return nothing, as we don't want to let it hallcinate a response without web5 context. 
    return None  


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
    #print(ask_chat("How do I resolve a DID using the web5 did api?"))
    app.run(debug=True, host="0.0.0.0", port=5003)
    

if __name__ == "__main__":
    main()
