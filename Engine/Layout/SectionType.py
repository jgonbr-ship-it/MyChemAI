from enum import Enum


class SectionType(Enum):

    TITLE = "Title"

    ABSTRACT = "Abstract"

    KEYWORDS = "Keywords"

    INTRODUCTION = "Introduction"

    BACKGROUND = "Background"

    EXPERIMENTAL = "Experimental"

    MATERIALS = "Materials"

    METHODS = "Methods"

    RESULTS = "Results"

    DISCUSSION = "Discussion"

    CONCLUSION = "Conclusion"

    ACKNOWLEDGEMENTS = "Acknowledgements"

    REFERENCES = "References"

    SUPPORTING_INFORMATION = "Supporting Information"

    UNKNOWN = "Unknown"