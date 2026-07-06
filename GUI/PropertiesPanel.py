from PySide6.QtWidgets import QTextEdit


class PropertiesPanel(QTextEdit):

    def __init__(self):

        super().__init__()

        self.setMaximumWidth(320)

        self.setReadOnly(True)

        self.show_empty()

    def show_empty(self):

        self.setText(
            "Propiedades\n\n"
            "Aqui apareceran los datos del objeto seleccionado."
        )

    def show_database_details(self, stats, storage_path):

        self.setText(
            "Base de conocimiento\n\n"
            f"Documentos : {stats['documents']}\n"
            f"Reacciones : {stats['reactions']}\n"
            f"Moleculas  : {stats['molecules']}\n"
            f"Espectros  : {stats['spectra']}\n\n"
            "Persistencia\n"
            f"{storage_path}"
        )
