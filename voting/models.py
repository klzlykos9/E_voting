from django.db import models
from account.models import CustomUser
# Create your models here.


class Voter(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, unique=True)  # Used for OTP
    otp = models.CharField(max_length=10, null=True)
    verified = models.BooleanField(default=False)
    voted = models.BooleanField(default=False)
    otp_sent = models.IntegerField(default=0)  # Control how many OTPs are sent

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name

class VoterPhoto(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='voter_photos/%Y/%m/%d/')
    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['captured_at']

    def __str__(self):
        return f"Photo of {self.voter.admin.first_name} {self.voter.admin.last_name}"
    
    
class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_vote = models.IntegerField()
    priority = models.IntegerField()

    def __str__(self):
        return self.name


class Candidate(models.Model):
    fullname = models.CharField(max_length=50)
    photo = models.ImageField(upload_to="candidates")
    bio = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return self.fullname


class Votes(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

 
class Block(models.Model):
    index = models.IntegerField()
    previous_hash = models.CharField(max_length=256)
    timestamp = models.DateTimeField()
    nonce = models.IntegerField()
    hash = models.CharField(max_length=256)

class Transaction(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    voter = models.CharField(max_length=100)
    candidate = models.CharField(max_length=100)
