from django.db import models
from account.models import User
from pgvector.django import VectorField
from django.db.models.signals import post_save
from django.dispatch import receiver
# from sentence_transformers import SentenceTransformer
from django.conf import settings
import requests
from django.contrib.postgres.fields import ArrayField
from openai import OpenAI
import openai
# Create your models here.

class GroupPost(models.Model):
    group_id = models.BigIntegerField()
    message_id = models.BigIntegerField()
    text = models.TextField(blank=True, null=True)
    image_links = models.JSONField(default=list)
    media_group_id = models.BigIntegerField(null=True, blank=True)
    embedding = VectorField(
        dimensions=384,
        help_text="Vector embeddings (clip-vit-large-patch14) of the file content",
        null=True,
        blank=True,
    )
    display_text = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group_id', 'message_id')

    def __str__(self):
        return f"Post {self.message_id} in group {self.group_id}"

class UserBot(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (owned by {self.owner})"


class SearchSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    search_term = models.TextField()
    viewed_ids = ArrayField(models.BigIntegerField(), default=list)
    page = models.IntegerField(default=1)
    embedding = VectorField(
        dimensions=384,
        help_text="Vector embeddings (clip-vit-large-patch14) of the search term",
        null=True,
        blank=True,
    )

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=settings.GROQ_API_KEY
)

@receiver(post_save, sender=GroupPost)
def enrich_post_with_tags_and_embedding(sender, instance, created, **kwargs):
    if not instance.text:
        return

    # Skip if tags already exist
    if instance.tags and len(instance.embedding) > 0:
        return

    # 1. Send prompt to DeepSeek
    prompt = f"""
You are a helpful assistant. Based on the user's description, extract a list of relevant product tags or keywords that can help solve the user's problem. 

If the user provides input in a language other than English, try to understand the user's need by translating their input to English first. Then, extract tags based on the English translation. Do not reply with any other detail, just provide the comma-separated list of tags that represent the products or solutions the user might need.

The tags should include:
1. Individual keywords (e.g., 'red', 'jacket', 'cream', 'lotion').
2. Common variations or synonyms (e.g., 'red jacket', 'red coat', 'moisturizer', 'skin care lotion') that best describe the product solutions.

If the user describes a problem but doesn't explicitly ask for a solution, try to infer a possible product that could address the problem in a quick, impulsive way.

The tags should capture all relevant aspects of the product as described in the user's message, including solutions that someone would consider buying impulsively to address their immediate need.
Remove any phone numbers, gmails, usernames or other form of contact message and avoid combining words with underscore since user will send just normal user query use space to separate any combination and comma for separate tags
Response (comma-separated list of tags and possible solutions):
Dont include extra words like here is the tags... your response is going to be  saved on database so be sharp
""".strip()

    # deepseek
    # response = client.chat.completions.create(
    #     model="deepseek-chat",
        # messages=[
        #     {"role": "system", "content": prompt},
        #     {"role": "user", "content": instance.text},
        # ],
    #     stream=False
    # )
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # or "gpt-4"
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": instance.text},
        ],
    )
    
    # Call DeepSeek or your LLM
    tags = response.choices[0].message.content
    print('tags', tags)

    try:
        payload = {"text": instance.text + ' ' + tags}
        r = requests.post(f"{settings.ENCODER_SERVER_SCHEME}://{settings.ENCODER_SERVER_HOST}:{settings.ENCODER_SERVER_PORT}/encode", json=payload, timeout=10)
        r.raise_for_status()
        embedding = r.json().get("embedding")
        if embedding:
            instance.tags = tags
            instance.embedding = embedding
            instance.save(update_fields=["tags", "embedding"])
        else:
            instance.tags = tags
            instance.save(update_fields=["tags"])
            print("No embedding returned from encoder server")
    except Exception as e:
        print(f"Error calling encoder server: {e}")