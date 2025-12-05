from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


def get_interest_matrix(db):
    users = []
    user_ids = []
    user_map = {}

    # Get all users and create mapping
    for user_key, user_data in db.data["users"].items():
        full_name = f"{user_data['firstname']} {user_data['lastname']}"
        users.append(full_name)
        user_ids.append(user_key)
        user_map[user_key] = full_name

    # Initialize 2D array
    n = len(users)
    matrix = [[False] * n] * n

    # Populate the matrix
    for user_key, user_interests in db.data["interests"].items():
        if user_key in user_map:
            from_idx = users.index(user_map[user_key])
            for target_key in user_interests:
                if target_key in user_map:
                    to_idx = users.index(user_map[target_key])
                    matrix[from_idx][to_idx] = True

    return {"users": users, "user_ids": user_ids, "matrix": matrix}


@router.get("/admin")
async def admin_page():
    return FileResponse("static/admin.html")


@router.get("/admin/matrix")
async def admin_matrix(db=None):
    return get_interest_matrix(db)
