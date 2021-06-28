import requests, json, os

trello_key = os.environ.get('TRELLO_KEY')
trello_token = os.environ.get('TRELLO_TOKEN')
trello_board = os.environ.get('TRELLO_BOARD')


def get_lists():
    """
    Fetches all the lists for the board from trello.

    Returns:
        dictionary: key value pairs of board id and board name, as well as board name and id (for reverse lookup)
    """    
    lists = {}
    url = 'https://www.trello.com/1/boards/{0}/lists?key={1}&token={2}'.format(trello_board, trello_key, trello_token)
    resp = requests.get(url)
    json_lists = json.loads(resp.text) 
    for json_list in json_lists:
        # dual purpose dictionary. keyed on name and id for reverse lookups
        lists[json_list['id']] = json_list['name']
        lists[json_list['name']] = json_list['id']
    return lists


def get_items():
    """
    Fetches all cards from trello.

    Returns:
        list: The list of cards.
    """
    lists = get_lists()

    url = 'https://www.trello.com/1/boards/{0}/cards?key={1}&token={2}'.format(trello_board, trello_key, trello_token)
    resp = requests.get(url)
    items = json.loads(resp.text)

    # enrich the output by appending the list name to each card, based on its list id
    for item in items:
        item['list_name'] = lists[item['idList']]

    sorted_items = sorted(items, key = lambda x: (x['idList'], x['name']))
    
    return sorted_items


def add_item(title):
    """
    Adds a new card with the specified title to the 'To Do' list in Trello.

    Args:
        title: The title of the card.

    Returns:
        item: The saved card.
    """
    lists = get_lists()
    url = 'https://www.trello.com/1/cards?key={0}&token={1}'.format(trello_key, trello_token)
    # pass the the listId for 'To Do' list
    data = {'name' : title, 'idList': lists['To Do']}   
    resp = requests.post(url, data)
    return json.loads(resp.text)


def save_item(id, list):
    """
    Updates an existing item in the session. If no existing item matches the ID of the specified item, nothing is saved.

    Args:
        id: The item to save.
        list: the list to save the item to.
    """
    lists = get_lists()
    url = 'https://www.trello.com/1/cards/{0}?key={1}&token={2}'.format(id, trello_key, trello_token)
    # pass the the listId for the list argument
    data = {'idList': lists[list]}
    resp = requests.put(url, data)
    return json.loads(resp.text)


def complete_item(id):
    """
    Sets an existing item to Complete/Done

    Args:
        id: The item to set to complete

    Returns:
        item: The updated item
    """
    return save_item(id, 'Done')


def start_item(id):
    """
    Sets an existing item to To Do

    Args:
        id: The item to set to To Do
        
    Returns:
        item: The updated item
    """
    return save_item(id, 'To Do')


def progress_item(id):
    """
    Sets an existing item to In Progress/Doing

    Args:
        id: The item to set to in progress
        
    Returns:
        item: The updated item
    """
    return save_item(id, 'Doing')    
