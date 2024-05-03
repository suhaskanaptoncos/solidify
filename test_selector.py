import os
import re
import json
import sys
import argparse

def is_valid_list(input_str):
  try:
    pattern = r"^(-?\d+,?)+$"
    if not input_str:
        return False
    match = re.match(pattern, input_str)
    return match is not None
  except Exception as e:
    print(f"An error occurred with determining input validity: {e}. Please try again.")
    return False

def test_selector(contract_folder):
    try:
        output_file_path = os.path.join(contract_folder, 'Solidify', 'analysis_output.json')
        tests = {}
        flag = False
    except Exception as e:
        print(f"An error with reading the analysis_output.json file occurred: {e}")
        sys.exit(1)

    try:
        with open(output_file_path, 'r') as fp:
            data = json.load(fp)

        for func in data:
            print(f"for the function titled {func['function name']}, which tests do you want to run?")
            print("Enter a comma separated list of the test codes you want to run, with no spaces, for example: 1,2,3")
            print("Enter just 0 to run all tests, -2 to run all tests for all files, -3 to skip and enter -1 to exit")
            print("The test options are 1 - Functionality tests, 2 - Authorization tests, and 3 - Input Tests")
            if not flag:
                user_input = input("Enter here and press enter: ")
                if user_input == "-1":
                    break
                if user_input == "-2":
                    flag = True
                if user_input == "-3":
                    print("Skipping")
                    continue
            if flag or is_valid_list(user_input):
                if flag:
                    user_input = "1,2,3"
                elif user_input == "0":
                    user_input = "1,2,3"
                user_input = user_input.split(",")
                tests[func['function name']] = user_input
                print("Thank you, continuing to the next function\n\n")
            else:
                print("Invalid input. Please try again.")
                break

        with open(f"{os.path.join(contract_folder, 'Solidify')}/test_suites.json", "w") as json_fp:
            json.dump(tests, json_fp)

    except Exception as ex:
        print("An error occurred with selecting a test. Please try again" + str(ex))
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Selects test for test generator.')
    parser.add_argument('contract_folder', type=str, help='Path to the contract folder with Solidify folder inside, ex. "sample_contracts/CarMileageTracker"')
    args = parser.parse_args()
    test_selector(args.contract_folder)