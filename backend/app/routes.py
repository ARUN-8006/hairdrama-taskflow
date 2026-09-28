from flask import Blueprint, jsonify, request
from datetime import datetime, timezone

from .db import supabase
from .auth import verify_google_id_token, issue_session, require_auth
from .email_service import send_email


api = Blueprint("api", __name__)


def db_required():
    if not supabase:
        return jsonify({"error": "Database is not configured"}), 503
    return None


# =========================================================
# GOOGLE LOGIN
# =========================================================

@api.post("/auth/google")
def google_login():
    missing = db_required()
    if missing:
        return missing

    body = request.get_json(silent=True) or {}
    credential = body.get("credential")

    if not credential:
        return jsonify({
            "error": "Google credential is required"
        }), 400

    try:
        info = verify_google_id_token(credential)

        google_id = info.get("sub")
        email = info.get("email")
        name = info.get("name") or email.split("@")[0]
        picture = info.get("picture")

        if not google_id or not email or not info.get("email_verified"):
            return jsonify({
                "error": "Google account is not verified"
            }), 401

        existing = (
            supabase
            .table("users")
            .select("*")
            .eq("google_id", google_id)
            .execute()
            .data
        )

        if existing:
            user = existing[0]

            (
                supabase
                .table("users")
                .update({
                    "name": name,
                    "avatar_url": picture,
                    "email": email
                })
                .eq("id", user["id"])
                .execute()
            )

            user = (
                supabase
                .table("users")
                .select("*")
                .eq("id", user["id"])
                .single()
                .execute()
                .data
            )

        else:
            (
                supabase
                .table("users")
                .insert({
                    "google_id": google_id,
                    "email": email,
                    "name": name,
                    "avatar_url": picture
                })
                .execute()
            )

            user = (
                supabase
                .table("users")
                .select("*")
                .eq("google_id", google_id)
                .single()
                .execute()
                .data
            )

        token = issue_session(user)

        return jsonify({
            "token": token,
            "user": user
        }), 200

    except Exception as exc:
        print("GOOGLE AUTH ERROR:", repr(exc))

        return jsonify({
            "error": "Google authentication failed",
            "detail": str(exc)
        }), 401


# =========================================================
# USERS
# =========================================================

@api.get("/users")
@require_auth
def users(current):
    missing = db_required()
    if missing:
        return missing

    data = (
        supabase
        .table("users")
        .select("id,name,email,avatar_url")
        .neq("id", current["id"])
        .order("name")
        .execute()
        .data
    )

    return jsonify({
        "users": data
    })


# =========================================================
# CURRENT USER
# =========================================================

@api.get("/me")
@require_auth
def me(current):
    return jsonify({
        "user": current
    })


# =========================================================
# GET TASKS
# =========================================================

@api.get("/tasks")
@require_auth
def get_tasks(current):
    missing = db_required()
    if missing:
        return missing

    created = (
        supabase
        .table("tasks")
        .select(
            "*, "
            "created_by_user:created_by(id,name,email), "
            "assigned_user:assigned_to(id,name,email)"
        )
        .eq("created_by", current["id"])
        .order("created_at", desc=True)
        .execute()
        .data
    )

    assigned = (
        supabase
        .table("tasks")
        .select(
            "*, "
            "created_by_user:created_by(id,name,email), "
            "assigned_user:assigned_to(id,name,email)"
        )
        .eq("assigned_to", current["id"])
        .order("created_at", desc=True)
        .execute()
        .data
    )

    return jsonify({
        "created": created,
        "assigned": assigned
    })


# =========================================================
# CREATE TASK
# =========================================================

@api.post("/tasks")
@require_auth
def create_task(current):
    missing = db_required()
    if missing:
        return missing

    body = request.get_json(silent=True) or {}

    title = (body.get("title") or "").strip()
    description = (body.get("description") or "").strip()
    assigned_to = body.get("assigned_to")

    if not title or len(title) > 120:
        return jsonify({
            "error": "Title is required and must be 120 characters or less"
        }), 400

    if not assigned_to:
        return jsonify({
            "error": "Assignee is required"
        }), 400

    try:
        # Find assigned user
        assignee = (
            supabase
            .table("users")
            .select("id,name,email")
            .eq("id", assigned_to)
            .single()
            .execute()
            .data
        )

        if not assignee:
            return jsonify({
                "error": "Assigned user was not found"
            }), 404

        # Create task
        (
            supabase
            .table("tasks")
            .insert({
                "title": title,
                "description": description,
                "created_by": current["id"],
                "assigned_to": assigned_to
            })
            .execute()
        )

        # Get newly created task
        task_result = (
            supabase
            .table("tasks")
            .select("*")
            .eq("created_by", current["id"])
            .eq("assigned_to", assigned_to)
            .eq("title", title)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
            .data
        )

        if not task_result:
            return jsonify({
                "error": "Task was created but could not be retrieved"
            }), 500

        task = task_result[0]

        # Send assignment email.
        # Email failure should not make task creation fail.
        try:
            send_email(
                assignee["email"],
                f"New task assigned: {title}",
                f"""Hi {assignee['name']},

You have been assigned a new task.

Title: {title}
Description: {description or 'No description'}

Please open the task manager to review it."""
            )

            print("TASK EMAIL SENT:", assignee["email"])

        except Exception as email_error:
            print("EMAIL SEND ERROR:", repr(email_error))

        return jsonify({
            "task": task
        }), 201

    except Exception as exc:
        print("CREATE TASK ERROR:", repr(exc))

        return jsonify({
            "error": "Could not create task",
            "detail": str(exc)
        }), 400


# =========================================================
# COMPLETE TASK
# =========================================================

@api.patch("/tasks/<task_id>/complete")
@require_auth
def complete_task(current, task_id):
    missing = db_required()
    if missing:
        return missing

    try:
        # Get task
        task = (
            supabase
            .table("tasks")
            .select(
                "*, "
                "created_by_user:created_by(id,name,email), "
                "assigned_user:assigned_to(id,name,email)"
            )
            .eq("id", task_id)
            .single()
            .execute()
            .data
        )

        if not task:
            return jsonify({
                "error": "Task not found"
            }), 404

        # Only assigned user can complete task
        if task["assigned_to"] != current["id"]:
            return jsonify({
                "error": "Only the assigned user can complete this task"
            }), 403

        # Already completed
        if task["status"] == "completed":
            return jsonify({
                "task": task
            }), 200

        # Update status
        completed_at = datetime.now(timezone.utc).isoformat()

        (
            supabase
            .table("tasks")
            .update({
                "status": "completed",
                "completed_at": completed_at
            })
            .eq("id", task_id)
            .execute()
        )

        # Get updated task
        updated = (
            supabase
            .table("tasks")
            .select("*")
            .eq("id", task_id)
            .single()
            .execute()
            .data
        )

        # Notify creator
        creator_email = None

        if task.get("created_by_user"):
            creator_email = task["created_by_user"].get("email")

        if creator_email:
            try:
                send_email(
                    creator_email,
                    f"Task completed: {task['title']}",
                    f"""Hi,

Your task '{task['title']}' has been completed by
{current['name']} ({current['email']})."""
                )

                print("COMPLETION EMAIL SENT:", creator_email)

            except Exception as email_error:
                print(
                    "COMPLETION EMAIL ERROR:",
                    repr(email_error)
                )

        return jsonify({
            "task": updated
        }), 200

    except Exception as exc:
        print("COMPLETE TASK ERROR:", repr(exc))

        return jsonify({
            "error": "Could not complete task",
            "detail": str(exc)
        }), 400