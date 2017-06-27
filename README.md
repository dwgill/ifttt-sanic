# ifttt-sanic

This is an attempt at a server to interface with [If This Then That][ifttt_url]'s
[Maker Webhooks channel][maker_url], leveraging the [Sanic][sanic_url] asynchronous
Python web framework. 

It was supposed to leverage IFTTT to fetch updates to [thewirecutter.com][], determine
if the update had anything to do with Android tablets, and if so, alert me via
[Pushbullet][pb_url], leveraging the [corresponding IFTTT channel][pb_channel_url].
However, it turns out that the information received from the Wirecutter RSS needs to
be properly escaped before it can be successfully sent via a JSON POST back to IFTTT,
so this project is not fully functional at this time.

[ifttt_url]: https://en.wikipedia.org/wiki/IFTTT
[maker_url]: https://ifttt.com/maker_webhooks
[sanic_url]: https://github.com/channelcat/sanic
[pb_url]: https://www.pushbullet.com/
[pb_channel_url]: https://ifttt.com/pushbullet
