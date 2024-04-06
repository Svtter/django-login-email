from django.db import models

# Create your models here.


class EmailLogin(models.Model):
    last_time = models.DateTimeField(auto_now_add=True, verbose_name="Last login request time")
    validated = models.BooleanField(default=False, verbose_name="Login Token validated")
    sault = models.CharField(max_length=100, verbose_name="Sault")
    email = models.EmailField(verbose_name="Email", unique=True, null=False)

    @classmethod
    def set_email_last_time(cls, email, datetime) -> "EmailLogin":
        obj, _ = cls.objects.get_or_create(email=email)
        obj.set_last_time(datetime)
        return obj

    def set_last_time(self, datetime):
        self.last_time = datetime
        self.validated = False
        self.save()

    def __str__(self) -> str:
        return f"Email: {self.email}"
