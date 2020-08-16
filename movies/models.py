from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db import models


USER_MODEL = settings.AUTH_USER_MODEL


class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True


class Film(models.Model):
    title = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True, null=True)
    film_duration = models.DurationField(blank=True, verbose_name='Duration')
    start_show = models.DateField(null=True)
    is_deleted = models.BooleanField(default=True, db_index=True)
    image = models.ImageField(blank=True, null=True, upload_to='media/film_images/')
    image_title = models.ImageField(blank=True, null=True, upload_to='media/film_images/')

    @property
    def duration(self):
        duration = self.film_duration * 60
        return duration

    @property
    def end_show(self):
        end_show = self.start_show + timedelta(days=14)
        return end_show

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        super(Film, self).save(*args, **kwargs)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class Hall(TimestampModel):
    name = models.CharField(blank=True, max_length=80, unique=True)
    row = models.IntegerField(default=0)
    seat = models.IntegerField(default=0)

    @property
    def total_seats(self):
        total = self.row * self.seat
        return total

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        super(Hall, self).save(*args, **kwargs)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class Seance(TimestampModel):
    film = models.ForeignKey(Film, null=True, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, null=True, on_delete=models.CASCADE)
    beginning = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=0)
    price = models.FloatField(default=0)
    seats = models.IntegerField(default=0)
    is_editable = models.BooleanField(default=True)

    @property
    def seat_list(self):
        return [i for i in range(1, self.hall.seat+1)]

    @property
    def row_list(self):
        return [i for i in range(1, self.hall.row+1)]

    class Meta:
        db_table = "Seance"
        unique_together = ("id", "beginning", "hall")

    def save(self, *args, **kwargs):
        self.end = self.beginning + self.film.duration
        # if self.seats == 0 and self.created_at == None:
        #     self.seats = self.hall.total_seats
        # elif self.is_editable == True:
        super(Seance, self).save(*args, **kwargs)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.film} {self.beginning.strftime('%d %b %H:%M')}"


class Ticket(TimestampModel):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    seance = models.ForeignKey(Seance, null=True, on_delete=models.CASCADE)
    row = models.IntegerField(default=0)
    seat = models.IntegerField(default=0)

    class Meta:
        unique_together = ("seat", "row", "seance")

    def save(self, *args, **kwargs):
        super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.seance.film} {self.seance.beginning}"


