import json

import quart
import quart_cors
from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}


@app.get("/help/setup")
async def help_setup():
    return quart.Response(response=json.dumps({"code": "npm install @tbd54566975/web5@0.7.0", "explanation": "This is how you install it from the command line for npm, showing the version."}), status=200)


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



@app.get("/help/write-send")
async def help_e2e():
    sample = '''
// Create a record in Alice's DWN
const { record: aliceRecord } = await web5.dwn.records.create({
  data: "Hello Web5",
  message: {
    dataFormat: 'text/plain',
  },
});

// Alice writes the same record to Bob's DWN
const { status } = await record.send(bobDid);
'''
    return quart.Response(response=json.dumps({"code": sample, "explanation": "Create a record in Alice's DWN, and send it directly to Bobs DWeb Nodes."}), status=200)


@app.get("/help/query")
async def help_query():
    sample = '''
const web5 = new Web5();
const response = await web5.dwn.records.query('did:example:bob', {
  author: 'did:example:alice',
  message: {
    filter: {
      schema: 'https://schema.org/Playlist',
      dataFormat: 'application/json'
    }
  }
});

console.log(response.entries) // logs array of Record class instances
'''
    return quart.Response(response=json.dumps({"code": sample, "explanation": '''Method for querying the DWeb Node of a provided target DID. The query request must contain the following:
author - string: The decentralized identifier of the DID signing the query. This may be the same as the target parameter if the target and the signer of the query are the same entity, which is common for an app querying the DWeb Node of its own user.
message - object: The properties of the DWeb Node Message Descriptor that will be used to construct a valid DWeb Node message.'''}), status=200)


@app.get("/help/query-full")
async def help_query_full():
    sample = '''
//A. Your local

const { protocols, status } = await dwn.protocols.query({
  message: {
    filter: {
      protocol: emailProtocolDefinition.protocol
    }
  }
});

//B. Your remote
const { protocols, status } = await dwn.protocols.query({
  from: aliceDid,
  message: {
    filter: {
      protocol: emailProtocolDefinition.protocol
    }
  }
});

// C. Someone else's remote
const { protocols, status } = await dwn.protocols.query({
  from: bobDid,
  message: {
    filter: {
      protocol: emailProtocolDefinition.protocol
    }
  }
});

console.log(response.entries) // logs array of Record class instances
'''
    return quart.Response(response=json.dumps({"code": sample, "explanation": '''Query from your DWN or remote DWeb nodes. Uses protocol as filter criteria but can also use a 'schema' field instead of protocol (which is a jsonschema)'''}), status=200)


@app.get("/help/protocol")
async def help_protocol():
    sample = '''
// installing a protocol in your local DWN looks like this:    
const { protocol, status } = await web5.dwn.protocols.configure({
  message: {
    definition: chatProtocolDefinition
  }
});    

// The following is an example protocol in json: 

{
  "protocol": "http://credential-issuance-protocol.xyz",
  "types": {
    "credentialApplication": {
      "schema": "https://identity.foundation/credential-manifest/schemas/credential-application",
      "dataFormats": ["application/json"]
    },
    "credentialResponse": {
      "schema": "https://identity.foundation/credential-manifest/schemas/credential-response",
      "dataFormats": ["application/json"]
    }
  },
  "structure": {
    "credentialApplication": {
      "$actions": [
        {
          "who": "anyone",
          "can": "write"
        }
      ],
      "credentialResponse": {
        "$actions": [
          {
            "who": "recipient",
            "of": "credentialApplication",
            "can": "write"
          }
        ]
      }
    }
  }
}

'''
    return quart.Response(response=json.dumps({"code": sample, "explanation": '''Shows how to install a protocol, and also has an example of a web5 protocol defintion that allows a credential issuance flow. Protocols allow threaded conversations.'''}), status=200)


@app.get("/help/html-import")
async def help_html():
    sample = '''
  <script type="module">

    import { Web5 } from 'https://cdn.jsdelivr.net/npm/@tbd54566975/web5@0.7.0/dist/browser.mjs';

    const web5 = new Web5();'''
    return quart.Response(response=json.dumps({"code": sample, "explanation": "Shows how to use web5 in a html page script tag."}), status=200)










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
