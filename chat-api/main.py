import openai
import json


api_did_content = """


Overview
The did class is responsible for providing operations related to DIDs

Methods

create(method, options)
Enables generation of DIDs for a supported set of DID Methods. The output is method-specific, and handles things like key generation and assembly of DID Documents that can be published to DID networks.

NOTE
You do not usually need to manually invoke this, as the Web5.connect() method already acquires a DID for the user (either by direct creation or connection to an identity agent app).

Parameters
method: type is string: The method on which to create the did. Supported methods are: 'ion' and 'key'
options type is CreateOptions (optiona): Enables customization of the DID formation based on the DID method

Return Value: The created DID

//Code Example
const myDid = await web5.did.create('ion');


resolve(did):
Resolves a DID into a DID document by using the "read" operation of the applicable DID method. DIDs that are resolved are cached for a default of 15 minutes.
DIDs need to be resolved to their document (that contains all the information of the did you want to reach).

Parameters
did type is string: The decentralized identifier to resolve

Return Value
result: type DidResolutionResult: DID resolution result which includes DID Document and its metadata


// Code Example:
const myDid = 'did:key:z6MkhvthBZDxVvLUswRey729CquxMiaoYXrT5SYbCAATc8V9';
const didDocument = await web5.did.resolve(myDid);

"""


def run_conversation():
    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": "How do I resolve a DID using the web5 did api?"}]
    functions = [
        {
            "name": "api_did",
            "description": "Explains the did API. Web5. Please use the output of this function and ideally one other for formulate an answer.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):

        print("-----> GPT wants to call a function " + str(response_message["function_call"]))

        function_name = response_message["function_call"]["name"]
        function_response = api_did_content

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )  # get a new response from GPT where it can see the function response
        return second_response


print(run_conversation())