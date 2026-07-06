import pandas as pd
from Engine.reaction import Reaction


class DataEngine:

    def __init__(self):
        print("=================================")
        print(" MyChemAI Data Engine iniciado")
        print("=================================")

    def import_csv(self, path):

        try:
            df = pd.read_csv(path)

            print("\nArchivo cargado correctamente.\n")

            print(f"Filas: {len(df)}")
            print(f"Columnas: {len(df.columns)}")

            print("\nColumnas encontradas:")

            for column in df.columns:
                print(f" - {column}")

            print("\nCreando primer objeto Reaction...\n")

            reaction = Reaction(
                reactants=df.iloc[0]["Original_reaction"],
                products=df.iloc[0]["Updated_reaction"],
                label=df.iloc[0]["Label"]
            )

            reaction.show()

            return df

        except Exception as e:
            print(e)
            return None
