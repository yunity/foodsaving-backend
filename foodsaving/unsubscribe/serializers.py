from django.core.signing import BadSignature
from rest_framework import serializers

from foodsaving.unsubscribe.utils import parse_token, unsubscribe_from_conversation, unsubscribe_from_thread, \
    unsubscribe_from_all_conversations_in_group


class UnsubscribeSerializer(serializers.Serializer):
    choice = serializers.ChoiceField(choices=['conversation', 'thread', 'group'], default='conversation')
    token = serializers.CharField()

    @staticmethod
    def validate_token(token):
        try:
            return parse_token(token)  # will throw an exception if invalid
        except BadSignature:
            raise serializers.ValidationError()

    def create(self, validated_data):
        token_data = validated_data.get('token')

        user = token_data['user']
        choice = validated_data.get('choice')

        if choice == 'conversation':
            if 'conversation' not in token_data:
                raise serializers.ValidationError()
            unsubscribe_from_conversation(user, token_data['conversation'])

        elif choice == 'thread':
            if 'thread' not in token_data:
                raise serializers.ValidationError()
            unsubscribe_from_thread(user, token_data['thread'])

        elif choice == 'group':
            if 'group' not in token_data:
                raise serializers.ValidationError()
            unsubscribe_from_all_conversations_in_group(user, token_data['group'])

        return {}
