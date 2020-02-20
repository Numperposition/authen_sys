from django.db import models


#import django.db.backends.mysql.operations

# Create your models here.

class userInfo(models.Model):

    user_name = models.CharField(max_length=255, blank=True, null=True)
    # user_password = models.CharField(max_length=20)
    user_email = models.CharField(max_length=255, blank=True, null=True)
    token = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'userInfo'

# class userToken(models.Model):
#     token = models.IntegerField()
#     user = models.ForeignKey(userInfo, on_delete=models.CASCADE)
