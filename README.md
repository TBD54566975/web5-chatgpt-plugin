# Web5 assistant plugin for ChatGPT

This ChatGPT plugin is an assistant that can teach you about web5, Decentralized Web Nodes and more, and can even write web5 code for you if you ask it nicely. 

## Some examples



## Setup

Firstly, you need to have a ChatGPT account and access to GPT-4 and the plugin store. If you don't have access yet, please join the waitlist [here](https://openai.com/waitlist/plugins).

To install the required packages for this plugin, run the following command:

```bash
pip install -r requirements.txt
```

To run the plugin, enter the following command:

```bash
python main.py
```

Once the local server is running:

1. Navigate to https://chat.openai.com. 
2. In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).
3. Select "Plugin store"
4. Select "Develop your own plugin"
5. Enter in `localhost:5003` since this is the URL the server is running on locally, then select "Find manifest file".

The plugin should now be installed and enabled! You can start with a question like "What is on my todo list" and then try adding something to it as well! 

## Getting help

If you run into issues or have questions building a plugin, please join our [Developer community forum](https://community.openai.com/c/chat-plugins/20).
