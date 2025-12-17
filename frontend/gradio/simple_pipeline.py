from Slide2Study.backend.noteGenerator import generate_and_store_all_notes
from Slide2Study.backend.utils import Client
from Slide2Study.backend.questionGenerator import question_generator_prompt
from Slide2Study.backend.gradeGenerator import grade_generator_prompt

notes = generate_and_store_all_notes(Client.getClient(),"ANA200","Introduction to HistologyOrdinary Connective Tissue, Cartilage and Bone")

topic_ids = []
summaries = []
raw_texts = []

notes  = notes["topics"]
for note in notes:
    topic_ids.append(note["topic_id"])
    summaries.append(note["summary"])
    raw_texts.append(note["raw_text"])

print(len(topic_ids))
print(len(summaries))
print(len(raw_texts))

levels_questions = ['remember','understand','apply']
i=0
for topic_id in topic_ids:
    print("Current topic is: ",topic_id)
    print("---------------------------------------------------")
    print("Here is summary for reading:")
    print(summaries)
    print("---------------------------------------------------")
    for level in levels_questions:
        question = Client.getClient().responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "system",
                    "content": question_generator_prompt
                },
                {
                    "role": "user",
                    "content": (
                        f"Slide text:\n{raw_texts[i]}\n\n"
                        f"Level: {level}"
                    )
                }
            ],max_output_tokens=4000,
        )
        print(question.output_text)
        answer = input("Enter your answer: ")
        response = Client.getClient().responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "system",
                    "content": grade_generator_prompt
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n"
                        f"Student Answer: {answer}\n\n"
                        "Evaluate correctness and explain why."
                    )
                }
            ],max_output_tokens=4000,
        )
        print("Your answer evaluation is:")
        print(response.output_text)
        i=i+1



