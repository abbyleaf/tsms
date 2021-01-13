import json

with open('debug.log', 'r', encoding='UTF8') as logfile:
    for line in logfile:
        line = line.strip()
        if 'Error' in line.lower() or 'authorised' in line or 'permitted' in line:
            print('=== BLOCKED ===')
        if line.startswith('2'):
            continue
        line = '{' + line
        try:
            data = json.loads(line)
        except:
            continue
        if 'message' in data:
            data = data['message']
            try:
                print(data['from']['first_name'], ':', data['text'])
            except:
                print('=== CONTACT ===')
        elif 'callback_query' in data:
            data = data['callback_query']
            print(data['from']['first_name'], ':', data['data'])
        else:
            print(data)
