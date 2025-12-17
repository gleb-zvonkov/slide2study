from slide2study.backend.utils import Client 
import json
from typing import  Dict, Any
from Slide2Study.backend.contentParser import get_parsed_contents


prompt_summary_generator_generate_and_store_all_notes = """
You are the study summary note creator agent for the Slide2Study system.

Your job:
1. Take lecture materials represented as a list of slides with `index` and `text`.
2. remove obvious headers/footers, slide numbers, teacher/class information).
3. group the content into coherent topics.
4. for each topic, produce:
   - `topic_id`: a short stable identifier string (e.g., "lec03_t01", "lec03_t02").
   - `title`: a concise, human-readable title.
   - `summary`: Generate a single, coherent set of summary study notes in plain text for this topic. These notes should be something a student can read directly to understand and review this specific topic.
   - `source_spans`: a list of objects like { "slide_index": <int> } showing which slides this topic comes from.
   - `key_terms`: 3–10 important technical terms or concepts from this topic.
   - `raw_text`: cleaned, merged teaching text from the relevant slides.
5. make sure all of the important slides text should be used, do not remove any content

Constraints:
1 do not invent new concepts that are not in the slides.
2 you may rephrase and summarize, but keep content faithful to the slides.
3 Write summary in clear, student-friendly language.
4 always output a single JSON object that strictly matches the following schema:

{
  "course_id": "<string>",
  "material_id": "<string>",
  "topics": [
    {
      "topic_id": "<string>",
      "title": "<string>",
      "summary": "<string>",
      "source_spans": [ { "slide_index": <int> }, ... ],
      "key_terms": ["<string>", ...],
      "raw_text": "<string>"
    },
    ...
  ]
}

Never include explanations outside of this JSON. No markdown, no comments.
    """.strip()



prompt_summary_generator_generate_single_note_using_parsed_slide_text = """
Task:
You will be given parsed text from one lecture slide. Your job is to produce a concise, faithful summary of the slide’s content.


Input:
- A block of text extracted directly from a single lecture slide.
- This text may contain headers, footers, slide numbers, or instructor/course labels.


Output:
- A single plain-text summary that captures all essential concepts from the slide.
- The summary must be written in clear, student-friendly language.
- Output ONLY the summary text with no headings, labels, explanations, or extra commentary.


Requirements:
1. Remove irrelevant elements such as headers, footers, slide numbers, and instructor or course information.
2. Do NOT invent new facts, examples, or interpretations not present in the slide.
3. You may rephrase, condense, and reorganize, but all important information from the slide must be preserved.
4. The summary should be short, coherent, and directly helpful for a student trying to understand the slide.


Always output only the summary.
""".strip()




def generate_and_store_all_notes(client, course_id, material_id, model="gpt-4.1"):
    slides = get_parsed_contents("/home/mohammadrezasabramooz/Documents/Slide2Study_main/Slide2Study/backend/1.pdf", "ANA200",
                                 "Introduction to HistologyOrdinary Connective Tissue, Cartilage and Bone")
    # put slides into a JSON payload
    user_payload: Dict[str, Any] = {
        "course_id": course_id,
        "material_id": material_id,
        "slides": [
            {"index": s.index, "text": s.text}
            for s in slides
        ],
    }

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": prompt_summary_generator_generate_and_store_all_notes,
            },
            {
                "role": "user",
                "content": json.dumps(user_payload),
            },
        ],
        max_output_tokens=4000,
    )

    raw_json = response.output_text
    note = json.loads(raw_json)
    with open("/home/mohammadrezasabramooz/Documents/Slide2Study_main/Slide2Study/backend/StoredContents/" + course_id + "_" + material_id + ".txt", "w", encoding="utf-8") as f:
        json.dump(note, f, ensure_ascii=False, indent=2)
    return note




def generate_single_note_based_on_given_slide_text(client,slide_text,model="gpt-4.1"):
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": prompt_summary_generator_generate_single_note_using_parsed_slide_text,
            },
            {
                "role": "user",
                "content": slide_text,
            },
        ],
        max_output_tokens=4000,
    )

    return response.output_text

# generate_note(Client.getClient(),"ANA200","Introduction to HistologyOrdinary Connective Tissue, Cartilage and Bone")

#print(generate_single_note_based_on_given_slide_text(Client.getClient(),"Bone Composition: Matrix\nAbout one third organic matter (osteoid): about 90% is collagen fibers, about 10% is ground substance (adhesive glycoproteins and proteoglycans). Organic components impart tensile strength and flexibility to bone. Osteoid becomes mineralized in the process of matrix formation. About two thirds inorganic matter: osteoid is mineralized largely by calcium, also phosphate, bicarbonate, citrate, magnesium, potassium, sodium. Mineralization gives bone compressional strength. Hydrated mineral crystals allow exchange of electrolytes with blood and enable bone tissue to act as a mineral reservoir."))