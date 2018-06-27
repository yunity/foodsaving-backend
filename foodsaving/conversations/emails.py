from email.utils import formataddr
from babel.dates import format_date, format_time

from django.utils import translation, timezone
from django.utils.translation import ugettext as _

from config import settings
from foodsaving.groups.models import Group
from foodsaving.pickups.models import PickupDate
from foodsaving.utils.email_utils import prepare_email
from foodsaving.utils.frontend_urls import (
    group_wall_url,
    group_conversation_mute_url,
    pickup_detail_url,
    pickup_conversation_mute_url,
)
from foodsaving.webhooks.api import make_local_part


def prepare_conversation_message_notification(user, message):
    if isinstance(message.conversation.target, Group):
        return prepare_group_conversation_message_notification(user, message)
    if isinstance(message.conversation.target, PickupDate):
        return prepare_pickup_conversation_message_notification(user, message)
    raise Exception('Cannot send message notification because conversation doesn\'t have a known target')


def prepare_group_conversation_message_notification(user, message):
    group = message.conversation.target

    reply_to_name = group.name
    conversation_name = group.name

    local_part = make_local_part(message.conversation, user)
    reply_to = formataddr((reply_to_name, '{}@{}'.format(local_part, settings.SPARKPOST_RELAY_DOMAIN)))
    from_email = formataddr((message.author.display_name, settings.DEFAULT_FROM_EMAIL))

    return prepare_email(
        'conversation_message_notification',
        from_email=from_email,
        user=user,
        reply_to=[reply_to],
        context={
            'conversation_name': conversation_name,
            'author': message.author,
            'message_content': message.content_rendered(),
            'conversation_url': group_wall_url(group),
            'mute_url': group_conversation_mute_url(group, message.conversation)
        }
    )


def prepare_pickup_conversation_message_notification(user, message):
    pickup = message.conversation.target
    group_tz = pickup.store.group.timezone

    language = user.language

    if not translation.check_for_language(language):
        language = 'en'

    with translation.override(language):
        with timezone.override(group_tz):
            weekday = format_date(
                pickup.date.astimezone(timezone.get_current_timezone()),
                'EEEE',
                locale=translation.to_locale(language),
            )
            time = format_time(
                pickup.date,
                format='short',
                locale=translation.to_locale(language),
                tzinfo=timezone.get_current_timezone(),
            )
            date = format_date(
                pickup.date.astimezone(timezone.get_current_timezone()),
                format='long',
                locale=translation.to_locale(language),
            )

            long_date = '{} {}, {}'.format(weekday, time, date)
            short_date = '{} {}'.format(weekday, time)

            reply_to_name = _('Pickup %(date)s') % {
                'date': short_date,
            }
            conversation_name = _('Pickup %(date)s') % {
                'date': long_date,
            }

            local_part = make_local_part(message.conversation, user)
            reply_to = formataddr((reply_to_name, '{}@{}'.format(local_part, settings.SPARKPOST_RELAY_DOMAIN)))
            from_email = formataddr((message.author.display_name, settings.DEFAULT_FROM_EMAIL))

            return prepare_email(
                'conversation_message_notification',
                from_email=from_email,
                user=user,
                reply_to=[reply_to],
                context={
                    'conversation_name': conversation_name,
                    'author': message.author,
                    'message_content': message.content_rendered(),
                    'conversation_url': pickup_detail_url(pickup),
                    'mute_url': pickup_conversation_mute_url(pickup, message.conversation)
                }
            )