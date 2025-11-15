from unstructured.partition.pdf import partition_pdf
from collections import defaultdict
from classes.ParsedSlides import ParsedSlide
from typing import List



# parse slides contents using partition_pdf library
def get_slides(slide_name) -> List[ParsedSlide]:
    elements = partition_pdf(
        filename=slide_name,
        strategy="hi_res",
        chunking_strategy=None,
        ocr_languages="eng")

    page_texts = defaultdict(list)

    for element in elements:
        page_num = getattr(element.metadata, "page_number", None)
        if page_num is None:
            continue

        page_texts[page_num].append(str(element))

    slides: List[ParsedSlide] = []
    for page_num in sorted(page_texts.keys()):
        merged_text = "\n".join(page_texts[page_num])
        slides.append(ParsedSlide(index=page_num, text=merged_text))

    return slides








