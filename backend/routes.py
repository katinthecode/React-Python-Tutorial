from app import app, db
from flask import request, jsonify
from models import Friend

def get_img_url(name, gender):
    # Fetch avatar image based on gender
    if gender == "male":
        return f"https://avatar.iran.liara.run/public/boy?username={name}"
    elif gender == "female":
        return f"https://avatar.iran.liara.run/public/girl?username={name}"
    else:
        return None
    
# Get all friends
@app.route("/api/friends",methods=["GET"])
def get_friends():
    friends = Friend.query.all()
    result = [friend.to_json() for friend in friends] # Loops through all friends and puts it in a list
    return jsonify(result)

# Get a friend
@app.route("/api/friends/<int:id>",methods=["GET"])
def get_friend(id):
    friend = Friend.query.get(id)

    if friend is None:
        return jsonify({"error":"Friend not found"}),404
    
    return jsonify(friend.to_json())

# Create a friend
@app.route("/api/friends",methods=["POST"])
def create_friend():
    try:
        data = request.json

        # Validation
        fields_missing = ""
        required_fields = ["name","role","description","gender"]
        for field in required_fields:
            if field not in data or not data.get(field):
                if fields_missing == "":
                    fields_missing = field
                else:
                    fields_missing += f", {field}"
        
        if fields_missing != "":
            return jsonify({"error":f'Missing required field(s):  {fields_missing}'}),400

        name = data.get("name")
        role = data.get("role")
        description = data.get("description")
        gender = data.get("gender")
        img_url = get_img_url(name, gender)

        new_friend = Friend(name=name, role=role, description=description, gender=gender, img_url=img_url)

        db.session.add(new_friend)
        db.session.commit()

        return jsonify(new_friend.to_json()),201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),500
    
# Delete a friend
@app.route("/api/friends/<int:id>",methods=["DELETE"])
def delete_friend(id):
    try:
        friend = Friend.query.get(id)

        if friend is None:
            return jsonify({"error":"Friend not found"}),404
        
        db.session.delete(friend)
        db.session.commit()

        return jsonify({"msg":"Friend deleted"}),200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),500
    
# Update a friend
@app.route("/api/friends/<int:id>",methods=["PATCH"])
def update_friend(id):
    try:
        friend = Friend.query.get(id)

        if friend is None:
            return jsonify({"error":"Friend not found"}),404

        data = request.json

        friend.name = data.get("name", friend.name)
        friend.role = data.get("role", friend.role)
        friend.description = data.get("description", friend.description)

        if friend.gender != data.get("gender", friend.gender):
            friend.gender = data.get("gender", friend.gender)
            friend.img_url = get_img_url(friend.name, friend.gender)

        db.session.commit()

        return jsonify(friend.to_json()),200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),500