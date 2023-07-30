from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
import json
import boto3

class Subscription(models.Model):
    RESOURCE_TYPES = (
        ('ec2', 'ec2'),
        ('s3', 's3'),
        ('lambda', 'lambda'),
    )

    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    email = models.EmailField()

    class Meta:
        unique_together = (('email', 'resource_type'),)

    def __str__(self):
        return f"{self.resource_type}: {self.email}"

    def save(self, *args, **kwargs):
        save_subscription_data(self.email, self.resource_type)
        super(Subscription, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        remove_subscription_data(self.email, self.resource_type)
        super(Subscription, self).delete(*args, **kwargs)


def save_subscription_data(email, resource_type):
    s3_bucket_name = 'b00946272-subscriptions' 
    s3_file_name = 'subscriptions.json'

    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(s3_bucket_name, s3_file_name)
        json_data = obj.get()['Body'].read().decode('utf-8')
        data = json.loads(json_data)
    except Exception as e:
        data = {}

    if data.get(resource_type) is None:
        data[resource_type] = [email]
    else:
        data[resource_type].append(email)

    json_data = json.dumps(data)
    obj.put(Body=json_data)


def remove_subscription_data(email, resource_type):
    s3_bucket_name = 'b00946272-subscriptions'
    s3_file_name = 'subscriptions.json'

    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(s3_bucket_name, s3_file_name)
        json_data = obj.get()['Body'].read().decode('utf-8')
        data = json.loads(json_data)
    except Exception as e:
        return

    if resource_type in data and email in data[resource_type]:
        data[resource_type].remove(email)

        json_data = json.dumps(data)
        obj.put(Body=json_data)


@receiver(post_delete, sender=Subscription)
def subscription_deleted(sender, instance, **kwargs):
    remove_subscription_data(instance.email, instance.resource_type)
