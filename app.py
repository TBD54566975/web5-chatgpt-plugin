import os
import flask
import openai
from flask import Flask

openai.api_key = os.environ.get('OPENAI_API_KEY')
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
        <body>
        <h1>response:</h1>
        <div id="result"></div>
        <script>
        var source = new EventSource("/completionChat");
        source.onmessage = function(event) {
            document.getElementById("result").innerHTML += event.data + "<br>";
        };
        </script>
        </body>
    </html>
    """


@app.route('/completionChat', methods=['GET'])
def completion_api():
    def stream():
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo', 
            messages=[{"role": "user", "content": "Hello world"}],
            stream=True)
        for line in completion:
            chunk = line['choices'][0].get('delta', {}).get('content', '')
            if chunk:
                yield 'data: %s\n\n' % chunk
    return flask.Response(stream(), mimetype='text/event-stream')

def main():
    import os
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
