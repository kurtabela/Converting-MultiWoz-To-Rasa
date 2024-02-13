# Translating MultiWoz

## Step 1: Create a single JSON files with all the train/dev/test files
This can be done via the file `split_train_dev_test.py` by calling `convert_multiwoz_to_csv()`. The file is a python script that takes in the MultiWoz dataset and creates a single JSON file with all the train/dev/test files.

## Step 2: Convert MultiWoz to CSV
This can be done via the file `json_to_csv.py`. The file is a python script that takes in the JSON file and converts it to a CSV file.

## Step 3: Translate
We can automatically translate the sentences using Google Translate

## Step 4: Convert CSV to the original JSON Format
This can be done via the file `split_train_dev_test.py` by calling `convert_csv_to_multiwoz()`. The file is a python script that takes in the MultiWoz dataset and creates a single JSON file with all the train/dev/test files.

## Step 5: Convert this new JSON file to Rasa format
This can be done via the file `multidomain_rasa.py`. The file is a python script that takes in the JSON file and converts it to the Rasa format.



