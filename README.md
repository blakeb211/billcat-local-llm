# Credit Card Statement Categorizer using AI (private, no cloud)
* A local (doesn't even require internet) Large Language Model (LLM) 
performs the task of reading credit card transaction descriptions (messy text) 
and assigning the best category out of a list you give it.

# Why 
* To show an example of how to setup an LLM comparable to GPT3 on your laptop
for something useful. This is not the most profound example...
**Your own local AI model like ChatGPT but without the subscription or the privacy concern of sending them your data...**
* Demonstrate prompt engineering an LLM to give you the answer you want.
* Demonstrate prototyping NLP projects quickly with an LLM .

# How it works
* Optionally enter some examples via the GUI window and click the button. A custom
prompt will be created and sent to the LLM.
* <img src="screenshots/GUI_window_to_prompt_LLM_with_examples.png" alt="hi" class="inline"/>
* Timing data and debug info is printed to the console as the spreadsheet file is processed line by line.
* It outputs a new **results.csv** spreadsheet with a column "Category_LLM" containing the category selected by the LLM. 
* They won't be perfect but they are very good for having no database or human involved.

# Caveats
* This is prototype to display the technique, nothing more and not production code.

# Install
* Download the mistral-7b or similar LLM model file **(Google: "mistral-7b-instruct-v0.2.Q4_K_M.gguf huggingface")** from huggingface and put it in its own directory. You'll see where to tweak the location inside of *main.py*.
* Change the folder `/home/bb/llms` in main.py to point to your model file. (mistral-7b recommended, but others work!)
* ```python3.10 -m venv myenv``` # create virtual environment
* ```source myenv/bin/activate``` # activate virtual environment
* Install python package *llama-cpp-python* with or without cuda support 
* To install with cuda: `FORCE_CMAKE=1 CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python`
* If you want to use CPU only, (10-30x slower per answer, but still delivers the point) just skip the line above.
* Install the other dependencies:
* ```pip install -r requirements.txt```
* Run with  `python main.py`

# Help me out!
* If you found this helpful and got to understand LLMs prototyping a bit better, I would be extremely glad if you could give it a star! :star:
