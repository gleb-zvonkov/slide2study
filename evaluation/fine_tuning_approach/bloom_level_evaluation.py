import csv
import json
import random
from Slide2Study.backend.utils import Client
from time import sleep

base_system_prompt = """You are a bloom's Taxonomy classifier for educational questions.

Classify questions into one of three cognitive levels:

1. remember - recall facts, definitions, lists

2. understand - explain, describe, compare concepts

3. apply - use knowledge in new situations, predict, design, solve

Give output with only one word: "remember", "understand", or "apply"
"""


def prepare_data(csv_filepath):

    data = []
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'question': row['question'],
                'label': row['label'].lower().strip()
            })



    formatted = []
    for item in data:
        formatted.append({
            "messages": [
                {"role": "system", "content": base_system_prompt},
                {"role": "user", "content": item['question']},
                {"role": "assistant", "content": item['label']}
            ]
        })


    random.shuffle(formatted)
    split = int(len(formatted) * 0.8)
    train = formatted[:split]
    val = formatted[split:]


    with open('bloom_train.jsonl', 'w', encoding='utf-8') as f:
        for item in train:
            f.write(json.dumps(item) + '\n')

    with open('bloom_val.jsonl', 'w', encoding='utf-8') as f:
        for item in val:
            f.write(json.dumps(item) + '\n')


    return train, val


def upload_dataset():
    client = Client.getClient()

    with open('bloom_train.jsonl', 'rb') as f:
        train_file = client.files.create(file=f, purpose='fine-tune')

    with open('bloom_val.jsonl', 'rb') as f:
        val_file = client.files.create(file=f, purpose='fine-tune')

    print(f"Train file ID: {train_file.id}")
    print(f"Val file ID: {val_file.id}")

    return train_file.id, val_file.id


def create_job(train_file_id, val_file_id):

    client = Client.getClient()

    job = client.fine_tuning.jobs.create(
        training_file=train_file_id,
        validation_file=val_file_id,
        model="gpt-4.1-2025-04-14",
        hyperparameters={"n_epochs": 3},
        suffix="bloom-classifier"
    )

    print(f"Job ID: {job.id}")
    print(f"Status: {job.status}")

    return job.id


# load train dataset
prepare_data('questions_bloom_train.csv')
# upload dataset to OpenAI
train_file_id, val_file_id = upload_dataset()

# request fine tuning
job_id = create_job(train_file_id, val_file_id)

print(job_id)

# check training status every 5 seconds
while True:
    job = Client.getClient().fine_tuning.jobs.retrieve(job_id)
    print("Status:", job.status)

    if job.status in ["succeeded", "failed", "cancelled"]:
        break

    sleep(5)

print("Final status:", job.status)
print("Fine-tuned model:", job.fine_tuned_model)
