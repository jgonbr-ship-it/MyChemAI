from Engine.Logger import Logger
from Engine.Models.ChemicalReaction import ChemicalReaction


class ReactionParser:

    def parse(self, document, schema):

        if "Reaction" not in schema:

            Logger.info("No se encontraron columnas de reaccion.")

            return []

        if len(document.tables) == 0:

            Logger.info("El documento no contiene tablas para analizar.")

            return []

        reactions = []

        dataframe = document.tables[0]

        reaction_columns = schema["Reaction"]

        for column in reaction_columns:

            if column not in dataframe.columns:

                continue

            for reaction_string in dataframe[column]:

                if not isinstance(reaction_string, str):

                    continue

                reaction_string = reaction_string.strip()

                if ">>" not in reaction_string:

                    continue

                reaction = ChemicalReaction()

                left, right = reaction_string.split(">>", 1)

                self.add_side(left, reaction.add_reactant)

                self.add_side(right, reaction.add_product)

                if len(reaction.reactants) > 0 or len(reaction.products) > 0:

                    reactions.append(reaction)

        Logger.info(f"Reacciones extraidas: {len(reactions)}")

        return reactions

    def add_side(self, side, add_molecule):

        for smiles in side.split("."):

            smiles = smiles.strip()

            if smiles:

                add_molecule(smiles)
