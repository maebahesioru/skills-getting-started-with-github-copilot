"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Club": {
        "description": "Practice soccer skills and play matches against other schools",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": []
    },
    "Swimming Club": {
        "description": "Swim training and endurance sessions in the school pool",
        "schedule": "Mondays and Wednesdays, 5:00 PM - 6:30 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Rehearse and perform plays, develop acting and stagecraft skills",
        "schedule": "Wednesdays and Saturdays, 4:00 PM - 6:00 PM",
        "max_participants": 16,
        "participants": []
    },
    "Photography Club": {
        "description": "Explore photography techniques and organize exhibitions",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": []
    },
    "Debate Team": {
        "description": "Prepare for debate tournaments and improve public speaking",
        "schedule": "Mondays and Thursdays, 4:30 PM - 6:00 PM",
        "max_participants": 16,
        "participants": []
    },
    "Science Club": {
        "description": "Conduct experiments, discuss scientific topics, and enter fairs",
        "schedule": "Tuesdays, 3:45 PM - 5:15 PM",
        "max_participants": 20,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
    participants = activity.get("participants", [])
    max_participants = activity.get("max_participants", 0)

    # Reject duplicate signups
    if email in participants:
        raise HTTPException(status_code=400, detail=f"Email {email} is already signed up for {activity_name}")

    # Reject if activity is full
    if len(participants) >= max_participants:
        raise HTTPException(status_code=400, detail=f"Activity {activity_name} is full")

    # Add student
    participants.append(email)
    activity["participants"] = participants
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants/{email}")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
    participants = activity.get("participants", [])

    # Validate participant exists
    if email not in participants:
        raise HTTPException(status_code=404, detail="Participant not found")

    # Remove student
    participants.remove(email)
    activity["participants"] = participants
    return {"message": f"Unregistered {email} from {activity_name}"}
