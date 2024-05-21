from django.db.models.signals import post_save
from django.dispatch import receiver
from AI_courtroom.models import Courtroom, ChatHistory
from User_Profile.models import Case

@receiver(post_save, sender=Case)
def create_courtroom_for_case(sender, instance, created, **kwargs):
    if created:
        # Create a courtroom for the case
        courtroom = Courtroom.objects.create(case=instance, current_speaker='AI')
        
        # Create the initial chat message for case filing
        ChatHistory.objects.create(
            courtroom=courtroom,
            sender=instance.filed_by,
            sender_role='Petitioner',
            message=f"Case {instance.id} filed by {instance.filed_by.username} against {instance.case_against.username}",
        )
        
        # Create a chat message for the case details
        ChatHistory.objects.create(
            courtroom=courtroom,
            sender=instance.filed_by,  # Assuming this should not be attributed to a specific sender
            sender_role='Petitioner',  # Assuming the AI will provide the case details
            message=f"Case details: {instance.details}",
        )
