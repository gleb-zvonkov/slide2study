import json
import random
import csv
from Slide2Study.backend.utils import Client
from time import sleep


base_system_prompt = """You are a fidelity evaluator for educational content.

Your task is to determine if a generated note is factually consistent with the source text.

Rules:
- Output "fidelity" if the note is supported by or consistent with the source text
- Output "infidelity" if the note contradicts, distorts, or adds information not in the source
- Be strict: the note must be supported by the specific source provided

Respond with only one word: yes or no"
"""



def prepare_data(csv_filepath):

    data = []
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'text': row['text'],
                'summary': row['summary'].lower().strip(),
                'fidelity': row['fidelity'].lower().strip()
            })

    formatted = []
    for item in data:
        user_content = f"""Source Text:
{item['text']}

Generated note:
{item['summary']}

Is this note faithful to the source text?"""

        formatted.append({
            "messages": [
                {"role": "system", "content": base_system_prompt},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": item['fidelity']}
            ]
        })

    random.shuffle(formatted)
    split = int(len(formatted) * 0.8)
    train = formatted[:split]
    val = formatted[split:]

    with open('fidelity_train.jsonl', 'w', encoding='utf-8') as f:
        for item in train:
            f.write(json.dumps(item) + '\n')

    with open('fidelity_val.jsonl', 'w', encoding='utf-8') as f:
        for item in val:
            f.write(json.dumps(item) + '\n')


    return train, val


def upload_dataset():

    client = Client.getClient()

    with open('fidelity_train.jsonl', 'rb') as f:
        train_file = client.files.create(file=f, purpose='fine-tune')

    with open('fidelity_val.jsonl', 'rb') as f:
        val_file = client.files.create(file=f, purpose='fine-tune')

    print(f"Train file ID: {train_file.id}")
    print(f"Val file ID: {val_file.id}")

    return train_file.id, val_file.id


def create_dataset(train_file_id, val_file_id):

    client = Client.getClient()

    job = client.fine_tuning.jobs.create(
        training_file=train_file_id,
        validation_file=val_file_id,
        model="gpt-4.1-2025-04-14",
        hyperparameters={"n_epochs": 3},
        suffix="fidelity-evaluator"
    )

    print(f"Job ID: {job.id}")
    print(f"Status: {job.status}")

    return job.id

def create_job(train_file_id, val_file_id):

    client = Client.getClient()

    job = client.fine_tuning.jobs.create(
        training_file=train_file_id,
        validation_file=val_file_id,
        model="gpt-4.1-2025-04-14",
        hyperparameters={"n_epochs": 3},
        suffix="fidelity-evaluator"
    )

    print(f"Job ID: {job.id}")
    print(f"Status: {job.status}")

    return job.id


prepare_data('fidelity_train.csv')
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
