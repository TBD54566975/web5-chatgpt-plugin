import datetime
import tiktoken
import os
from openai.types.chat import ChatCompletion

MONTHLY_USAGE_LIMIT_USD = os.getenv("WEB5GPT_MONTHLY_USAGE_LIMIT_USD")

DEFAULT_MONTHLY_USAGE_LIMIT_USD = 500.0

# Pricing rates updated on 2023-12-19
MODELS_COSTS = {
    "gpt-3.5-turbo-16k": { "price_per_thousand_tokens": { "input": 0.001, "output": 0.0020 } },
    "gpt-4-1106-preview": { "price_per_thousand_tokens": { "input": 0.01, "output": 0.03 } },
}

class UsageCostTracker:
    def __init__(self):
        self.current_date = datetime.datetime.now().date()
        self.monthly_usage_cost = 0.0
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # initialize monthly usage limit in USD
        if MONTHLY_USAGE_LIMIT_USD:
            self.total_monthly_limit = float(MONTHLY_USAGE_LIMIT_USD)
        else:
            self.total_monthly_limit = DEFAULT_MONTHLY_USAGE_LIMIT_USD
        print(">>> Total monthly cost limit: $%.2f" % self.total_monthly_limit)

    def check_usage_costs(self):
        today = datetime.datetime.now().date()

        # Reset the monthly usage cost if it's a new month
        if self.current_date.month != today.month:
            print(">>> New month, resetting monthly usage cost")
            print(">>> Current Monthly usage cost: $%.4f (of $%.2f)" % (self.monthly_usage_cost, self.total_monthly_limit))
            self.monthly_usage_cost = 0.0
            self.current_date = today

        # Check if the monthly usage cost has exceeded the limit
        if self.monthly_usage_cost >= self.total_monthly_limit:
            raise Exception(f">>> ERROR! Monthly usage cost ${self.monthly_usage_cost:.2f} exceeded limit of ${self.total_monthly_limit:.2f}")
        
    def compute_response_costs(self, response: ChatCompletion):
        if not response.usage or not response.model:
            print(">>> WARNING! No model/usage in response, impossible to compute costs")
            return
        
        response_model = response.model
        if response_model not in MODELS_COSTS:
            print(">>> WARNING! Model not found in MODELS_COSTS, impossible to compute costs")
            return

        model_costs = MODELS_COSTS[response_model]

        print(">>> Computing costs for Model: %s" % response_model)

        price_per_thousand_tokens = model_costs["price_per_thousand_tokens"]
        input_cost = calculate_tokens_cost(response.usage.prompt_tokens, price_per_thousand_tokens["input"])
        output_cost = calculate_tokens_cost(response.usage.completion_tokens, price_per_thousand_tokens["output"])
        total_cost = input_cost + output_cost
        print(">>> Total cost: $%.4f" % total_cost)

        self.monthly_usage_cost += total_cost
        print(">>> Current Monthly usage cost: $%.4f (of $%.2f)" % (self.monthly_usage_cost, self.total_monthly_limit))


    def compute_messages_cost(self, messages, model_name):
        tokens_per_message = 3
        tokens_per_name = 1
        num_tokens = 0
        
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += self.count_tokens(value)
                if key == "name":
                    num_tokens += tokens_per_name
        
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        
        self.compute_tokens_cost(num_tokens, model_name)


    def compute_stream_cost(self, chunk, model_name):
        token_count = self.count_tokens(chunk)

        # Assuming the chunk is the response content
        self.compute_tokens_cost(token_count, model_name, is_output=True)


    def compute_tokens_cost(self, tokens, model_name, is_output=False):
        if model_name not in MODELS_COSTS:
            print(">>> WARNING! Model not found in MODELS_COSTS, impossible to compute costs")
            return

        model_costs = MODELS_COSTS[model_name]
        input_type = "output" if is_output else "input"
        price_per_thousand_tokens = model_costs["price_per_thousand_tokens"][input_type]

        usage_cost = calculate_tokens_cost(tokens, price_per_thousand_tokens)

        self.monthly_usage_cost += usage_cost
        print(f">>> Added cost: ${usage_cost:.4f}, New monthly usage: ${self.monthly_usage_cost:.4f} (of ${self.total_monthly_limit:.2f})")

    def count_tokens(self, text):  
        return len(self.tokenizer.encode(text))



def calculate_tokens_cost(tokens, price_per_thousand_tokens):
    cost_per_token = price_per_thousand_tokens / 1000
    return cost_per_token * tokens
    