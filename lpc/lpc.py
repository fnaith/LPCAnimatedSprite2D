from os import walk, makedirs
from os.path import join, exists
from json import loads, dumps
import shutil
from uuid import uuid1
from itertools import groupby
from operator import itemgetter

import base36
import jsbeautifier



LPC_DIR = '../../Universal-LPC-Spritesheet-Character-Generator/'
SHEET_DEFINITION_DIR = LPC_DIR + 'sheet_definitions'
SPRITESHEET_DIR = LPC_DIR + 'spritesheets'
COPY_DIR = './'



BODY_TYPES = ["male", "muscular", "female", "pregnant", "teen", "child"]

LPC_SPRITE_SHEET_TEMPLATE = '''[gd_resource type="Resource" script_class="LPCSpriteSheet" load_steps=3 format=3 uid="uid://%s"]

[ext_resource type="Script" path="res://addons/LPCAnimatedSprite/LPCSpriteSheet.gd" id="1"]
[ext_resource type="Texture2D" uid="uid://%s" path="res://lpc/%s" id="2"]

[resource]
script = ExtResource("1")
SpriteSheet = ExtResource("2")
Name = "%s"
SpriteType = 0'''

LPC_SPRITE_SHEET_PRELOAD_TEMPLATE = 'static var %s: LPCSpriteSheet = "res://lpc/%s"'


def load_sheet_definitions():
  sheet_definitions = []

  for dir_path, dir_names, file_names in walk(SHEET_DEFINITION_DIR):
    for file_name in file_names:
      if file_name.endswith('.json'):
        with open(join(SHEET_DEFINITION_DIR, file_name), 'r', encoding='utf-8') as f:
          sheet_definition = loads(f.read())
          sheet_definitions.append(sheet_definition)

  return sheet_definitions

def stat_sheet_definitions(sheet_definitions):
  type_name_count = {}
  for sheet_definition in sheet_definitions:
    type_name = sheet_definition['type_name']
    type_name_count[type_name] = type_name_count.get(type_name, 0) + 1
  type_name_count = sorted(type_name_count.items(), key=lambda x:x[1])
  for entry in type_name_count:
    print(entry[0], entry[1])

def validate_spritesheet(sheet_definitions, show_error):
  valid_sheet_definitions = []
  for sheet_definition in sheet_definitions:
    valid = True
    layer_count = 0
    key_count = {}
    for field in sheet_definition.keys():
      if field.startswith('layer_'):
        layer = sheet_definition[field]
        layer_count += 1
        for key in layer.keys():
          if 'zPos' != key and 'is_mask' != key and 'custom_animation' != key:
            key_count[key] = key_count.get(key, 0) + 1

    if 0 == layer_count:
      raise Exception('no layers : %s, %s' % (sheet_definition['name'], sheet_definition['type_name']))

    key_count_items = list(key_count.items())
    for item in key_count_items:
      if item[0] not in BODY_TYPES:
        raise Exception('unknown body type : %s, %s, %s' % (sheet_definition['name'], sheet_definition['type_name'], item[0]))
    for item in key_count_items:
      if key_count_items[0][1] != item[1]:
        raise Exception('missing body type : %s, %s, %s' % (sheet_definition['name'], sheet_definition['type_name'], str(key_count_items)))

    variants = sheet_definition['variants']
    layer_dirs = []
    for item in key_count_items:
      body_type = item[0]
      for variant in variants:
        has_variant = None
        for layer_index in range(layer_count):
          layer_dir = sheet_definition['layer_' + str(layer_index + 1)][body_type]
          if layer_dir not in layer_dirs:
            layer_dirs.append(layer_dir)
          spritesheet_path = SPRITESHEET_DIR + '/' + layer_dir + variant + '.png'
          if None == has_variant:
            has_variant = exists(spritesheet_path)
          elif has_variant != exists(spritesheet_path):
            valid = False
            if show_error:
              print('missing spritesheet : %s, %s, %s, %s' % (sheet_definition['name'], sheet_definition['type_name'], body_type, variant))
    for layer_dir in layer_dirs:
      is_missing = True
      for variant in variants:
        spritesheet_path = SPRITESHEET_DIR + '/' + layer_dir + variant + '.png'
        if exists(spritesheet_path):
          is_missing = False
      if is_missing:
        valid = False
        if show_error:
          print('missing layer dir : %s, %s, %s' % (sheet_definition['name'], sheet_definition['type_name'], layer_dir))

    if valid:
      valid_sheet_definitions.append(sheet_definition)

  return valid_sheet_definitions

def list_spritesheet(valid_sheet_definitions):
  spritesheet_list = []

  for sheet_definition in valid_sheet_definitions:
    name = sheet_definition['name']
    type_name = sheet_definition['type_name']
    layer_count = 0
    for field in sheet_definition.keys():
      if field.startswith('layer_'):
        layer_count += 1

    variants = sheet_definition['variants']
    for body_type in BODY_TYPES:
      first_layer = sheet_definition['layer_1']
      if body_type not in first_layer:
        continue
      for variant in variants:
        if not exists(SPRITESHEET_DIR + '/' + first_layer[body_type] + variant + '.png'):
          continue
        layers = []
        for layer_index in range(layer_count):
          layer = sheet_definition['layer_' + str(layer_index + 1)]
          layers.append((layer[body_type], layer['zPos']))
        spritesheet_list.append([body_type, type_name, name, variant, layers])

  return spritesheet_list

def stat_spritesheet_list(spritesheet_list):
  spritesheet_list = sorted(spritesheet_list, key=itemgetter(0))
  for body_type, spritesheet_by_body_type in groupby(spritesheet_list, key=itemgetter(0)):
    spritesheet_by_body_type = sorted(list(spritesheet_by_body_type), key=itemgetter(1))
    type_count = 0
    name_count = 0
    variant_count = 0
    print('body_type %s : %d' % (body_type, len(spritesheet_by_body_type)))
    for type_name, spritesheet_by_type_name in groupby(spritesheet_by_body_type, key=itemgetter(1)):
      spritesheet_by_type_name = sorted(list(spritesheet_by_type_name), key=itemgetter(2))
      type_count += 1
      #print('\ttype_name %s : %d' % (type_name, len(spritesheet_by_type_name)))
      for name, spritesheet_by_name in groupby(spritesheet_by_type_name, key=itemgetter(2)):
        spritesheet_by_name = sorted(list(spritesheet_by_name), key=itemgetter(3))
        name_count += 1
        variant_count += len(spritesheet_by_name)
        #print('\tname %s : %d' % (name, len(spritesheet_by_name)))
    print('\ttype_count %s : %d' % (body_type, type_count))
    print('\tname_count %s : %d' % (body_type, name_count))
    print('\tvariant_count %s : %d' % (body_type, variant_count))

def copy_spritesheet(spritesheet_list):
  for spritesheet in spritesheet_list:
    variant = spritesheet[3]
    layer_dirs = list(map(lambda x: x[0], spritesheet[4]))
    for layer_dir in layer_dirs:
      makedirs(COPY_DIR + layer_dir, exist_ok=True)
      file_name = layer_dir + variant
      file_path = file_name + '.png'
      spritesheet_path = SPRITESHEET_DIR + '/' + file_path
      copy_path = COPY_DIR + file_path
      if not exists(copy_path):
        shutil.copyfile(spritesheet_path, copy_path)

def generate_spritesheet_tres(spritesheet_list):
  for spritesheet in spritesheet_list:
    variant = spritesheet[3]
    layer_dirs = list(map(lambda x: x[0], spritesheet[4]))
    for layer_dir in layer_dirs:
      makedirs(COPY_DIR + layer_dir, exist_ok=True)
      file_name = layer_dir + variant
      file_path = file_name + '.png'
      copy_path = COPY_DIR + file_path
      import_path = copy_path + '.import'
      tres_path = COPY_DIR + file_name + '.tres'
      if exists(import_path) and not exists(tres_path):
        texture_uid = None
        text = open(import_path, 'r').read()
        lines = text.strip().split('\n')
        for line in lines:
          if line.startswith('uid='):
            texture_uid = line[11:-1]
            break
        new_uid = uuid1().int & 0x7FFFFFFFFFFFFFFF
        lpc_sprite_sheet = LPC_SPRITE_SHEET_TEMPLATE % (new_uid, texture_uid, file_path, file_name)
        with open(tres_path, 'w', encoding='utf-8') as f:
          f.write(lpc_sprite_sheet)

def generate_spritesheet_group(spritesheet_list):
  spritesheet_list = sorted(spritesheet_list, key=itemgetter(0))
  for body_type, spritesheet_by_body_type in groupby(spritesheet_list, key=itemgetter(0)):
    spritesheet_by_body_type = sorted(list(spritesheet_by_body_type), key=itemgetter(1))
    type_name_to_spritesheets = {}
    for type_name, spritesheet_by_type_name in groupby(spritesheet_by_body_type, key=itemgetter(1)):
      spritesheet_by_type_name = sorted(list(spritesheet_by_type_name), key=itemgetter(3))
      spritesheets = []
      type_name_to_spritesheets[type_name] = spritesheets
      for spritesheet in spritesheet_by_type_name:
        spritesheets.append(spritesheet[3:])

    json_path = COPY_DIR + '/spritesheets-' + body_type + '.json'
    with open(json_path, 'w', encoding='utf-8') as f:
      options = jsbeautifier.default_options()
      options.indent_size = 1
      options.indent_char = '\t'
      output = jsbeautifier.beautify(dumps(type_name_to_spritesheets, sort_keys=True), options)
      f.write(output.replace(', ', ','))





sheet_definitions = load_sheet_definitions()
#stat_sheet_definitions(sheet_definitions)
valid_sheet_definitions = validate_spritesheet(sheet_definitions, False)
print(len(sheet_definitions))
print(len(valid_sheet_definitions))
spritesheet_list = list_spritesheet(valid_sheet_definitions)
print(len(spritesheet_list))
#stat_spritesheet_list(spritesheet_list)
#copy_spritesheet(spritesheet_list)
#generate_spritesheet_tres(spritesheet_list)
generate_spritesheet_group(spritesheet_list)
