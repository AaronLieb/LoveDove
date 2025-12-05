from fastapi import FastAPI, HTTPException, Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from database import Database
import admin
import email_service

app = FastAPI(title="LoveDove", description="Find out if someone is in love with you")
db = Database()

app.mount("/static", StaticFiles(directory="static"), name="static")


class User(BaseModel):
    firstname: str
    lastname: str
    password: str
    email: Optional[str] = None


class Interest(BaseModel):
    firstname: str
    lastname: str
    password: str
    target_firstname: str
    target_lastname: str


class UpdateDescription(BaseModel):
    password: str
    description: str


@app.get("/")
async def read_root():
    return FileResponse("static/index.html")


@app.get("/register")
async def register_page():
    return FileResponse("static/register.html")


@app.post("/register")
async def register(user: User):
    try:
        db.create_user(user.firstname, user.lastname, user.password, user.email)
        return {"message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/interest")
async def express_interest(interest: Interest):
    user = db.get_user(interest.firstname, interest.lastname)
    if not user or user["password"] != interest.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    is_mutual = db.check_mutual_interest(
        interest.firstname,
        interest.lastname,
        interest.target_firstname,
        interest.target_lastname,
    )

    db.add_interest(
        interest.firstname,
        interest.lastname,
        interest.target_firstname,
        interest.target_lastname,
    )

    if is_mutual:
        # Send emails to both users if they have email addresses
        target_user = db.get_user(interest.target_firstname, interest.target_lastname)

        user_name = f"{user['firstname']} {user['lastname']}"
        target_name = f"{target_user['firstname']} {target_user['lastname']}"

        email_service.send_match_email(user.get("email"), user_name, target_name)
        email_service.send_match_email(target_user.get("email"), target_name, user_name)

        return {"message": "🎉 You are in love! 💕"}
    else:
        return {"message": "Interest recorded"}


@app.get("/admin")
async def admin_page():
    return FileResponse("static/admin.html")


@app.get("/admin/matrix")
async def admin_matrix():
    return admin.get_interest_matrix(db)


@app.get("/user/{user_id}")
async def user_profile(user_id: str = Path(...)):
    return FileResponse("static/profile.html")


@app.get("/api/user/{user_id}")
async def get_user_profile(user_id: str = Path(...)):
    if user_id not in db.data["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    user = db.data["users"][user_id]

    return {
        "firstname": user["firstname"],
        "lastname": user["lastname"],
        "description": user.get("description", ""),
    }


@app.post("/api/user/{user_id}/description")
async def update_description(user_id: str, update: UpdateDescription):
    if user_id not in db.data["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    user = db.data["users"][user_id]
    if user["password"] != update.password:
        raise HTTPException(status_code=401, detail="Invalid password")

    db.data["users"][user_id]["description"] = update.description
    db._save_data()
    return {"message": "Description updated successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
