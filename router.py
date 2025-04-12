from flask import Blueprint, request, jsonify
import bcrypt
print("bcrypt is working!")
from schema import UserModel, ContactModel

routes = Blueprint("routes", __name__)

def validate_required_fields(data, required_fields):
    """Validate required fields in request data"""
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None

# ==================== Authentication Routes ====================

@routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    # Validate required fields
    valid, error = validate_required_fields(data, ["email", "password"])
    if not valid:
        return jsonify({"status": 400, "message": error}), 400
    
    try:
        user = UserModel.find_by_email(data["email"])
        if not user:
            return jsonify({"status": 404, "message": "User not found"}), 404
        
        
        password = data.get("password").encode('utf-8')
        stored_hash_password = user["password"].encode('utf-8')

        if not bcrypt.checkpw(password, stored_hash_password):
            return jsonify({"status": 401, "message": "Invalid credentials"}), 401

            
        return jsonify({
            "status": 200,
            "message": "Login successful!",
            "user": {
                "name": user["name"],
                "id": user["id"]
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": 500,
            "message": f"Login failed: {str(e)}"
        }), 500


@routes.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    data["gender"] = data["gender"].strip().lower()
    # Validate required fields
    required_fields = ["name", "email", "password", "gender", "phone"]
    valid, error = validate_required_fields(data, required_fields)
    if not valid:
        return jsonify({"status": 400, "message": error}), 400
    
    try:
        # Check if user already exists
        if UserModel.find_by_email(data["email"]):
            return jsonify({
                "status": 409,
                "message": "User with this email already exists"
            }), 409
        
        plain_password = data["password"].encode("utf-8") #convert to bytes
        hashed_password = bcrypt.hashpw(plain_password, bcrypt.gensalt()) # hash with salt
        print(data["name"], hashed_password)
            
        # Create new user
        UserModel.create(
            name=data["name"],
            gender=data["gender"],
            phone=data["phone"],
            email=data["email"],
            password=hashed_password.decode('utf-8')  # convert bytes to string before saving
        )
        
        return jsonify({
            "status": 201,
            "message": "User registered successfully"
        }), 201
        
    except Exception as e:
        return jsonify({
            "status": 500,
            "message": f"Registration failed: {str(e)}"
        }), 500


@routes.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    
    # Validate required fields
    valid, error = validate_required_fields(data, ["email", "password"])
    if not valid:
        return jsonify({"status": 400, "message": error}), 400
    
    try:
        # Check if user exists
        user = UserModel.find_by_email(data["email"])
        if not user:
            return jsonify({
                "status": 404,
                "message": "User not found"
            }), 404
        
        password = data["password"].encode("utf-8") #convert to bytes
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()) # hash with salt

        # Update password
        UserModel.update_password(data["email"], hashed_password.decode('utf-8'))
        return jsonify({
            "status": 200,
            "message": "Password updated successfully"
        })
        
    except Exception as e:
        return jsonify({
            "status": 500,
            "message": f"Password update failed: {str(e)}"
        }), 500


# ==================== Contact Management Routes ====================

@routes.route("/contacts/<int:user_id>", methods=["GET"])
def fetch_contacts(user_id):
    try:
        contacts = ContactModel.get_all(user_id)
        
        if not contacts:
            return jsonify({
                "status": 404,
                "message": "No contacts found"
            }), 404
            
        return jsonify({
            "status": 200,
            "count": len(contacts),
            "contacts": contacts
        })
        
    except Exception as e:
        return jsonify({
            "status": 500,
            "message": f"Failed to fetch contacts: {str(e)}"
        }), 500


@routes.route("/add-contact", methods=["POST"])
def add_contact():
    data = request.get_json()
    phone = data.get("contact_phone")
    user_id = data.get("user_id")
    
    # Validate required fields
    required_fields = ["contact_name", "contact_phone", "user_id"]
    valid, error = validate_required_fields(data, required_fields)
    if not valid:
        return jsonify({"status": 400, "message": error}), 400
    
    try:
        is_Exist = ContactModel.get_added_contact(phone, user_id)
        if is_Exist:
            return jsonify({
                "status": 409,
                "message": "Contact number already exists"
            }), 409


        # Create new contact
        ContactModel.create(
            contact_name=data["contact_name"],
            contact_phone=data["contact_phone"],
            contact_email=data.get("contact_email"),
            contact_address=data.get("contact_address"),
            contact_gender=data.get("contact_gender", "Other"),
            contact_favorite=data.get("contact_favorite", 0),
            user_id=data["user_id"]
        )

        added_contact = ContactModel.get_added_contact(phone, user_id)
        
        return jsonify({
            "status": 201,
            "message": "Contact added successfully",
            "data": added_contact
        }), 201
        
    except Exception as e:
        return jsonify({
            "status": 500,
            "message": f"Failed to add contact: {str(e)}"
        }), 500


@routes.route("/delete-contact/<int:contact_id>", methods=["DELETE"])
def delete_contact(contact_id):
    data = request.get_json()
    
    # Validate required fields
    if not data or "user_id" not in data:
        return jsonify({
            "status": 400,
            "message": "Missing user_id in request"
        }), 400
    
    try:
        ContactModel.delete(contact_id, data["user_id"])
        return jsonify({
            "status": 200,
            "message": "Contact deleted successfully"
        })
        
    except Exception as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            return jsonify({
                "status": 404,
                "message": error_message
            }), 404
        return jsonify({
            "status": 500,
            "message": f"Failed to delete contact: {error_message}"
        }), 500


@routes.route("/update-contact/<int:contact_id>", methods=["PUT"])
def update_contact(contact_id):
    data = request.get_json()
    
    # Validate required fields
    if not data or "user_id" not in data:
        return jsonify({
            "status": 400,
            "message": "Missing user_id in request"
        }), 400
    
    try:
        # Update contact fields
        update_data = {
            key: data[key] 
            for key in [
                "contact_name", 
                "contact_phone", 
                "contact_email", 
                "contact_address", 
                "contact_gender", 
                "contact_favorite"
            ] 
            if key in data
        }
        
        if not update_data:
            return jsonify({
                "status": 400,
                "message": "No valid fields provided for update"
            }), 400
        
        ContactModel.update(contact_id, data["user_id"], **update_data)
        return jsonify({
            "status": 200,
            "message": "Contact updated successfully"
        })
        
    except Exception as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            return jsonify({
                "status": 404,
                "message": error_message
            }), 404
        return jsonify({
            "status": 500,
            "message": f"Failed to update contact: {error_message}"
        }), 500