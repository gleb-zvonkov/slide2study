
from Slide2Study.backend.utils import PDFParser




def get_parsed_contents(input_file,course_id,material_id):

    # parse text of slides from slides
    slides_parsed = PDFParser.get_slides(input_file)

    return slides_parsed



