from PySide6.QtWidgets import QTextEdit


class Workspace(QTextEdit):

    def __init__(self):

        super().__init__()

        self.setReadOnly(True)

        self.show_welcome()

    def show_welcome(self):

        self.setText(
            "Bienvenido a MyChemAI\n\n"
            "Workspace principal."
        )

    def show_database_summary(self, stats):

        self.setText(
            "MyChemAI\n\n"
            "Base de conocimiento activa\n\n"
            f"Documentos : {stats['documents']}\n"
            f"Reacciones : {stats['reactions']}\n"
            f"Moleculas  : {stats['molecules']}\n"
            f"Espectros  : {stats['spectra']}\n\n"
            "El conocimiento importado queda estructurado para busqueda, "
            "analisis y futuras capas de IA."
        )
