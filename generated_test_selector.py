import sys
import os
import re
import google.generativeai as genai
import argparse

try:
    # Instantiate Model
    with open('gemini_api_key.txt', 'r') as fp:
            api_key = fp.read()
    genai.configure(api_key=api_key)
    USE_ADVANCED_MODEL = False
    REPEAT_AMOUNT = 3

    if USE_ADVANCED_MODEL:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
    else:
        model = genai.GenerativeModel('gemini-pro')

    chat = model.start_chat(history=[])

except Exception as e:
    print(f"An error with initializing the model occurred: {e}")
    sys.exit(1)

def generated_test_selector(folder_path, test_string):
    matching_files = None
    try:
        solidify_path = os.path.join(folder_path, 'Solidify')
        files = os.listdir(solidify_path)
        pattern = re.compile(f"{test_string}_\d+")
        matching_files = [file for file in files if pattern.match(file)]

        if not matching_files or len(matching_files) == 0:
            raise Exception("No files matching test string are found. Please read documentation and try again.")
        
    except Exception as e:
        print(f"An error with finding the test files occurred: {e}")
        sys.exit(1)

    try:
        print("Generating tests")
        option_prompt_str = []
        for i, file_name in enumerate(matching_files):
            file_num = i + 1
            with open(os.path.join(solidify_path, file_name), 'r') as fp:
                file = fp.read()
                option_prompt_str.append(f"Option {file_num} is {file}. ")

        option_prompt_str = "".join(option_prompt_str)

        prompt = f'You are given truffle js test files to unit test a particular function in a smart contract written in solidity. Please select the option for the file that is the best testing file, in terms of test quality and lack of compilation errors. Your options are: {option_prompt_str} Simply output the number of the option, so if you pick option 2 simply output 2.'
        response = chat.send_message(prompt)
        selected_test = response.text
        
        print(f"Selected test: {selected_test}")

    except Exception as e:
        print(f"An error with selecting the test occurred: {e}")
        sys.exit(1)

            
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Selects best generated test.')
    parser.add_argument('contract_folder', type=str, help='Path to the contract folder with Solidify folder inside, ex. "sample_contracts/CarMileageTracker"')
    parser.add_argument('test_string', type=str, help='test string for desired test selection, ex. "registerCar_FUNCTIONAL"')
    args = parser.parse_args()
    generated_test_selector(args.contract_folder, args.test_string)