from Engine.Logger import Logger
from Engine.Processors.Processor import Processor


class PipelineManager:

    def __init__(self, processors=None):

        self.processors = []

        for processor in processors or []:

            self.add_processor(processor)

    # ===================================

    def add_processor(self, processor):

        if not isinstance(processor, Processor):

            raise TypeError("Todos los processors deben heredar de Processor.")

        self.processors.append(processor)

    # ===================================

    def run(self, document):

        for processor in self.processors:

            Logger.info(f"Pipeline: {processor.name}")

            document = processor.process(document)

            if document is None:

                Logger.info(f"Pipeline detenido por {processor.name}.")

                return None

        return document
