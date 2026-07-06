import re


class TextNormalizer:

    def normalize(self, text):

        if not text:
            return ""

        # Normaliza saltos de línea
        text = text.replace("\r", "\n")

        # Une palabras cortadas por guion al final de línea
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

        # Convierte saltos simples en espacios
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

        # Colapsa múltiples espacios
        text = re.sub(r"[ \t]+", " ", text)

        # Máximo dos saltos consecutivos
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()