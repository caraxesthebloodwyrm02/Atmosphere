# Import required libraries
import time
from typing import List, Dict, Optional

# View 1: High-level view - Make a sandwich
def make_sandwich():
    """Main function to make a sandwich."""
    print("=== Making a Sandwich ===")
    
    # View 2: Process view
    ingredients = gather_ingredients()
    
    # View 3: Detailed preparation
    prepared = prepare_ingredients(ingredients)
    
    # View 4: Integration and execution
    sandwich = assemble_sandwich(prepared)
    
    # Final output
    print("\n=== Sandwich Complete! ===")
    print(f"Enjoy your {', '.join(sandwich['layers'])} sandwich!")
    return sandwich

# View 2: Gather ingredients
def gather_ingredients() -> Dict[str, List[str]]:
    """Gather all necessary ingredients."""
    print("\nGathering ingredients...")
    
    ingredients = {
        'bread': ['whole wheat', 'sourdough'],
        'spreads': ['mustard', 'peanut butter'],
        'fillings': ['lettuce', 'tomato', 'cheese']
    }
    
    for category, items in ingredients.items():
        print(f"- {category.title()}: {', '.join(items)}")
    
    return ingredients

# View 3: Prepare ingredients
def prepare_ingredients(ingredients: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Prepare the gathered ingredients."""
    print("\nPreparing ingredients...")
    
    prepared = {'slices': [], 'spreads': []}
    
    # Prepare bread
    for bread in ingredients['bread']:
        print(f"- Slicing {bread} bread")
        prepared['slices'].append(f"sliced {bread}")
    
    # Prepare spreads
    for spread in ingredients['spreads']:
        print(f"- Getting {spread} ready")
        prepared['spreads'].append(spread)
    
    # Prepare fillings
    prepared['fillings'] = [f"fresh {item}" for item in ingredients['fillings']]
    print("- Washing and preparing vegetables")
    
    return prepared

# View 4: Assemble the sandwich
def assemble_sandwich(prepared: Dict[str, List[str]]) -> Dict:
    """Assemble all prepared ingredients into a sandwich."""
    print("\nAssembling sandwich...")
    
    # Take two slices of bread
    if len(prepared['slices']) >= 2:
        base = prepared['slices'][0]
        top = prepared['slices'][1]
    else:
        base = top = "sliced bread"
    
    # Apply spreads
    spread_text = " and ".join(prepared['spreads']) if prepared['spreads'] else "nothing"
    print(f"- Spreading {spread_text} on {base}")
    
    # Add fillings
    print("- Adding fillings:")
    for filling in prepared.get('fillings', []):
        print(f"  - {filling}")
    
    # Toast the sandwich
    print("- Toasting for 3 minutes...")
    time.sleep(1)  # Simulate toasting time
    
    # Final assembly
    print(f"- Placing {top} on top")
    
    return {
        'base': base,
        'spreads': prepared['spreads'],
        'fillings': prepared['fillings'],
        'top': top,
        'layers': [base] + prepared['spreads'] + prepared['fillings'] + [top]
    }

if __name__ == "__main__":
    # View 1: The simple interface
    make_sandwich()
