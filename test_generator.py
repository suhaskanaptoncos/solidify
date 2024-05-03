import google.generativeai as genai
import json
import os
import sys
import argparse
try:
    # Instantiate Model
    with open('gemini_api_key.txt', 'r') as fp:
            api_key = fp.read()
    genai.configure(api_key=api_key)
    USE_ADVANCED_MODEL = False

    if USE_ADVANCED_MODEL:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
    else:
        model = genai.GenerativeModel('gemini-pro')

    chat = model.start_chat(history=[])

except Exception as e:
    print(f"An error with initializing the model occurred: {e}")
    sys.exit(1)
    

def train_model(training_data_path):

    try:
        # Load training data
        training_folders = []
        func_training_examples = []
        auth_training_examples = []
        input_training_examples = []

        for subfolder in os.listdir(training_data_path):
            if subfolder.startswith("training_example_") and subfolder.endswith(str(int(subfolder.split("_")[-1]))):
                training_folders.append(os.path.join(training_data_path, subfolder))
        
        for training_folder in training_folders:
            found = False
            # Functional Training
            for filename in os.listdir(training_folder):
                if filename.endswith("functional_tests.js"):
                    with open(os.path.join(training_folder, filename), 'r') as fp:
                        func_test_example = fp.read()
                        found = True
                elif filename.endswith(".sol"):
                    with open(os.path.join(training_folder, filename), 'r') as fp:
                        contract_example = fp.read()
            if found:
                func_training_examples.append((contract_example, func_test_example))

            # Authorization Training
            found = False
            for filename in os.listdir(training_folder):
                if filename.endswith("authorization_tests.js"):
                    with open(os.path.join(training_folder, filename), 'r') as fp:
                        auth_test_example = fp.read()
                        found = True
                elif filename.endswith(".sol"):
                    with open(os.path.join(training_folder, filename), 'r') as fp:
                        contract_example = fp.read()
            if found:
                auth_training_examples.append((contract_example, auth_test_example))

            # Input Training
            found = False
            for filename in os.listdir(training_folder):
                if filename.endswith("input_tests.js"):
                    with open(os.path.join(training_folder, filename), 'r') as fp:
                        input_test_example = fp.read()
                elif filename.endswith(".sol"):
                    with open(os.path.join(training_folder, filename), 'r') as fp:
                        contract_example = fp.read()
                        found = True
            if found:
                input_training_examples.append((contract_example, input_test_example))

        # Train model    
        response = chat.send_message("Your job will be to generate unit test files for smart contracts. Train yourself on the given full smart contract code, list of functions, and function tests to learn how to do this as your job will be to generate FULL, READY TO RUN truffle js test files. Do not wrap in ``` javascript ``` Just output only \"DONE\" if you understand.")
        print("Initial Setup: " + response.text)

        for full_code, test_code in func_training_examples:
            response = chat.send_message(f"Train yourself on the following example. This is an example of testing the functionality of functions. Observe how the test is checking if the function behaves as expected. The full smart contract is: {full_code}, the list of functions being tested is: getPosition(), registerAsset(), and the test code example is: {test_code}. When you are asked later to generate functional tests you should create similar tests. If you have done so, just only respond \"DONE\"")
            print("Training Functional: " + response.text)
        
        for full_code, test_code in auth_training_examples:
            response = chat.send_message(f"Train yourself on the following example. This is an example of testing the authorization and access control aspect of functions. Observe how the test is checking if the function's access control behaves properly. The full smart contract is: {full_code}, the list of functions being tested is: registerAsset(), and the test code example is: {test_code}. When you are asked later to generate authorization tests you should create similar tests. If you have done so, just only respond \"DONE\"")
            print("Training Authorization: " + response.text)
        
        for full_code, test_code in input_training_examples:
            response = chat.send_message(f"Train yourself on the following example. This is an example of testing how the function behaves with incorrect/invalid input. Observe how the test is checking if the function errors as expected for incorrect/invalid input. The full smart contract is: {full_code}, the list of functions being tested is: registerAsset(), and the test code example is: {test_code}. When you are asked later to generate input tests you should create similar tests. If you have done so, just only respond \"DONE\"")
            print("Training Input: " + response.text)
        
        print("")

    except Exception as e:
        print(f"An error with training the model occurred: {e}")
        sys.exit(1)

def test_generator(contract_folder, iteration, num_tests = 2):
    try:
        print("Generating Tests")
        print("")
        analysis_output_file_path = None
        test_suites_file_path = None
        for filename in os.listdir(os.path.join(contract_folder, "Solidify")):
            if filename.endswith("analysis_output.json"):
                analysis_output_file_path = os.path.join(contract_folder, "Solidify",filename)
            if filename.endswith("test_suites.json"):
                test_suites_file_path = os.path.join(contract_folder, "Solidify", filename)

        if not analysis_output_file_path or not test_suites_file_path:
            print("Analysis output file not found in the proper folder. Please use the analyze_file.py tool to generate it.")
            sys.exit(1)

        with open(analysis_output_file_path, 'r') as fp:
            analysis_data = json.load(fp)
        
        with open(test_suites_file_path, 'r') as fp:
            test_suites = json.load(fp)

        contract_file_name = None
        for filename in os.listdir(contract_folder):
            if filename.endswith("main.sol"):
                contract_file_name = os.path.join(contract_folder, filename)

        with open(contract_file_name, 'r') as cont_fp:
            full_smart_contract = cont_fp.read()

        NUM_TESTS = num_tests
            
        test_prompts = {1: f'Test the correctness of the function. Use and understand the the function code and test description provided to create a FULL, READY TO RUN truffle js test file with {NUM_TESTS} truffle js tests for the provided function to ensure that the provided function is acting correctly. In other words you need to understand the function and write correctness tests for it. Remember to use your training to help you create the test file similar to your training for functional tests. DO NOT USE ANY truffleAssert, chai, or external packages other than the ones in your training!  Do not wrap in ``` javascript ``` Mark your output with // FUNCTIONAL TEST', 
                        2: f'Test the behavior of the function with authorized and unauthorized users. Use and understand the function code and test description provided to create a FULL, READY TO RUN truffle js test file with {NUM_TESTS} truffle js tests for the provided function to ensure that the function acts properly with authorized and unauthorized users. In other words you need to understand the function and write authorization tests for it in a test file. For example, an onlyOwner function must only work with the account that deployed the contract and functions that require a user to have a role should not work without the role. Make sure to set up try catch statements as necessary to capture the errors for unauthorized actions, but do not expect a specific error string, just expect an error for an unauthorized action. Do not test the functionality of the function, only test that it errors with invalid input. Remember your training to help you create the file similar to your training on authorization tests. DO NOT USE ANY truffleAssert, chai, or external packages other than the ones in your training!  Do not wrap in ``` javascript ``` Mark your output with // AUTHORIZATION TEST',
                        3: f'Test the behavior of the function with incorrect input. Use and understand the function code and test description provided to create a FULL, READY TO RUN truffle js test file with {NUM_TESTS} truffle js tests to ensure the function errorswhen invalid input is entered. In other words you need to understand the function and write two tests for each parameter such that the program errors properly with incorrect/invalid input. For example a function that uses an address must make sure it errors when the address is invalid. Make sure to set up try catch statements as necessary to capture the errors for incorrect input, but do not expect a specific error string, just expect an error for an incorrect input. Remember to use your training to help you create the test file similar to your training for input tests. DO NOT USE ANY truffleAssert, chai, or external packages other than the ones in your training!  Do not wrap in ``` javascript ``` Mark your output with // INPUT TEST'}

        test_types = {1: 'FUNCTIONAL', 2: 'AUTHORIZATION', 3: 'INPUT'}

        for func in analysis_data:
            function_w_code = func['function with code']
            function_comment = func['function_comment']
            function_name = func['function name']
            test_suite = test_suites.get(function_name, None)
            if not test_suite:
                print(f"Test suite not found for function {function_name}. Skipping.")
                print("")
                continue
            print(f"Generating tests for {function_name}")

            for test_type in test_suite:
                test_type = int(test_type)
                test_type_txt = test_types[test_type]
                prompt = f'Based on your training, the given solidity function code, function description, and full smart contract code as follows: "{full_smart_contract}", generate a full, ready to run truffle js test file with unit tests for the function based on the test description. CODE ONLY, no accompanying text, no comments, etc. Just output the desired data in the asked format! Do not use any truffle functions not present in truffle npm package (no truffle assertions, etc.), only use the same methodology and libraries as your training files.' + f'Your output should be valid truffle js code that is ready to run without errors. Your function with its body is {function_w_code}, your function description is "{function_comment}" and the test description is "{test_prompts[test_type]}". Make sure to use your understanding of the file as a whole and set up/grant roles to instances, variables, etc as necessary. Remember to only use variables already defined in the contract, or set up variables manually. Do not use variables that have not been initialized, and make sure any dummy data used follows the required solidity format (an address must be a valid address). CODE ONLY. No accompanying text, no comments, etc.  DO NOT USE ANY truffleAssert, chai, or external packages other than the ones in your training! Do not wrap in ``` javascript ```'
                print(f"Generating Tests for {function_name} - {test_type_txt}")
                
                response = chat.send_message(prompt)
                gen_test = response.text
                test_write_path = os.path.join(contract_folder, "Solidify", f"{function_name}_{test_type_txt}_{iteration}.js")
                with open(test_write_path, 'w') as fp:
                    fp.write(gen_test)
    
    except Exception as e:
        print(f"An error with generating tests occurred: {e}")
        sys.exit(1)

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate unit test files for smart contracts.')
    parser.add_argument('training_data_path', type=str, help='Path to the training data folder')
    parser.add_argument('contract_folder', type=str, help='Path to the contract folder')
    parser.add_argument('-t', '--num_tests', type=int, default=2, help='Number of tests to generate per function (default: 2)')
    parser.add_argument('-r', '--repeat_amount', type=int, default=3, help='Number of iterations to run generator (default: 3)')
    args = parser.parse_args()
    REPEAT_AMOUNT = args.repeat_amount
    for iteration in range(REPEAT_AMOUNT):
        chat = model.start_chat(history=[])
        print(f"BEGIN ITERATION {iteration + 1}")
        train_model(args.training_data_path)
        test_generator(args.contract_folder, iteration, args.num_tests)
        print(f"CONCLUDED ITERATION {iteration + 1}")
        print("")