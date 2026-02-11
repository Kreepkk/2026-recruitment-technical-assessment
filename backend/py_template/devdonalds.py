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
	# TODO: Return name if satisfies all without needing to modify after .strip()
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
		if (any(d['name'] == data.get('name') for d in cookbook)):
			return {}, 400

	# Check type correct
	if data.get('type') != 'ingredient' and data.get('type') != 'recipe':
		return {}, 400
	# Check cook time if ingredient
	if data.get('type') == 'ingredient':
		if (data.get('cookTime') < 0):
			return {}, 400
		
	# Check requiredItem if recipe
	if data.get('type') == 'recipe':
		item_names = []
		for item in data.get('requiredItems'):
			item_names.append(item.get('name'))
		if len(item_names) != len(set(item_names)):
			return {}, 400
 
	
	cookbook.append(data)

	return {}, 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	# TODO: implement me
	# Check if cookbook empty
	if (cookbook == None or cookbook == {}):
		return {}, 400
	name = request.args.get('name')
	found = False
	for d in cookbook:
		if d['name'] == name and d['type'] == 'recipe':
			recipe = d
			found = True
	
	if not found:
		return {}, 400

	return 'not implemented', 500


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
