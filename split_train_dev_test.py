import json

test_set_ids = "testListFile.txt"
dev_set_ids = "valListFile.txt"
original_data = "output.json"



with open(test_set_ids, "r", encoding="utf-8") as test_set_file:
    with open(dev_set_ids, "r", encoding="utf-8") as dev_set_file:
        with open(original_data, "r", encoding="utf-8") as original_data_file:
            list_of_test_set_ids = test_set_file.read().splitlines()
            list_of_dev_set_ids = dev_set_file.read().splitlines()
            list_of_original_data = json.load(original_data_file)

            with open("./data/train.json", "w+", encoding="utf-8") as train:
                with open("./data/dev.json", "w+", encoding="utf-8") as dev:
                    with open("./data/test.json", "w+", encoding="utf-8") as test:
                        to_add_to_train = {}
                        to_add_to_dev = {}
                        to_add_to_test = {}

                        for original_conv in list_of_original_data:
                            if original_conv in list_of_dev_set_ids:
                                to_add_to_dev[original_conv] = list_of_original_data[original_conv]
                            elif original_conv in list_of_test_set_ids:
                                to_add_to_test[original_conv] = list_of_original_data[original_conv]
                            else:
                                to_add_to_train[original_conv] = list_of_original_data[original_conv]
                        train.write(json.dumps(to_add_to_train))
                        dev.write(json.dumps(to_add_to_dev))
                        test.write(json.dumps(to_add_to_test))

