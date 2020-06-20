from itertools import groupby

import requests
from django.core.management.base import BaseCommand
from operator import itemgetter
from pymdownx import twemoji_db

SOURCE_URL = 'https://raw.githubusercontent.com/markdown-it/markdown-it-emoji/fffd76a632c1ff5c7014156320a1db894a3a02e0/lib/data/full.json'  # noqa E501
FILENAME = 'karrot/conversations/emoji_db.py'
HEADER = """
# Source: {url} # noqa E501
# Auto-generated by manage.py make_emoji_list

""".format(url=SOURCE_URL)

CUSTOM_PREFERENCES = [
    'information_desk_person',
    'no_good_man',
]


def with_colons(n):
    return ':' + n + ':'


class Command(BaseCommand):
    def handle(self, *args, **options):
        def get_shortest(entries):
            shortest_len = min(len(t[0]) for t in entries)
            return next(t for t in entries if len(t[0]) == shortest_len)

        emoji = {}
        aliases = {}

        def choose(chosen, entries):
            chosen_name, chosen_unicode = chosen
            emoji[chosen_name] = chosen_unicode
            our_aliases = {}
            for name, unicode in entries:
                if name == chosen_name:
                    continue
                our_aliases[name] = chosen_name
            if len(our_aliases) > 0:
                print('Choosing {} over {}'.format(chosen_name, ', '.join(our_aliases.keys())))
            aliases.update(our_aliases)

        source_list = requests.get(SOURCE_URL).json()
        keyfunc = itemgetter(1)
        for _, g in groupby(sorted(source_list.items(), key=keyfunc), key=keyfunc):
            group = list(g)
            if len(group) < 2:
                choose(group[0], group)
                continue

            preferred = [t for t in group if t[0] in CUSTOM_PREFERENCES]
            if len(preferred) > 0:
                choose(preferred[0], group)
                continue

            in_twemoji = [t for t in group if with_colons(t[0]) in twemoji_db.emoji]
            if len(in_twemoji) == 1:
                choose(in_twemoji[0], group)
                continue

            if len(in_twemoji) > 1:
                choose(get_shortest(in_twemoji), group)
                continue

            choose(get_shortest(group), group)

        with open(FILENAME, 'w') as f:
            f.write(HEADER)
            f.write('emoji = {}'.format(repr(emoji)))
            f.write('\n')
            f.write('aliases = {}'.format(repr(aliases)))
