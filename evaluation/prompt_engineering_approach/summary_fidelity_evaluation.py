from Slide2Study.backend.utils import Client
from Slide2Study.backend.noteGenerator import generate_note

def check_fidelity(note, raw_text):

    client = Client.getClient()

    prompt = f"""You are a fidelity evaluator for educational content. Your task is to determine if a generated sentence is factually consistent with the source text.

    Source Text:
    {raw_text}

    Generated Sentence:
    {note}

    Evaluate the sentence by following these steps:

    Step 1 - Identify key claims: List the main factual claims made in the generated sentence.

    Step 2 - Check each claim: For each claim, determine if it is:
      - supported: Directly stated or clearly implied in the source
      - not found: Information not present in the source 

    STEP 3 : 
      - If ALL claims are SUPPORTED then  fidelity
      - If any claim is not found then infidelity

    Output is: Just fidelity or infidelity"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()


summaries = []
raw_texts = []

for i in range(3):
    note = generate_note(Client.getClient(),"ANA200","Introduction to HistologyOrdinary Connective Tissue, Cartilage and Bone")
    for topic in note["topics"]:
        summaries.append(topic["summary"])
        raw_texts.append(topic["raw_text"])

count=0
correct=0
for summary in summaries:
    result=check_fidelity(summary,raw_texts[count])

    if result=="fidelity":
        correct=correct+1
    count = count+1


print("Accuracy is:")
print(correct/count)