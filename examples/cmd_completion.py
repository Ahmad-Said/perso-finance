# to enable completion in intellij go to:
# run configuration -> modify options -> emulate terminal in output console

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

# Define the words for autocompletion
fruit_completer = WordCompleter(['apple', 'banana', 'bambo', 'cherry', 'date', 'elderberry', 'fig', 'grape'])

# Use the prompt with autocompletion
user_input = prompt("Type a fruit name: ",
                    default='apple',
                    completer=fruit_completer)
print(f"You entered: {user_input}")
