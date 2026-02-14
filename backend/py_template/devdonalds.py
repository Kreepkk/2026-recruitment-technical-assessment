from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = None

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	recipeName = recipeName.strip()
	recipeName = recipeName.replace("-", " ")
	recipeName = recipeName.replace("_", " ")
	recipeName = re.sub(r'[^a-zA-Z\s]', '', recipeName)
	recipeName = recipeName.title()
	if len(recipeName) > 0:
		return recipeName
	return None


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	global cookbook
	data = request.get_json()
	# Cookbook is list
	if cookbook == None:
		cookbook = []
	else:
		if (any(d.name == data.get('name') for d in cookbook)): # Check names unique
			return {}, 400
	if data.get('type') == 'ingredient':			# ingredients check and entry
		if (data.get('cookTime') < 0):
			return {}, 400
		else:
			entry = Ingredient(
				name=data.get('name'),
				cook_time=data.get('cookTime')
			)
	elif data.get('type') == 'recipe':			# recipe check and entry
		# Check if all item names are unique
		items = [RequiredItem(name=item.get('name'), quantity=item.get('quantity')) 
		   			for item in data.get('requiredItems', [])]
		
		item_names = [item.name for item in items]
		if len(item_names) != len(set(item_names)):
			return {}, 400
		entry = Recipe(
			name=data.get('name'),
			required_items=items
		)
	else:
		return {}, 400			# Case where it's type is not ingredient nor recipe
 
	
	cookbook.append(entry)

	return {}, 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	# Check if cookbook empty
	if (cookbook == None or cookbook == []):
		return {}, 400
	
	name = request.args.get('name')

	# Check if recipe, if not exist return status 400
	found = False
	for d in cookbook:
		if d.name == name and isinstance(d, Recipe):
			found = True
	if not found:
		return {}, 400
	
	# setting up summary 
	res = {}
	res['name'] = name
	res['ingredients'] = []
	res['cookTime'] = 0
	
	# Get all base ingredients
	found_all = True
	res['ingredients'], found_all = getbaseIngredients(name, found_all)

	# If there was a required item not found in cookbook
	if not found_all:
		return {}, 400

	# get total cookTime
	for ingredient in res['ingredients']:
		res['cookTime'] += ingredient.get('quantity') * getCookTime(ingredient.get('name'))

	return res, 200

# Get the cookTime of an ingredient, assumes that name given is an ingredient
# returns none if not exist
def getCookTime(name: int):
	for d in cookbook:
		if d.name == name:
			return d.cook_time
	return None

# Recursive call to gain all base ingredients of an item
def getbaseIngredients(item_name: str, found_all: bool, multiplier=1):
	# Get item
	item = None
	for d in cookbook:
		if d.name == item_name:
			item = d

	# item does not exist in cookbook, set flag found_all to false
	if item is None:
		found_all = False
		return [], found_all
	
	# item is ingredient, return it's name and quantity as a list
	if isinstance(item, Ingredient):
		return [{'name': item_name, 'quantity': multiplier}], found_all
	
	# Item is recipe
	# Initialise result [name: quantity, ...]
	# Initialise base_ing -> list of base ingredients
	result = {}
	for req_item in item.required_items:
		# Sub-items found during recursive call -> has list of base ingredient for that req_item
		sub_ing, found_all = getbaseIngredients(
			req_item.name,
			found_all,
			multiplier*req_item.quantity,
			)
		# Use sub_ing to get new added items in result
		for ingredient in sub_ing:
			name = ingredient['name']
			quant = ingredient['quantity']
			result[name] = result.get(name, 0) + quant

	return [{'name': name, 'quantity': quantity} for name, quantity in result.items()], found_all




# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
