import gradio as gr
from Slide2Study.backend.noteGenerator import generate_and_store_all_notes
from Slide2Study.backend.utils import Client
from Slide2Study.backend.questionGenerator import question_generator_prompt
from Slide2Study.backend.gradeGenerator import grade_generator_prompt

bloom_levels = ['remember', 'understand', 'apply']

# states
topics = []
current_topic_idx = 0
current_level_idx = 0
current_question = ""


def reset_state():
    global topics, current_topic_idx, current_level_idx, current_question
    topics = []
    current_topic_idx = 0
    current_level_idx = 0
    current_question = ""


def load_notes(course_code, lecture_title):
    global topics

    if not course_code.strip() or not lecture_title.strip():
        return "Please enter both course code and lecture title to load Slides.", "", gr.update(visible=False)

    try:
        reset_state()

        result = generate_and_store_all_notes(
            Client.getClient(),
            course_code.strip(),
            lecture_title.strip()
        )

        topics = result.get("topics", [])

        if not topics:
            return "No topics found. Check your input.", "", gr.update(visible=False)

        return (
            f"Loaded {len(topics)} topics successfully.",
            get_current_summary(),
            gr.update(visible=True)
        )
    except Exception as e:
        return f"Error: {str(e)}", "", gr.update(visible=False)


def get_current_summary():
    if not topics:
        return "No topics loaded."

    topic = topics[current_topic_idx]
    level = bloom_levels [current_level_idx]

    return f"""**Topic {current_topic_idx + 1} of {len(topics)}: {topic['topic_id']}**

**Current Level:** {level.capitalize()} ({current_level_idx + 1}/3)

---

**Summary:**

{topic['summary']}
"""


def is_completed():
    return (current_topic_idx == len(topics) - 1 and (current_level_idx == len(bloom_levels ) - 1) and current_question != "")


def generate_question():
    global current_question

    if not topics:
        return "Load notes first."

    # Skip if already completed
    if is_completed():
        return "Congratulations! You have completed all topics and levels."

    topic = topics[current_topic_idx]
    level = bloom_levels [current_level_idx]

    try:
        response = Client.getClient().responses.create(
            model="gpt-4.1",
            input=[
                {"role": "system", "content": question_generator_prompt},
                {"role": "user", "content": f"Slide text:\n{topic['raw_text']}\n\nLevel: {level}"}
            ],
            max_output_tokens=4000
        )

        current_question = response.output_text
        return f"**Question ({level.capitalize()}):**\n\n{current_question}"

    except Exception as e:
        return f"Error generating question: {str(e)}"


def grade_answer(student_answer):
    if not current_question:
        return "Generate a question first."

    if not student_answer.strip():
        return "Please enter an answer."

    try:
        response = Client.getClient().responses.create(
            model="gpt-4.1",
            input=[
                {"role": "system", "content": grade_generator_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Question: {current_question}\n"
                        f"Student Answer: {student_answer}\n\n"
                        "Evaluate correctness and explain why."
                    )
                }
            ],
            max_output_tokens=4000
        )

        return f"**Evaluation:**\n\n{response.output_text}"

    except Exception as e:
        return f"Error grading answer: {str(e)}"


def go_next():
    global current_topic_idx, current_level_idx, current_question

    if not topics:
        return get_current_summary(), "Generating question...", ""

    current_level_idx += 1

    if len(bloom_levels)<=current_level_idx:
        current_level_idx = 0
        current_topic_idx += 1

        if len(topics)<=current_topic_idx:
            current_topic_idx = len(topics) - 1
            current_level_idx = len(bloom_levels ) - 1
            return (
                get_current_summary(),
                "Congratulations! You have completed all topics and levels.",
                ""
            )

    current_question = ""
    return get_current_summary(), "Generating question...", ""


with gr.Blocks(title="Slide2Study", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Slide2Study")
    gr.Markdown("ECE1786 Course Project")

    gr.Markdown("---")
    gr.Markdown("### Setup")

    with gr.Row():
        course_input = gr.Textbox(label="Course Code")
        lecture_input = gr.Textbox(label="Lecture Title")

    load_btn = gr.Button("Load Notes", variant="primary")
    status_text = gr.Markdown("")

    gr.Markdown("---")
    gr.Markdown("### Study Session")

    summary_text = gr.Markdown("")

    with gr.Group(visible=False) as study_section:
        question_text = gr.Markdown("")

        answer_input = gr.Textbox(
            label="Your Answer",
            placeholder="Type your answer here...",
            lines=4
        )

        submit_btn = gr.Button("Submit Answer", variant="primary")
        evaluation_text = gr.Markdown("")

    # handeling events
    load_btn.click(
        fn=lambda: "Loading notes, please wait...",
        inputs=[],
        outputs=[status_text]
    ).then(
        fn=load_notes,
        inputs=[course_input, lecture_input],
        outputs=[status_text, summary_text, study_section]
    ).then(
        fn=lambda: "Generating question...",
        inputs=[],
        outputs=[question_text]
    ).then(
        fn=generate_question,
        inputs=[],
        outputs=[question_text]
    )

    submit_btn.click(
        fn=lambda: "Evaluating your answer...",
        inputs=[],
        outputs=[evaluation_text]
    ).then(
        fn=grade_answer,
        inputs=[answer_input],
        outputs=[evaluation_text]
    ).then(
        fn=go_next,
        inputs=[],
        outputs=[summary_text, question_text, answer_input]
    ).then(
        fn=generate_question,
        inputs=[],
        outputs=[question_text]
    )




demo.launch()