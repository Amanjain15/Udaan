from __future__ import unicode_literals

from django.db import models

class ScreenData(models.Model):
	name = models.CharField(max_length=255, blank=False, null=False, unique=True)
	row_num = models.IntegerField(blank=False, null=False)
	def __unicode__(self):
		return self.name

class RowData(models.Model):
	name = models.CharField(max_length=255, blank=False, null=False)
	seat_num = models.IntegerField(blank=False, null=False)
	screen = models.ForeignKey(ScreenData)
	def __unicode__(self):
		return str(self.name)

class SeatData(models.Model):
	seat_no = models.IntegerField(blank=False, null=False)
	aisle_seat = models.BooleanField(default=False)
	row = models.ForeignKey(RowData)
	reserved = models.BooleanField(default=False)
	def __unicode__(self):
		return str(self.row.name + str(self.seat_no))

class ReservationData(models.Model):
	transaction_id = models.CharField(max_length=255, blank=False, null=False)
	seat_data = models.ForeignKey(SeatData)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
	def __unicode__(self):
		return str(self.transaction_id)
