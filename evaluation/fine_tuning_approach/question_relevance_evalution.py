import csv
import json
import random
from Slide2Study.backend.utils import Client
from time import sleep


base_system_prompt = """You are a question relevance evaluator for educational content.

Your task is to determine if a question is related to source text.

Rules:
- Output "relevance" if  information is directly supported by the slide text
- Output "irrelevance" if the question cannot be answered from the source text, or asks about topics not covered in the source

Respond with only one word: "relevance" or "irrelevance"
"""


def prepare_data(csv_filepath):


    data = []
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'text': row['text'],
                'question': row['question'],
                'label': row['label'].strip().lower()
            })

    formatted = []
    for item in data:
        user_content = f"""Source Text:
{item['text']}

Question:
{item['question']}

Is this question from given source?"""

        formatted.append({
            "messages": [
                {"role": "system", "content": base_system_prompt},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": item['label']}
            ]
        })

    random.shuffle(formatted)
    split = int(len(formatted) * 0.8)
    train = formatted[:split]
    val = formatted[split:]

    with open('relevance_train.jsonl', 'w', encoding='utf-8') as f:
        for item in train:
            f.write(json.dumps(item) + '\n')

    with open('relevance_val.jsonl', 'w', encoding='utf-8') as f:
        for item in val:
            f.write(json.dumps(item) + '\n')


    return train, val


def upload_dataset():

    client = Client.getClient()

    with open('relevance_train.jsonl', 'rb') as f:
        train_file = client.files.create(file=f, purpose='fine-tune')

    with open('relevance_val.jsonl', 'rb') as f:
        val_file = client.files.create(file=f, purpose='fine-tune')

    return train_file.id, val_file.id


def create_job(train_file_id, val_file_id):

    client = Client.getClient()

    job = client.fine_tuning.jobs.create(
        training_file=train_file_id,
        validation_file=val_file_id,
        model="gpt-4.1-2025-04-14",
        hyperparameters={"n_epochs": 3},
        suffix="question-relevance"
    )

    print(f"Job ID: {job.id}")
    print(f"Status: {job.status}")

    return job.id


prepare_data('relevance_train.csv')

train_file_id, val_file_id = upload_dataset()

job_id = create_job(train_file_id, val_file_id)

print(job_id)

while True:
    job = Client.getClient().fine_tuning.jobs.retrieve(job_id)
    print("Status:", job.status)

    if job.status in ["succeeded", "failed", "cancelled"]:
        break

    sleep(5)

print("Final status:", job.status)
print("Fine-tuned model:", job.fine_tuned_model)