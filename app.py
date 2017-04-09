from functools import partial
from sanic import Sanic, response
from sanic.response import json
import os
import re
import requests


IFTTT_KEY = os.getenv("IFTTT_API_KEY")
if IFTTT_KEY == '' or IFTTT_KEY is None:
    raise Exception('IFTTT_API_KEY env var required')


app = Sanic()


@app.route('/')
async def test(request):
    return json({
        'status': 'ok',
        'result': 'Hello World!'
    })


@app.post('/wirecutter')
async def wirecutter_update(request):
    '''
    The json body of the request should look like this:
    {
        "EntryId": "{{EntryId}}",
        "EntryTitle": "{{EntryTitle}}",
        "EntryUrl": "{{EntryUrl}}",
        "EntryAuthor": "{{EntryAuthor}}",
        "EntryContent": "{{EntryContent}}",
        "EntryImageUrl": "{{EntryImageUrl}}",
        "EntryPublished": "{{EntryPublished}}",
        "FeedTitle": "{{FeedTitle}}",
        "FeedUrl": "{{FeedUrl}}"
    }
    '''

    for entry_section_name in ['EntryTitle', 'EntryUrl',
                               'EntryContent', 'EntryId']:
        entry_section = request.json.get(entry_section_name, '')
        if re.search('android.tablet', entry_section, re.IGNORECASE):
            await pb_link(
                title='Wirecutter Android Tablet Update',
                link_url=request.json['EntryUrl'])
            break

    return json({
        'status': 'ok',
        'result': None
    })


# https://ifttt.com/maker_webhooks
async def trigger_ifttt_maker_event(event, values):
    event_url = f'https://maker.ifttt.com/trigger/{event}/with/key/{IFTTT_KEY}'

    if values:
        post_event = partial(requests.post, url=event_url, json=values)
    else:
        post_event = partial(requests.post, event_url)

    await app.loop.run_in_executor(None, post_event)


# https://ifttt.com/applets/52387457d-maker-pushbullet-links
async def pb_link(title, link_url):
    await trigger_ifttt_maker_event('pb_link', {
        'value1': title,
        'value2': link_url
    })


# https://ifttt.com/applets/52387571d-maker-pushbullet-notes
async def pb_note(title, desc):
    await trigger_ifttt_maker_event('pb_note', {
        'value1': title,
        'value2': desc
    })


# https://ifttt.com/applets/52387669d-maker-pushbullet-files
async def pb_file(title, file_url):
    await trigger_ifttt_maker_event('pb_file', {
        'value1': title,
        'value2': file_url
    })


# https://ifttt.com/applets/52387695d-maker-pushbullet-addresses
async def pb_address(title, address):
    await trigger_ifttt_maker_event('pb_address', {
        'value1': title,
        'value2': address
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
