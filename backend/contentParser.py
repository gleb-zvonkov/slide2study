
from utils import Client,PDFParser
import json
from typing import  Dict, Any



prompt = """
You are the Content Parser Agent for the Slide2Study system.

Your job:
1. Take lecture materials represented as a list of slides with `index` and `text`.
2. remove obvious headers/footers, slide numbers, etc.).
3. Group the content into coherent topics.
4. For each topic, produce:
   - `topic_id`: a short stable identifier string (e.g., "lec03_t01", "lec03_t02").
   - `title`: a concise, human-readable title.
   - `summary`: 1–3 sentences describing what is taught in this topic.
   - `source_spans`: a list of objects like { "slide_index": <int> } showing which slides this topic comes from.
   - `key_terms`: 3–10 important technical terms or concepts from this topic.
   - `raw_text`: cleaned, merged teaching text from the relevant slides.
5. Make sure all of the important slides text should be used, do not remove any content

Constraints:
- Do not invent new concepts that are not in the slides.
- You may rephrase and summarize, but keep content faithful to the slides.
- Always output a single JSON object that strictly matches the schema:

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




def call_content_parser_agent(parser_client, course_id, material_id, slides, model="gpt-4.1-mini", ) -> Dict[str, Any]:
    # put slides into a JSON payload
    user_payload: Dict[str, Any] = {
        "course_id": course_id,
        "material_id": material_id,
        "slides": [
            {"index": s.index, "text": s.text}
            for s in slides
        ],
    }

    response = parser_client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": json.dumps(user_payload),
            },
        ],
        max_output_tokens=4000,
    )

    raw_json = response.output_text
    parsed = json.loads(raw_json)

    return parsed




def get_parsed_contents(input_file,course_id,material_id):

    client = Client.getClient()
    # parse text of slides from slides
    slides_parsed = PDFParser.get_slides(input_file)

    for slide in slides_parsed:
        print(slide.text)
    parsed_json = call_content_parser_agent(client,course_id=course_id,material_id=material_id,slides=slides_parsed,model="gpt-4.1-mini")

    with open(course_id+"_"+material_id+".txt", "w", encoding="utf-8") as f:
        json.dump(parsed_json, f, ensure_ascii=False, indent=2)




get_parsed_contents("1.pdf","ANA200","Introduction to HistologyOrdinary Connective Tissue, Cartilage and Bone")

