
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone



class CustomUser(AbstractUser):
    """Custom user model with roles"""
    bio = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'core_customuser'

    def __str__(self):
        return self.email

    def is_moderator(self):
        return self.role in ['moderator', 'admin']

    def is_admin(self):
        return self.role == 'admin'


class Course(models.Model):
    """Course model"""
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=100)
    semester = models.IntegerField(default=1)
    credits = models.IntegerField(default=4)
    instructor = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_course'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.title}"


class Resource(models.Model):
    """Learning resource model"""
    RESOURCE_TYPES = [
        ('PDF', 'PDF Document'),
        ('VIDEO', 'Video'),
        ('LINK', 'Link'),
        ('NOTE', 'Notes'),
        ('ASSIGNMENT', 'Assignment'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='PDF')
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resources_uploaded')
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_resource'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.course.code}"

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class ResourceRating(models.Model):
    """Rating for resources"""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resource_ratings')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_resourcerating'
        unique_together = ['resource', 'user']

    def __str__(self):
        return f"{self.resource.title} - {self.rating}★ by {self.user.email}"


class Category(models.Model):
    """Forum Categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tagging system for threads"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_tag'
        ordering = ['name']

    def __str__(self):
        return self.name


class Thread(models.Model):
    """Forum thread (main discussion)"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='threads')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_threads')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='threads_created')
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, related_name='threads')

    # Moderation
    is_locked = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    # Engagement
    like_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_thread'
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.title} (in {self.category.name})"

    def lock_thread(self):
        self.is_locked = True
        self.save()

    def increment_reply_count(self):
        self.reply_count += 1
        self.save(update_fields=['reply_count'])

    def decrement_reply_count(self):
        self.reply_count = max(0, self.reply_count - 1)
        self.save(update_fields=['reply_count'])


class Reply(models.Model):
    """Reply to a thread"""
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()

    # Soft delete
    is_deleted = models.BooleanField(default=False)

    # Engagement
    like_count = models.IntegerField(default=0)
    is_answer = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_reply'
        ordering = ['-is_answer', '-created_at']

    def __str__(self):
        return f"Reply by {self.author.email} on {self.thread.title}"

    def soft_delete(self):
        if not self.is_deleted:
            self.is_deleted = True
            self.save(update_fields=['is_deleted'])
            self.thread.decrement_reply_count()

    def restore(self):
        if self.is_deleted:
            self.is_deleted = False
            self.save(update_fields=['is_deleted'])
            self.thread.increment_reply_count()


class Like(models.Model):
    """Likes for threads and replies"""
    CONTENT_TYPES = [
        ('thread', 'Thread'),
        ('reply', 'Reply'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_like'
        unique_together = [
            ('user', 'content_type', 'thread'),
            ('user', 'content_type', 'reply'),
        ]

    def __str__(self):
        if self.content_type == 'thread' and self.thread:
            return f"{self.user.email} liked {self.thread.title}"
        return f"{self.user.email} liked a reply"


class Report(models.Model):
    """Content reporting system"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    CONTENT_TYPES = [
        ('thread', 'Thread'),
        ('reply', 'Reply'),
    ]

    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports_created')
    moderator = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_handled',
        limit_choices_to={'role__in': ['moderator', 'admin']},
    )

    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')

    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    resolution_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_report'
        ordering = ['-created_at']

    def __str__(self):
        content = self.thread if self.content_type == 'thread' else self.reply
        return f"Report: {content} - {self.status}"

    def resolve(self, moderator, notes, action='resolved'):
        self.moderator = moderator
        self.status = action
        self.resolution_notes = notes
        self.resolved_at = timezone.now()
        self.save()
