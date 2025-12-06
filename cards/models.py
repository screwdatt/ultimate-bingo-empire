from django.db import models

class Winner(models.Model):
    room = models.CharField(max_length=50)
    username = models.CharField(max_length=100)
    prize_type = models.CharField(max_length=20)  # one_line, two_lines, full_house
    prize_description = models.CharField(max_length=200)
    amount_gbp = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    won_at = models.DateTimeField(auto_now_add=True)
    selfie = models.ImageField(upload_to='selfies/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} won {self.prize_description} in {self.room}"

    class Meta:
        ordering = ['-won_at']
