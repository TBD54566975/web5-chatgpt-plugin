import json

import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}


@app.get("/help/setup")
async def help_setup():
    return quart.Response(response=json.dumps({"code": "npm install @tbd54566975/web5", "explanation": "This is how you install it from the command line."}), status=200)


@app.get("/help/did")
async def help_did():
    return quart.Response(response=json.dumps({"code": "const did = await web5.did.create('ion');", "explanation": "Create a Decentralized Identifier (DID). This one creates one of the ION did method type."}), status=200)


store = '''
        const { record } = await web5.dwn.records.write(did.id, {
          author: did.id,
          data: "Hello Web5",
          message: {
            dataFormat: 'text/plain',
          },
        });
'''

@app.get("/help/store")
async def help_store():
    return quart.Response(response=json.dumps({"code": store, "explanation": "Shows how to store in the web5 DWN."}), status=200)


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

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
