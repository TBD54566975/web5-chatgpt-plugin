# Web5 assistant plugin for ChatGPT

This is the source code for the ChatGPT plugin for Web5 assistant. You can find this plugin on the ChatGPT plugin store (you will currently need ChatGPT Plus access).

This ChatGPT plugin is an assistant that can teach you about web5, Decentralized Web Nodes and more, and can even write web5 code for you if you ask it nicely.

## Some examples

![ex1](https://github.com/TBD54566975/web5-chatgpt-plugin/assets/14976/b3d8d7d3-47c9-4c71-8740-f8e8f0fdf2da)

![ex2](https://github.com/TBD54566975/web5-chatgpt-plugin/assets/14976/5d7f6029-6399-4c35-a44e-7a426d866577)
![ex3](https://github.com/TBD54566975/web5-chatgpt-plugin/assets/14976/64ff76f6-7b3b-4bde-95e7-a66438990d77)
![ex4](https://github.com/TBD54566975/web5-chatgpt-plugin/assets/14976/695b4def-272d-462d-8956-16ce835a6506)

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
