from django.db import models

# Create your models here.


class EmailLogin(models.Model):
    last_time = models.DateTimeField(auto_now_add=True, verbose_name="Last login request time")
    email = models.EmailField(verbose_name="Email")

    @classmethod
    def set_email_last_time(cls, email, datetime):
        obj, _ = cls.objects.get_or_create(email=email)
        obj.set_last_time(datetime)

    def set_last_time(self, datetime):
        self.last_time = datetime
        self.save()
