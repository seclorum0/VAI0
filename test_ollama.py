import ollama

response = ollama.chat(model='llama2', messages=[
    {'role': 'user', 'content': 'Halo, apa kabar?'}
])
print(response['message']['content'])