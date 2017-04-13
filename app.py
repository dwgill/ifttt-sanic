from functools import partial
from sanic import Sanic, response
from sanic.response import json
from sanic.exceptions import InvalidUsage
import os
import re
import requests


IFTTT_KEY = os.getenv("IFTTT_API_KEY")
if IFTTT_KEY == '' or IFTTT_KEY is None:
    raise Exception('IFTTT_API_KEY env var required')


app = Sanic()


def ok_resp(value=None):
    return json({
        'status': 'ok',
        'result': value,
    })

def err_resp(err='Something went wrong', http_status=400):
    return json({
        'status': 'err',
        'err': err,
    }, status=http_status)


@app.route('/')
async def test(request):
    return ok_resp('Hello world!')


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

    try:
        json_body = request.json
    except InvalidUsage:
        await pb_note(title='Issue with ifttt-maker',
            desc=('wirecutter_update received a post without a proper JSON body.\n\n'
                  'Full body:\n\n'
                  '{body}').format(body=request.body))

        return err_resp('Invalid JSON body')

    if 'EntryUrl' not in request.json:
        err_text = ('No EntryUrl in request to wirecutter_update.\n\n'
                    'Full json body:\n\n'
                    '{json_body}').format(json_body=request.json)

        await pb_note(title='Issue with ifttt-maker',
                      desc=err_text)
        return err_resp('No EntryUrl')

    for entry_section in ['EntryTitle', 'EntryUrl',
                          'EntryContent', 'EntryId']:
        if re.search('android.tablet', request.json.get(entry_section, ''),
                     re.IGNORECASE):
            await pb_link(
                title='Wirecutter Android Tablet Update',
                link_url=request.json['EntryUrl'])
            break

    return ok_resp()


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
        'value1': str(title).strip(),
        'value2': str(link_url).strip()
    })


# https://ifttt.com/applets/52387571d-maker-pushbullet-notes
async def pb_note(title, desc):
    await trigger_ifttt_maker_event('pb_note', {
        'value1': str(title).strip(),
        'value2': str(desc).strip()
    })


# https://ifttt.com/applets/52387669d-maker-pushbullet-files
async def pb_file(title, file_url):
    await trigger_ifttt_maker_event('pb_file', {
        'value1': str(title).strip(),
        'value2': file_url
    })


# https://ifttt.com/applets/52387695d-maker-pushbullet-addresses
async def pb_address(title, address):
    await trigger_ifttt_maker_event('pb_address', {
        'value1': str(title).strip(),
        'value2': address
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
