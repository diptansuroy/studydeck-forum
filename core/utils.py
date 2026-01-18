import re
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser

def send_async_mail(subject, message, recipient_list):
    """Wrapper to send mail (Console for now, SMTP later)"""
    if not recipient_list:
        return
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=True
        )
        print(f"Email sent to: {recipient_list}")
    except Exception as e:
        print(f"Email Failed: {e}")

def notify_mentions(content, sender, thread, context_url):
    """
    Parses content for @username and sends emails.
    """
    mentioned_usernames = set(re.findall(r'@(\w+)', content))
    
    if not mentioned_usernames:
        return

    users_to_notify = CustomUser.objects.filter(
        username__in=mentioned_usernames
    ).exclude(id=sender.id)

    emails = [u.email for u in users_to_notify]
    if emails:
        subject = f"You were mentioned in: {thread.title}"
        message = (
            f"Hello,\n\n"
            f"{sender.username} mentioned you in a post on StudyDeck.\n\n"
            f"Thread: {thread.title}\n"
            f"Snippet: \"{content[:100]}...\"\n\n"
            f"View here: http://127.0.0.1:8000/thread/{thread.id}/"
        )
        send_async_mail(subject, message, emails)

def notify_thread_reply(thread, replier, content):
    """
    Notify the thread author that someone replied.
    """
    if thread.author == replier:
        return  # Don't notify if replying to self

    subject = f"New Reply on: {thread.title}"
    message = (
        f"Hello {thread.author.username},\n\n"
        f"{replier.username} just replied to your thread.\n\n"
        f"Reply: \"{content[:100]}...\"\n\n"
        f"Check it out: http://127.0.0.1:8000/thread/{thread.id}/"
    )
    send_async_mail(subject, message, [thread.author.email])

def notify_thread_status(thread, action, moderator):
    """
    Notify author if their thread is Locked or Pinned.
    """
    if thread.author == moderator:
        return

    subject = f"Your thread has been {action}"
    message = (
        f"Hello {thread.author.username},\n\n"
        f"A moderator ({moderator.username}) has {action} your thread: '{thread.title}'.\n\n"
        f"View status: http://127.0.0.1:8000/thread/{thread.id}/"
    )
    send_async_mail(subject, message, [thread.author.email])