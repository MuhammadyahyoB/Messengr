from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist



# >>>>>>> User madeli <<<<<<
class User(AbstractUser):
    """ User model"""
    phone = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def user_groups(self):
        return GroupUsers.objects.filter(user=self)

    def __str__(self):
        return self.username


# >>>>>>> User Image Modeli <<<<<< 
class UserImage(models.Model):
    """ User Image model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user/image')
    date = models.DateField(auto_now_add=True)
    selected = models.BooleanField(default=False)


@receiver(pre_delete, sender=UserImage)
def delete_image_with_user(sender, instance, **kwargs):
    if instance.image:
        # Rasmi diskdan o'chirish
        instance.image.delete(False)


# >>>>>>>>> Group Modeli <<<<<< 
class Group(models.Model):
    """ Group model"""
    name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='group/avatar')
    description = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(Group, self).save(*args, **kwargs)
        group_user, created = GroupUsers.objects.get_or_create(
            user=self.author,
            group=self,
            is_admin=True
        )

        if not created:
            group_user.is_admin = True
            group_user.save()

    def __str__(self):
        return self.name

    @property
    def group_users(self):
        return GroupUsers.objects.filter(group=self)


# >>>>>> Group Users Modeli <<<<
class GroupUsers(models.Model):
    """ Group Users model"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        gr = GroupUsers.objects.filter(user=self.user, group=self.group).count()
        if gr == 0:
            super(GroupUsers, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} - {self.group}'


# >>>>>>>> Group Join Request Modeli <<<<< 
class GroupJoinedRequest(models.Model):
    """ Group Join Request model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=((1, 'New'),(2, 'Rejected'),))

    def save(self, *args, **kwargs):
        is_group = GroupUsers.objects.filter(user=self.user, group=self.group).count()
        is_status = GroupJoinedRequest.objects.filter(user=self.user, group=self.group, status=2).count()
        if is_group == 0 and is_status == 0:

            super(GroupJoinedRequest, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} - {self.group} - {self.status}'

# delete group user
@receiver(pre_delete, sender=GroupJoinedRequest)
def delete_group_user(sender, instance, **kwargs):
    try:
        group_user = GroupUsers.objects.create(
            user=instance.user,
            group=instance.group,
            is_admin=False
        )
    except Exception as e:
        if group_user:
            group_user.delete()
        raise e



# >>>>>>> Message Modeli <<<<<<<<<< 
class Message(models.Model):
    """ Message model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            GroupUsers.objects.get(user=self.user, group=self.group)
            super(Message, self).save(*args, **kwargs)
        except ObjectDoesNotExist:
            pass

    def __str__(self):
        return f'{self.user} - {self.group} - {self.text}'



# >>>>>>>>>> Message class <<<<<<<<<
class MessageFiles(models.Model):
    """Message Model"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    file = models.FileField(upload_to='message/file')

# delete
@receiver(pre_delete, sender=MessageFiles)
def delete_file_with_message(sender, instance, **kwargs):
    if instance.file:
        # faylni diskdan o'chirish
        instance.file.delete(False)
