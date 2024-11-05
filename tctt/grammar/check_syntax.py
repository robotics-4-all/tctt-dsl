from textx import metamodel_from_file

# Load your grammar from a .tx file
meta_model = metamodel_from_file('syntax/tctt.tx')

# Parse the file to be validated
try:
    model = meta_model.model_from_file('examples/test.txt')
    print("Syntax is valid!")
except Exception as e:
    print(f"Syntax Error: {e}")