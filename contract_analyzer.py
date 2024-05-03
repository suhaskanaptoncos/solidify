import google.generativeai as genai
import json
import os
import sys
import argparse

def analyzeContract(contract_folder):
    try:
        print("Analyzing Contract")
        contract_file_path = None
        for filename in os.listdir(contract_folder):
            if filename.endswith("main.sol"):
                contract_file_path = os.path.join(contract_folder, filename)

        with open(contract_file_path, 'r') as fp:
            contract_code = fp.read()

        req_folder_name = os.path.join(contract_folder, 'Solidify')
        if not os.path.exists(req_folder_name):
            os.makedirs(req_folder_name) 
        else:
            for filename in os.listdir(req_folder_name):
                file_path = os.path.join(req_folder_name, filename)
                os.remove(file_path)

        with open('gemini_api_key.txt', 'r') as fp:
            api_key = fp.read()
        
        genai.configure(api_key=api_key)
        exfunc= '''function add(uint a, uint b) external view returns (uint) {return a + b;}'''
        prompt = f'Read the following solidity code and output a list of functions for the bottom most contract ONLY along with their code with return types, even if they return void, and any and all modifiers such as external, view, onlyOwner, etc. and the function comments directly above each function in an python array of objects in the following format: {{\"function name\": the function\'s name, \"function with code\": function with all of its code in the function body as one line without newlines, \"function_comment\": data}}. The code is the following: {contract_code}. CODE ONLY, no accomppanying text, no comments, etc. Just output the desired data in the asked format! An example of the format you should adhre to very closely is "\"function name\": \"add\", \"\"function with code\": {exfunc}, \"function_comment\": "Adds two values". Your output should be a valid JSON String. Do not wrap your output in ``` json ```, just output the json string exclusively.'

        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        out_obj = response.text
    except Exception as ex:
        print("An error occurred. Please try again" + str(ex))
        sys.exit(1)
    
    try:
        data = json.loads(out_obj)

    except Exception as ex:
        print("There is an error turning the LLM output into an analysis_output.json file. This is a common error, the best thing to do is simply try again.")
        print(f"The LLM Output is {out_obj}. You can try either running this tool again, or manually use the output for the next step by creating an analysis_output.json file.")
        sys.exit(1)
    
    try:
        with open(f"{req_folder_name}/analysis_output.json", "w") as fp:
            json.dump(data, fp)

    except Exception as ex:
        print("An error occurred. Please try again" + str(ex))
        sys.exit(1)
        
    print("Successfully analyzed contract")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyzes a contract folder.')
    parser.add_argument('contract_folder', type=str, help='Path to the contract folder, ex. "sample_contracts/CarMileageTracker"')
    args = parser.parse_args()
    analyzeContract(args.contract_folder)
