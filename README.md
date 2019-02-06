# Ease integration of Zendesk into your Django app

[![](https://img.shields.io/pypi/v/django-zengo.svg)](https://pypi.python.org/pypi/django-zengo/)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://pypi.python.org/pypi/django-zengo/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Codecov](https://codecov.io/gh/lukeburden/django-zengo/branch/master/graph/badge.svg)](https://codecov.io/gh/lukeburden/django-zengo)
[![CircleCI](https://circleci.com/gh/lukeburden/django-zengo.svg?style=svg)](https://circleci.com/gh/lukeburden/django-zengo)


## django-zengo

`django-zengo` is a Django app that provides conveniences for integrating with Zendesk.

It facilitates receiving webhook updates from Zendesk, detecting new tickets and changes to existing tickets.

### Installation ####

pip install django-zengo


### Usage ###

#### Configuring the webhook ####

Zengo comes with a view that processes messages sent by Zendesk and allows you to perform actions upon various Zendesk events.

##### Expose `zengo.views.WebhookView` #####

You need to configure your application to receive the webhook. To do so simply include it in your URL conf:

```python
from django.contrib import admin
from django.urls import path

from zengo.views import WebhookView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('zengo/webhook/', WebhookView.as_view())
]
```


##### Add required bits to `settings.py` #####

You need to tell Zengo how to authenticate with Zendesk:

-- `ZENDESK_EMAIL`; this is the email of the Zendesk account you will use to interact with the API.
-- `ZENDESK_TOKEN`; generate this for the user above in the Zendesk web interface.
-- `ZENDESK_SUBDOMAIN`; this must match the subdomain used in your Zendesk account.

As seen below, you need to specify
And you need to set a shared secret so that the webhook view can trust incoming messages from Zendesk:

-- `ZENGO_WEBHOOK_SECRET`; generate a nice long one-time-password for this.

So, your settings should appear something along the lines of:

```python
ZENDESK_EMAIL = "iamanemail@example.com"
ZENDESK_TOKEN = "<token-from-zendesk-webui>"
ZENDESK_SUBDOMAIN = "example"

ZENGO_WEBHOOK_SECRET = "<replace-me-with-a-great-password>"
```

###### Configure Zendesk to send events ######

Zendesk allows for many integrations, but for the purposes of Zengo we just need to be told when a ticket has been changed.

Log in as an administrator in Zendesk, and visit `Settings > Extensions > Targets > add target > HTTP target`.

Add an HTTP target with a URL of your service, and choose the `POST` method. Ensure you've added a `secret` query parameter to the URL where your webhook is accessible, such that the webhook view can authorize Zendesk's webhook sends.

Next, you must configure a trigger to use the target. Visit `Business Rules > Triggers > Add trigger`. Add a condition that suits your needs, such as, `Ticket is updated`, or `Ticket is created`, and select an action of `Notify target`, selecting the previously configured target. For JSON body, enter the following: 

```json
{
    "id": "{{ ticket.id }}"
}
```

You're done! Now whenever a ticket is created or updated in Zendesk, you should have an event being processed in your application.

Note: for development, I recommend using the excellent [ngrok](https://ngrok.com/) to proxy requests through to your localhost.

#### Performing actions upon receiving Zendesk events ####

When Zengo receives a webhook from Zendesk, it will fetch the latest state of the ticket from Zendesk's APIs, compare how this differs to the state in the local database models, and fire a signal indicating what has happened. In your application, you attach receivers to the signal that is most relevant to your need.

```python
from django.dispatch import receiver

from zengo.signals import ticket_created


@receiver(ticket_created)
def handle_new_ticket(sender, ticket, context, **kwargs):
    # perform your custom action here
    pass
```

#### Signals ####

You can connect to the following signals.

- `zengo.signals.ticket_created` - fires when a ticket is encountered for the first time.
- `zengo.signals.ticket_updated` - fires when a ticket previously encountered is changed, or has a new comment added.


## Contribute

`django-zengo` supports a variety of Python and Django versions. It's best if you test each one of these before committing. Our [Circle CI Integration](https://circleci.com) will test these when you push but knowing before you commit prevents from having to do a lot of extra commits to get the build to pass.

### Environment Setup

In order to easily test on all these Pythons and run the exact same thing that CI will execute you'll want to setup [pyenv](https://github.com/yyuu/pyenv) and install the Python versions outlined in [tox.ini](https://github.com/lukeburden/django-zengo/blob/master/tox.ini).

If you are on Mac OS X, it's recommended you use [brew](http://brew.sh/). After installing `brew` run:

```
$ brew install pyenv pyenv-virtualenv pyenv-virtualenvwrapper
```

Then:

```
pyenv install -s 2.7.15
pyenv install -s 3.4.7
pyenv install -s 3.5.4
pyenv install -s 3.6.3
pyenv virtualenv 2.7.15
pyenv virtualenv 3.4.7
pyenv virtualenv 3.5.4
pyenv virtualenv 3.6.3
pyenv global 2.7.15 3.4.7 3.5.4 3.6.3
pip install detox
```

To run the test suite:

Make sure you are NOT inside a `virtualenv` and then:

```
$ detox
```
