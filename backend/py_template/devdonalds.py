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
	# Check if cookbook empty
	if (cookbook == None or cookbook == {}):
		return {}, 400
	
	name = request.args.get('name')

	# Check if recipe, if not exist return status 400
	found = False
	for d in cookbook:
		if d['name'] == name and d['type'] == 'recipe':
			found = True
	if not found:
		return {}, 400
	
	# setting up summary 
	res = {}
	res['name'] = name
	res['ingredients'] = []
	res['cookTime'] = 0

	found_all = True
	res['ingredients'], found_all = getbaseIngredients(name, found_all)

	if not found_all:
		return {}, 400

	for ingredient in res['ingredients']:
		res['cookTime'] += ingredient.get('quantity') * getCookTime(ingredient.get('name'))

	return res, 200

# Check if item is an ingredient or recipe, returns respective strings:
# if does not exist, returns None
def getType(name: str) -> Union[str | None]:
	for d in cookbook:
		if d['name'] == name:
			return d['type']
	return None

def getCookTime(name: int):
	for d in cookbook:
		if d['name'] == name:
			return d['cookTime']
	return None

def getbaseIngredients(item_name: str, found_all: bool, multiplier=1):
	item = None
	for d in cookbook:
		if d['name'] == item_name:
			item = d
	
	if item is None:
		found_all = False
		return [], found_all
	
	if item.get('type') == 'ingredient':
		return [{'name': item_name, 'quantity': multiplier}], found_all
	
	result = {}
	base_ing = []
	for req_item in item.get('requiredItems'):
		sub_ing, found_all = getbaseIngredients(
			req_item.get('name'),
			found_all,
			multiplier*req_item.get('quantity', 1),
			)
		for ingredient in sub_ing:
			name = ingredient['name']
			quant = ingredient['quantity']
			result[name] = result.get('name', 0) + quant
		
	for name, quant in result.items():
		base_ing.append({'name': name, 'quantity': quant})

	return base_ing, found_all




# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
