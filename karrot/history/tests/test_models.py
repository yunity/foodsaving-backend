from datetime import timedelta

from django.test import TestCase

from karrot.activities.factories import ActivityFactory
from karrot.activities.serializers import ActivitySerializer
from karrot.groups.factories import GroupFactory
from karrot.history.models import History, HistoryTypus
from karrot.places.factories import PlaceFactory
from karrot.users.factories import VerifiedUserFactory


class HistoryQuerySetTests(TestCase):
    def setUp(self):
        self.user = VerifiedUserFactory()
        self.group = GroupFactory(members=[self.user])
        self.place = PlaceFactory(group=self.group)
        self.activity = ActivityFactory(place=self.place)

    def create_history(self, **kwargs):
        return History.objects.create(
            typus=HistoryTypus.ACTIVITY_LEAVE,
            group=self.activity.place.group,
            place=self.activity.place,
            activity=self.activity,
            users=[self.user],
            payload=ActivitySerializer(instance=self.activity).data,
            **kwargs,
        )

    def test_activity_left_late(self):
        leave_seconds_before_activity = 324
        history = self.create_history(date=self.activity.date.start - timedelta(seconds=leave_seconds_before_activity))
        annotated = History.objects.annotate_activity_leave_seconds().get(pk=history.id)
        self.assertEqual(annotated.activity_leave_seconds, leave_seconds_before_activity)
        self.assertEqual(History.objects.activity_left_late(seconds=leave_seconds_before_activity).count(), 1)
        self.assertEqual(History.objects.activity_left_late(seconds=leave_seconds_before_activity - 1).count(), 0)
