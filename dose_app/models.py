from django.db import models
import datetime
#from django.core.urlresolvers import reverse


# Create your models here.
class ModelPatient(models.Model):

    name = models.CharField(max_length=256)
    name_for_URL = models.CharField(max_length=256)
    dob = models.CharField(max_length=128)
    dob_parsed = models.DateField(default=datetime.date(9999,12,30))
    sex = models.CharField(max_length=128)

    number_of_studies = models.PositiveIntegerField(default=0)
    dose_PKA_complete = models.DecimalField(decimal_places=2, max_digits=64, default=0)
    dose_KAPR_complete = models.DecimalField(decimal_places=2, max_digits=64, default=0)

    deleted = models.BooleanField(default=False)
    mistaken = models.BooleanField(default=False)


class ModelStudyXA(models.Model):

    patient = models.ForeignKey(ModelPatient, related_name='xa_studies', on_delete=models.CASCADE)

    uid = models.CharField(max_length=256)

    institution = models.CharField(max_length=256, default='HUCAM')

    kv = models.IntegerField(default=0)

    study_date = models.CharField(max_length=128)
    study_date_parsed = models.DateField(default=datetime.date(9999,12,30))

    study_time = models.CharField(max_length=32, default="000000.000000")
    study_time_parsed = models.TimeField(default=datetime.time(0,0,0))

    dose_KAPR_total = models.DecimalField(decimal_places=2, max_digits=64)
    dose_PKA_total = models.DecimalField(decimal_places=2, max_digits=64)

    fluoro_KAPR_total = models.DecimalField(decimal_places=2, max_digits=64)
    fluoro_PKA_total = models.DecimalField(decimal_places=2, max_digits=64)

    acq_KAPR_total = models.DecimalField(decimal_places=2, max_digits=64)
    acq_PKA_total = models.DecimalField(decimal_places=2, max_digits=64)

    fluoro_time_total = models.DecimalField(decimal_places=2, max_digits=64)
    acq_time_total = models.DecimalField(decimal_places=2, max_digits=64)

    deleted = models.BooleanField(default=False)
    mistaken = models.BooleanField(default=False)


class ModelRequestName(models.Model):
    name = models.CharField(max_length=15000, default='', blank=True )
    full_info = models.TextField(max_length=32768, default='', blank=True)
    priority = models.PositiveIntegerField(default=0)
    ready = models.BooleanField(default=False)


class ModelRequestUIDs(models.Model):
    uids = models.CharField(max_length=4096, default='', blank=True)
    full_info = models.TextField(max_length=32768, default='', blank=True)
    priority = models.PositiveIntegerField(default=0)
    ready = models.BooleanField(default=False)


class ModelRequestDateFixed(models.Model):
    days_back = models.PositiveIntegerField(default=0)
    months_back = models.PositiveIntegerField(default=0)
    full_info = models.TextField(max_length=32768, default='', blank=True)
    priority = models.PositiveIntegerField(default=0)
    ready = models.BooleanField(default=False)


class ModelRequestDatePeriod(models.Model):
    date_before = models.CharField(max_length=256, default='', blank=True )
    date_after = models.CharField(max_length=256, default='', blank=True )
    full_info = models.TextField(max_length=32768, default='', blank=True)
    priority = models.PositiveIntegerField(default=0)
    ready = models.BooleanField(default=False)


class ModelDeletedUID(models.Model):
    del_uid = models.CharField(max_length=256)

