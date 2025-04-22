from flask import Flask
import sqlite3
from database import create_connection

app = Flask(__name__)

class BaseModel:
    """Base model with common database operations"""
    
    @staticmethod
    def execute_query(query, params=(), fetch_one=False):
        """Helper method to execute database queries"""
        conn = None
        cursor = None
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            
            if fetch_one:
                return cursor.fetchone()
            return cursor.rowcount
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()







class UserModel(BaseModel):
    """Handles all user-related database operations"""
    
    @staticmethod
    def create(name, gender, phone, email, password):
        """Create a new user"""
        query = """
        INSERT INTO users (name, gender, phone, email, password, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?, CURRENT_DATE, CURRENT_DATE)
        """
        try:
            rows_affected = BaseModel.execute_query(
                query, 
                (name, gender, phone, email, password)
            )
            return rows_affected > 0
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    @staticmethod
    def update_user(id, name, gender, phone, email):
        """Update user details"""
        query = """
        UPDATE users
        SET name = ?, gender = ?, phone = ?, email = ?, updatedAt = CURRENT_DATE
        WHERE id = ?
        """
        try:
            rows_affected = BaseModel.execute_query(
                query,
                (name, gender, phone, email, id)
            )
            return rows_affected > 0
        except Exception as e:
            raise Exception(f"Failed to update user: {str(e)}")
    
    @staticmethod
    def find_by_id(id):
        """Find user by id"""
        query = "SELECT * FROM users WHERE id=?"
        try:
            result = BaseModel.execute_query(query, (id,), fetch_one=True)
            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "gender": result[2],
                    "phone": result[3],
                    "email": result[4],
                    "password": result[5]
                }
            return None
        except Exception as e:
            raise Exception(f"Failed to find user: {str(e)}")

    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        query = "SELECT * FROM users WHERE email=?"
        try:
            result = BaseModel.execute_query(query, (email,), fetch_one=True)
            if result:
                return {
                    "id": result[0],
                    "name": result[1],
                    "gender": result[2],
                    "phone": result[3],
                    "email": result[4],
                    "password": result[5]
                }
            return None
        except Exception as e:
            raise Exception(f"Failed to find user: {str(e)}")

    @staticmethod
    def update_password(email, new_password):
        """Update user password"""
        query = "UPDATE users SET password=?, updatedAt=CURRENT_DATE WHERE email=?"
        try:
            rows_affected = BaseModel.execute_query(query, (new_password, email))
            if rows_affected == 0:
                raise Exception("No user found with that email")
            return True
        except Exception as e:
            raise Exception(f"Failed to update password: {str(e)}")



class ContactModel(BaseModel):
    """Handles all contact-related database operations"""
    
    @staticmethod
    def create(contact_name, contact_phone, contact_email, contact_address, contact_gender, contact_favorite, user_id):
        """Create a new contact"""
        query = """
        INSERT INTO contacts 
        (contact_name, contact_phone, contact_email, contact_address, contact_gender, contact_favorite, user_id, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_DATE, CURRENT_DATE)
        """
        try:
            rows_affected = BaseModel.execute_query(
                query,
                (contact_name, contact_phone, contact_email, contact_address, contact_gender, contact_favorite, user_id)
            )
            return rows_affected > 0
        except Exception as e:
            raise Exception(f"Failed to create contact: {str(e)}")

    @staticmethod
    def get_all(user_id):
        """Get all contacts for a user"""
        query = "SELECT * FROM contacts WHERE user_id=?"
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            
            contacts = []
            for result in results:
                contacts.append({
                    "id": result[0],
                    "contact_name": result[1],
                    "contact_phone": result[2],
                    "contact_email": result[3],
                    "contact_address": result[4],
                    "contact_gender": result[5],
                    "contact_favorite": result[6],
                    "user_id": result[7]
                })
            return contacts
        except Exception as e:
            raise Exception(f"Failed to get contacts: {str(e)}")
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_by_id(contact_id, user_id):
        """Get a single contact by ID"""
        query = "SELECT * FROM contacts WHERE id=? AND user_id=?"
        try:
            result = BaseModel.execute_query(query, (contact_id, user_id), fetch_one=True)
            if result:
                return {
                    "id": result[0],
                    "contact_name": result[1],
                    "contact_phone": result[2],
                    "contact_email": result[3],
                    "contact_address": result[4],
                    "contact_gender": result[5],
                    "contact_favorite": result[6],
                    "user_id": result[7]
                }
            return None
        except Exception as e:
            raise Exception(f"Failed to get contact: {str(e)}")

    @staticmethod
    def update(contact_id, user_id, **kwargs):
        """Update contact information"""
        if not kwargs:
            raise Exception("No fields to update provided")
            
        set_clause = ", ".join([f"{key}=?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.extend([contact_id, user_id])
        
        query = f"""
        UPDATE contacts 
        SET {set_clause}, updatedAt=CURRENT_DATE
        WHERE id=? AND user_id=?
        """
        try:
            rows_affected = BaseModel.execute_query(query, values)
            if rows_affected == 0:
                raise Exception("Contact not found or not owned by user")
            return True
        except Exception as e:
            raise Exception(f"Failed to update contact: {str(e)}")

    @staticmethod
    def delete(contact_id, user_id):
        """Delete a contact"""
        query = "DELETE FROM contacts WHERE id=? AND user_id=?"
        try:
            rows_affected = BaseModel.execute_query(query, (contact_id, user_id))
            if rows_affected == 0:
                raise Exception("Contact not found or not owned by user")
            return True
        except Exception as e:
            raise Exception(f"Failed to delete contact: {str(e)}")
        
    @staticmethod
    def get_added_contact(phone, user_id):
        # get added contact by phone number
        query = "SELECT * FROM contacts where contact_phone=? AND user_id=?"
        try:
            result = BaseModel.execute_query(query, (phone, user_id), fetch_one=True)
            if result:
                return {
                    "id": result[0],
                    "contact_name": result[1],
                    "contact_phone": result[2],
                    "contact_email": result[3],
                    "contact_address": result[4],
                    "contact_gender": result[5],
                    "contact_favorite": result[6],
                    "user_id": result[7]
                }
            return None
        except Exception as e:
            raise Exception(f"Failed to get added contact: {str(e)}")


def get_profile(user_id):
    try:
        query = """
                SELECT 
                    id,
                    name,
                    gender,
                    phone,
                    email,
                    createdAt,
                    updatedAt,
                    (SELECT COUNT(*) FROM contacts WHERE user_id=users.id) AS contacts
                FROM users    
                WHERE id=?"""
        result = BaseModel.execute_query(query, (user_id,), fetch_one=True)
        return result if result else None
    except Exception as e:
        raise Exception(f"Error retrieving profile: {str(e)}")