"""" Quick prototype for an automatic transaction categorizer for a set of credit card transactions. 
    A GUI window pops up at the beginning to generate some example data for the prompts sent to the Language Model. 

    It is not necessary to enter anything if you want it to just make its best guess with no example data.
    It does a pretty darn good job.

    Each item in the "description" column of a credit card statemnet is fed to the 
    local large language model (no cloud, all opensource). It guesses the best 
    category for the line item and then a new .csv file is generated at the end.

    The PyQt GUI code and answer caching makes this harder to read. You should be able to delete all the surrounding lines
    and write your own minimal implementation.
"""
import pdb
import pandas as pd
# Important Line
from llama_cpp import Llama
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel,QApplication, QWidget, QComboBox


def on_button_click(self):
    """ When button is clicked, turn the comboboxes with a value other than 'No Input' into
    a piece of the example prompt sent to the LLM in the format Q: A:  """
    print("on_button_click")
    _example_prompt = ""
    for name in combobox_names_list: 
        _ans = win.findChild(QComboBox,name).currentText()
        _desc = win.findChild(QLabel,"l" + name).text()
        if _ans != "No Input":
            _example_prompt += " Q: " + _desc + " A: " + _ans
    global example_prompt_from_user_input 
    example_prompt_from_user_input = _example_prompt
    win.close() 

def create_win():
    """ Pop up a GUI window to help prompt the LLM """
    _df = df.copy()
    _df.drop_duplicates(['Description'])
    samp = _df.sample(n=20)
    for idx, row in samp.iterrows():
        row_layout = QHBoxLayout()
        label = QLabel(row['Description'])
        label.setObjectName("l" + str(idx))
        label.setAccessibleName("l" + str(idx))
        combo_box = QComboBox(parent=win)
        combo_box.setObjectName(str(idx))
        combo_box.setAccessibleName(str(idx))
        combobox_names_list.append(combo_box.objectName())
        combo_box.addItems(["No Input"] + [cat.strip() for cat in CATEGORIES.split(",")])
        row_layout.addWidget(label)
        row_layout.addWidget(combo_box)
        layout.addLayout(row_layout)
    button_cont = QPushButton("Create prompt and let LLM solve task") 
    button_cont.clicked.connect(on_button_click)
    layout.addWidget(button_cont)
    win.setLayout(layout)
    win.show()

def predict_categories_with_llm(example_prompt):
    """ Add examples from user inputted changes, if any, then process more rows"""

    for idx, row in df.iterrows():

        desc = row['Description']

        # add any santization of the description column here 
        desc = desc[0:55]

        one_shot_prompt = f"""You are a direct and to-the-point question answering robot. Please help select the best category for a credit card transaction based on its description column. 
        The only allowed answers are: {CATEGORIES}.""" 
        examples = f"Examples to follow: {example_prompt_from_user_input}"
        user_data_prompt = f"Pick the best category. Q: {desc} A:"""

        # assemble the prompt that is going to the LLM 
        one_shot_prompt = one_shot_prompt + examples + user_data_prompt
        assert len(one_shot_prompt) <= CONTEXT_SIZE, "Increase CONTEXT_SIZE variable"

        answer = ""

        cat_mentioned_first = "NO_ANSWER" 
        cat_loc = 999 
        if desc in cache:
            answer = cache[desc]
            cat_mentioned_first = cat_predicted_cache[desc]
            print("cached value used")
        else:
            # generate a response (takes several seconds)
            full_prompt = one_shot_prompt + examples + user_data_prompt
            #######################################################
            # Important Line
            #######################################################
            output = LLM(full_prompt,temperature=0.9,seed=42)
            answer = output["choices"][0]["text"].splitlines()[0]
            # santize answer a little bit
            answer = answer.replace('\\','')
            answer = answer.upper() 

            cats_answered = 0
            for cat in CATEGORIES.split(","):
                cat = cat.strip()
                if cat in answer:
                    find_result = answer.find(cat)
                    if find_result != -1 and find_result < cat_loc:
                        cat_loc = answer.find(cat)
                        # Select first allowed category given in the answer
                        cat_mentioned_first = cat
            
            print(f"Desc = {desc}")
            print(f"Answer = {answer}")
            print(f"Category selected = {cat_mentioned_first}")
           
            cache[desc] = answer
            cat_predicted_cache[desc] = cat_mentioned_first

        df.loc[idx, "LLM Answer"] = cache[desc]
        df.loc[idx, "Category_LLM"] = cat_predicted_cache[desc]

def write_results_to_disk():
    """ Write modified dataframe to disk with the new Categories_LLM column for the 
     category picked by the LLM for each transaction """
    with open("results.csv","w") as f:
        f.write(df.to_string())


### GLOBALS 

CATEGORIES = "GAS_OR_CONVENIENCE_STORE, TRAVEL, RETAIL_STORE, ONLINE_PURCHASE, RESTAURANT, GROCERY, MEDICAL, RECREATION, BILL_PAY"
# Data from the initial GUI window fills these with the user selections
combobox_names_list = []
example_prompt_from_user_input = ""

# Setup for spreadsheet processing
df = pd.read_csv("./data/cc_transactions.csv")
df['Category_LLM'] = "NO_ANSWER"
cache = {}
cat_predicted_cache = {}

# Set up LLM to run prompts against
# Remove n_gpu_layers if you don't have a GPU. It will be 10-30x slower per answer)
CONTEXT_SIZE = 1024
LLM = Llama(model_path="/home/bb/llms/mistral-7b-instruct-v0.2.Q4_K_M.gguf" ,n_ctx=CONTEXT_SIZE,n_threads=10,n_gpu_layers=22)

# Set up QT App for taking user input
app = QApplication(["LLM Transaction Categorizer"])
app.setStyle('Windows')
win = QWidget(parent=None)
layout = QVBoxLayout()

create_win()
app.exec()    

predict_categories_with_llm(example_prompt_from_user_input)

write_results_to_disk()