from json import load, dumps, dump

from flask import Flask, request

app = Flask(__name__)


def generate_id(offset):
    with open('users.json', 'r', encoding='utf-8') as f:
        users = load(f)
    return max(map(lambda x: x['id'], users)) + offset


@app.route('/test', methods=['GET', 'POST'])
def test():
    return 'Hello, world!'


@app.route('/list', methods=['GET'])
def list_users():
    with open('users.json', encoding='utf-8') as f:
        return dumps(load(f), ensure_ascii=False, indent=2)


@app.route('/add', methods=['POST'])
def add_user():
    # Сначала прочитаем всю базу для удобства работы
    with open('users.json', 'r', encoding='utf-8') as f:
        data = load(f)

    # Создадим шаблон для овтета
    response = {
        "Status": "ok",
        # (from, to)
        "replaced_ids": [],
        "message": ""
    }

    # Для генерации нового id
    id_offset = 1

    # Если JSON не получен
    json_list = request.json
    if json_list is None:
        response['Status'] = 'failed'
        response['message'] = "JSON was not provided"
        return response

    # Принимаем как одного юзера, так и список юзеров
    if not isinstance(json_list, list):
        json_list = [json_list]
    for json in json_list:
        # Если id не был указан вовсе, то сгенерируем его
        # или
        # Если такой id уже есть, то изменим его на другой
        if not json.get('id') or json['id'] in map(lambda x: x['id'], data):
            old = json.get('id')
            json['id'] = generate_id(id_offset)
            id_offset += 1
            response['replaced_ids'].append((old, json['id']))

    # Добавляем всех юзеров к уже существующим данным
    data += json_list
    with open('users.json', 'w', encoding='utf-8') as f:
        dump(data, f, ensure_ascii=False, indent=2)

    return response


@app.route('/get_by_id', methods=['POST', 'GET'])
def get_user_by_id():
    with open('users.json', 'r', encoding='utf-8') as f:
        data = load(f)

    json = request.json

    if not (isinstance(json, dict) and json.get('id')):
        return {'Status': 'failed', 'user': None, 'message': 'Wrong JSON format, use dict with id'}

    try:
        return {'Status': 'ok', 'user': next(filter(lambda x: x['id'] == json['id'], data)), 'message': ''}
    except StopIteration:
        return {'Status': 'failed', 'user': None, 'message': 'No such user found'}


@app.route('/update', methods=['POST'])
def update_user():
    with open('users.json', 'r', encoding='utf-8') as f:
        data = load(f)

    json = request.json

    if not (isinstance(json, dict) and json.get('id')):
        return {'Status': 'failed', 'user': None, 'message': 'Wrong JSON format, use dict with id'}

    index = 0
    for u in data:
        if u['id'] == json['id']:
            break
        index += 1

    # Если такого id не оказалось
    if index == len(data):
        return {'Status': 'failed'}

    for k, v in json.items():
        data[index][k] = v

    with open('users.json', 'w', encoding='utf-8') as f:
        dump(data, f, ensure_ascii=False, indent=2)

    return {'Status': 'ok'}


@app.route('/delete', methods=['POST'])
def delete_user():
    with open('users.json', 'r', encoding='utf-8') as f:
        data = load(f)

    json = request.json

    if not (isinstance(json, dict) and json.get('id')):
        return {'Status': 'failed', 'user': None, 'message': 'Wrong JSON format, use dict with id'}

    index = 0
    for u in data:
        if u['id'] == json['id']:
            break
        index += 1

    # Если такого id не оказалось
    if index == len(data):
        return {'Status': 'failed'}

    data.pop(index)

    with open('users.json', 'w', encoding='utf-8') as f:
        dump(data, f, ensure_ascii=False, indent=2)

    return {'Status': 'ok'}


app.run('localhost', 9512)
