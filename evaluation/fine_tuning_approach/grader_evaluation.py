import json
from Slide2Study.backend.utils import Client
import csv
from time import sleep

base_system_prompt= """You are a grading assistant for educational assessments.

Your task is to grade a student's answer to a question.

Grading scale:
- Grade 3: Correct and complete answer. Uses accurate terminology and fully addresses the question.
- Grade 2: Partially correct or incomplete answer. Shows some understanding but lacks precision, uses vague language, or misses key details.
- Grade 1: Incorrect answer. Contains factual errors, is irrelevant, or demonstrates fundamental misunderstanding.

Respond with only one number: 1, 2, or 3
"""


def prepare_data(csv_filepath):


    data = []
    with open(csv_filepath, 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'question': row['question'],
                'answer': row['answer'],
                'grade': row['grade'].strip()
            })

    print(f"Loaded {len(data)} examples")


    formatted = []
    for item in data:
        user_content = f"""Question:
{item['question']}

Student Answer:
{item['answer']}

Grade this answer."""

        formatted.append({
            "messages": [
                {"role": "system", "content": base_system_prompt},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": item['grade']}
            ]
        })


    split = int(len(formatted) * 0.8)
    train = formatted[:split]
    val = formatted[split:]

    with open('grader_train.jsonl', 'w', encoding='utf-8') as f:
        for item in train:
            f.write(json.dumps(item) + '\n')

    with open('grader_val.jsonl', 'w', encoding='utf-8') as f:
        for item in val:
            f.write(json.dumps(item) + '\n')

    return train, val


def upload_dataset():
    client = Client.getClient()

    with open('grader_train.jsonl', 'rb') as f:
        train_file = client.files.create(file=f, purpose='fine-tune')

    with open('grader_val.jsonl', 'rb') as f:
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
        suffix="answer-grader"
    )

    print(f"Job ID: {job.id}")
    print(f"Status: {job.status}")

    return job.id


prepare_data('questions_answers_graded_train.csv')

train_file_id, val_file_id = upload_dataset

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
