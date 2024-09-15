import constants
entity_unit_map = constants.entity_unit_map
allowed_units = constants.allowed_units

# new part
import re

unit_to_entity = dict()
for u in allowed_units:
    unit_to_entity[u] = []
    for k,v in entity_unit_map.items():
        if u in v:
            unit_to_entity[u].append(k)
                
# alias_dict = {u:u for u in allowed_units}
alias_dict = {
    'cm': 'centimetre',
    'ft': 'foot',
    'feet': 'foot',
    'in': 'inch',
    'm': 'metre',
    'mm': 'millimetre',
    'yd': 'yard',
    
    'kg': 'kilogram',
    'g': 'gram',
    'gm': 'gram',
    'mg': 'milligram',
    'oz': 'ounce',
    'lb': 'pound',
    
    'kv': 'kilovolt',
    'mv': 'millivolt',
    'v': 'volt',
    'kw': 'kilowatt',
    'w': 'watt',
    
    'cl': 'centilitre',
    'cu ft': 'cubic foot',
    'cu in': 'cubic inch',
    'cu foot': 'cubic foot',
    'cu inch': 'cubic inch',
    'dl': 'decilitre',
    'ml': 'millilitre',
    'l': 'litre',
    'fl oz': 'fluid ounce',
    'pt': 'pint',
    'qt': 'quart',
    'gal': 'gallon',
    'imp gal': 'imperial gallon'
}

def normalize_unit(unit):
    unit = unit.strip()
    unit.replace("ter", "tre")    # uk/us
    unit.replace("feet", "foot")  #  plural
    unit.replace(".", "")
    if len(unit) > 1 and unit.endswith('s'):           # plural
        unit = unit[:-1]
    if unit in alias_dict:
        unit = alias_dict[unit]     # aliases / shorforms
    return unit
 
# extracts list of [val, unit] from a string or list of strings
def extract_value_unit(text):
    results= []
    if isinstance(text,list):
        for t in text:
            results.extend(extract_value_unit(t))
        return results
            
    value = '[0-9]*\.?[0-9]+'
    bi_word = '(cubic|cu|imperial|imp|fluid|fl)[ ]*'
    name = f'({bi_word})?[a-z]+'
    text = text.lower()
    
    matches=re.findall(f'({value})[ ,(]*({name})', text)
    if len(matches) == 0:
        return results
    
    for pair in matches:
        val = pair[0]
        unit = normalize_unit(pair[1])
        if unit in allowed_units:
            results.append((val, unit))
            
    return results



# take list of [val,unit] and entity. Removes entries with invalid units
def filter_by_entity(val_unit_list, entity_name):
    new_list = []
    if entity_name not in entity_unit_map.keys():
        print("invalid entity name")
        return new_list
    
    for entry in val_unit_list:
        if entry[1] not in entity_unit_map[entity_name]:
            continue
        new_list.append(entry)
    return new_list

def filter_paddle(image_results, entity_name=None):
    processed_results= []
    if len(image_results)==0:
        return image_results
    
    for result in image_results:
        vu_list = extract_value_unit(result[0]) # cleaning and segregating val/unit
        if entity_name is not None:
            vu_list = filter_by_entity(vu_list, entity_name)  # filter by entity type
        for vu in vu_list:
            processed_results.append([vu, result[1]])
            
    return processed_results
    