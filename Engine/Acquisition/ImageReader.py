from Engine.Acquisition.Reader import Reader


class ImageReader(Reader):

    def load(self, filepath):

        document = self.create_document(filepath, "Image")

        print("\nImagen cargada correctamente.")

        return document