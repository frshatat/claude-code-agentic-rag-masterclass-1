from supabase import Client

from app.db.supabase import get_supabase_for_token


def get_threads(user_id: str, access_token: str) -> list[dict]:
    client: Client = get_supabase_for_token(access_token)
    response = (
        client.table("threads")
        .select("*")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )
    return response.data


def get_thread(thread_id: str, user_id: str, access_token: str) -> dict | None:
    client: Client = get_supabase_for_token(access_token)
    response = (
        client.table("threads")
        .select("*, messages(*)")
        .eq("id", thread_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    return response.data


def create_thread(
    user_id: str,
    access_token: str,
    openai_thread_id: str,
    title: str | None,
) -> dict:
    client: Client = get_supabase_for_token(access_token)
    response = (
        client.table("threads")
        .insert(
            {
                "user_id": user_id,
                "openai_thread_id": openai_thread_id,
                "title": title,
            }
        )
        .execute()
    )
    return response.data[0]


def delete_thread(thread_id: str, user_id: str, access_token: str) -> None:
    client: Client = get_supabase_for_token(access_token)
    client.table("threads").delete().eq("id", thread_id).eq("user_id", user_id).execute()


def add_message(
    access_token: str,
    thread_id: str,
    role: str,
    content: str,
    openai_message_id: str | None = None,
) -> dict:
    client: Client = get_supabase_for_token(access_token)
    response = (
        client.table("messages")
        .insert(
            {
                "thread_id": thread_id,
                "role": role,
                "content": content,
                "openai_message_id": openai_message_id,
            }
        )
        .execute()
    )
    return response.data[0]
