class Reaction:

    def __init__(self, reactants, products, label=None):
        self.reactants = reactants
        self.products = products
        self.label = label

    def show(self):
        print("\n==============================")
        print("REACTION")
        print("==============================")

        print("Reactivos:")
        print(self.reactants)

        print("\nProductos:")
        print(self.products)

        print("\nEtiqueta:")
        print(self.label)