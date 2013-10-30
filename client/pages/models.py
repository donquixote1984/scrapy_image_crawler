from django.db import models

class Pages(models.Model):
    class Meta:
        db_table = 'pages'
    id=models.CharField(max_length=50,primary_key=True)
    url=models.CharField(max_length=200)
    time_added=models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=50)

class Images(models.Model):
    class Meta:
        db_table = 'images'
    id = models.CharField(max_length=50,primary_key=True)
    url = models.CharField(max_length=200)
    path = models.CharField(max_length=200)
    page = models.ForeignKey(Pages, to_field='url')
    time_added=models.DateTimeField(auto_now=True)
    last_update=models.DateTimeField(auto_now=True)
