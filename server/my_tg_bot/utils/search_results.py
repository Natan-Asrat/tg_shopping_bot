from django.db.models import F, Value, TextField
from django.db.models.functions import Concat
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from groupbot.models import GroupPost, SearchSession
from asgiref.sync import sync_to_async
from pgvector.django import CosineDistance

async def get_sorted_posts_by_similarity(search_session: SearchSession):
    # Calculate pagination slice
    start_idx = (search_session.page - 1)
    
    # Base querysets with exclusions
    base_queryset = GroupPost.objects.filter(embedding__isnull=False)
    if search_session.viewed_ids:
        base_queryset = base_queryset.exclude(id__in=search_session.viewed_ids)
    
    # Get vector similarity results with pagination
    vector_posts = await sync_to_async(list)(
        base_queryset
        .annotate(similarity=CosineDistance('embedding', search_session.embedding))
        .order_by('similarity')[start_idx:start_idx+1]
    )

    # Get keyword search query with exclusions
    keyword_query = (
        base_queryset
        .annotate(
            search=SearchVector('tags'),
            rank=SearchRank(SearchVector('tags'), SearchQuery(search_session.search_term))
        )
        .filter(search=SearchQuery(search_session.search_term))
        .exclude(id__in=[p.id for p in vector_posts])  # Exclude already found vector results
        .order_by('-rank')
    )

    # Get keyword results with pagination
    keyword_posts = await sync_to_async(list)(
        keyword_query[start_idx:start_idx+1]
    )

    # Combine results (vector results first, then keyword results)
    combined_posts = vector_posts + keyword_posts
    
    # Update the search session with viewed IDs
    if combined_posts:
        search_session.viewed_ids = list(set(search_session.viewed_ids + [p.id for p in combined_posts]))
        await sync_to_async(search_session.save)()
    
    return combined_posts
