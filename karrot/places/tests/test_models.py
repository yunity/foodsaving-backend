from django.db import DataError
from django.db import IntegrityError
from django.test import TestCase

from karrot.groups.factories import GroupFactory
from karrot.places.models import Place
from karrot.users.factories import UserFactory


class TestPlaceModel(TestCase):
    def setUp(self):
        self.group = GroupFactory()

    def test_create_fails_if_name_too_long(self):
        with self.assertRaises(DataError):
            Place.objects.create(name='a' * 81, group=self.group)

    def test_create_place_with_same_name_fails(self):
        Place.objects.create(name='abcdef', group=self.group)
        with self.assertRaises(IntegrityError):
            Place.objects.create(name='abcdef', group=self.group)

    def test_create_place_with_same_name_in_different_groups_works(self):
        Place.objects.create(name='abcdef', group=self.group)
        Place.objects.create(name='abcdef', group=GroupFactory())

    def test_get_active_status(self):
        s = Place.objects.create(name='my place', group=self.group)
        self.assertFalse(s.is_active())

        s.status = 'active'
        s.save()
        self.assertTrue(s.is_active())

        s.status = 'declined'
        s.save()
        self.assertFalse(s.is_active())

    def test_removes_subscription_when_leaving_group(self):
        place = Place.objects.create(name='abcdef', group=self.group)
        user = UserFactory()
        self.group.add_member(user)
        place.placesubscription_set.create(user=user)

        self.group.remove_member(user)

        self.assertFalse(place.placesubscription_set.filter(user=user).exists())
        conversation = place.conversation
        self.assertFalse(conversation.conversationparticipant_set.filter(user=user).exists())
