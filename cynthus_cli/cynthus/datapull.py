import json

def create_json_template():
  
    location = input("HuggingFace(H) or Kaggle(K): ")

    if location == 'H':

        template = {
            "dataset_url": "",
            "bucket_name": "your-gcs-bucket",
            "credentials": {
                "huggingface": {
                    "token": "your-huggingface-token"
                }
            }
        }

        with open('configure_huggingface.json', 'w') as f:
            json.dump(template, f, indent=4)

        dataset = input('The URL of the dataset your pulling: ')
        bucket = input('The name of the gcs bucket: ')
        token = input('HuggingFace Token: ')

        update_fields = {
            "dataset_url" : dataset,
            "bucket_name" : bucket
        }

        with open('configure_huggingface.json', 'r+') as f:
            data = json.load(f)

            for field, new_value in update_fields.items():
                data[field] = new_value

            data['credentials']['huggingface']['token'] = token

            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        print('File configure_huggingface.json created successfully!')
    
    elif location == 'K':

        template = {
            "dataset_url": "",
            "bucket_name": "your-gcs-bucket",
            "credentials": {
                "kaggle": {
                    "username": "your-kaggle-username",
                    "key": "your-kaggle-api-key"
                }
            }
        }

        with open('configure_kaggle.json', 'w') as f:
            json.dump(template, f, indent=4)

        dataset = input('The URL of the dataset your pulling: ')
        bucket = input('The name of the gcs bucket: ')
        username = input('Kaggle username: ')
        key = input('Kaggle API Key: ')

        update_fields = {
            "dataset_url" : dataset,
            "bucket_name" : bucket
        }

        with open('configure_kaggle.json', 'r+') as f:
            data = json.load(f)

            for field, new_value in update_fields.items():
                data[field] = new_value

            data['credentials']['kaggle']['username'] = username
            data['credentials']['kaggle']['key'] = key

            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        print('File configure_kaggle.json successfully created!')
    
    else:
        print('Invalid command, please try again')
