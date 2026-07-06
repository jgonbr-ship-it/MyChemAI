from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLabel,
    QGroupBox,
    QVBoxLayout
)


class DocumentInspector(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        info_group = QGroupBox("Información del documento")

        self.form = QFormLayout()

        self.name = QLabel("-")
        self.type = QLabel("-")
        self.source = QLabel("-")
        self.pages = QLabel("0")
        self.paragraphs = QLabel("0")
        self.tables = QLabel("0")
        self.images = QLabel("0")
        self.reactions = QLabel("0")
        self.molecules = QLabel("0")

        self.form.addRow("Nombre:", self.name)
        self.form.addRow("Tipo:", self.type)
        self.form.addRow("Origen:", self.source)
        self.form.addRow("Páginas:", self.pages)
        self.form.addRow("Párrafos:", self.paragraphs)
        self.form.addRow("Tablas:", self.tables)
        self.form.addRow("Imágenes:", self.images)
        self.form.addRow("Reacciones:", self.reactions)
        self.form.addRow("Moléculas:", self.molecules)

        info_group.setLayout(self.form)

        layout.addWidget(info_group)

        layout.addStretch()

    def update_document(self, document):

        self.name.setText(document.name)

        self.type.setText(document.type)

        self.source.setText(document.source)

        self.pages.setText(str(len(document.raw.pages)))

        self.paragraphs.setText(str(len(document.raw.paragraphs)))

        self.tables.setText(str(len(document.raw.tables)))

        self.images.setText(str(len(document.raw.images)))

        self.reactions.setText(str(len(document.reactions)))

        self.molecules.setText(str(len(document.molecules)))