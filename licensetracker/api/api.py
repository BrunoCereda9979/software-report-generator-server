from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Path
from typing import List
from django.db import IntegrityError
from api.models import (
    Software, Comment, Department, Vendor,
    ContactPerson, Division, GlAccount, 
    SoftwareToOperate, HardwareToOperate, User,
    BlacklistedToken
)
from api.schemas import (
    SoftwareSchema, SoftwareIn, SoftwareOut, SoftwareUpdate,
    CommentSchema, CommentIn, CommentOut, CommentUpdate,
    DepartmentSchema, VendorSchema, ContactPersonSchema,
    DivisionSchema, GlAccountSchema, SoftwareToOperateSchema,
    HardwareToOperateSchema, ErrorSchema, ContactPersonOut, 
    ContactPersonIn, UserCreateSchema, LoginSchema, UserResponseSchema,
    TokenSchema
)
from datetime import datetime
from django.core.validators import validate_email
from django.contrib.auth.hashers import make_password
from api.auth import AuthHandler, BearerAuth
from django.contrib.auth import logout
from django.db.models import Q
import logging
from django.conf import settings
import jwt

logger = logging.getLogger(__name__)

api_v1 = NinjaAPI(version="1.0.0", description="Software License Tracking Application API for Rocky Mount City")

@api_v1.get("software", response=List[SoftwareSchema])
def get_all_software(request):
    return Software.objects.all()

@api_v1.get("software/{id}", response=SoftwareSchema)
def get_software_by_id(request, id: int):
    return get_object_or_404(Software, id=id)

# Get all the comments for a Software
@api_v1.get("software/{software_id}/comments/", response=List[CommentSchema])
def get_comments_by_software_id(request, software_id: int = Path(...)):
    software = get_object_or_404(Software, id=software_id)
    comments = Comment.objects.filter(software_id=software_id)
    return comments

@api_v1.post("software", response={201: SoftwareOut, 400: ErrorSchema, 500: ErrorSchema})
def add_new_software(request, data: SoftwareIn):
    operational_status = ''
    
    try:
        if data.software_operational_status == 'Active':
            operational_status = 'A'
        elif data.software_operational_status == 'Inactive':
            operational_status = 'I'
          
        newSoftware = Software.objects.create(
            software_name=data.software_name,
            software_description=data.software_description,
            software_version=data.software_version,
            software_years_of_use=data.software_years_of_use,
            software_last_updated=data.software_last_updated,
            software_expiration_date=data.software_expiration_date,
            software_is_hosted=data.software_is_hosted,
            software_is_tech_supported=data.software_is_tech_supported,
            software_is_cloud_based=data.software_is_cloud_based,
            software_maintenance_support=data.software_maintenance_support,
            software_number_of_licenses=data.software_number_of_licenses,
            software_annual_amount=data.software_annual_amount,
            software_operational_status=operational_status
        )

        def extract_ids(objects):
            return [obj.id for obj in objects] if objects else []

        if data.software_department:
            newSoftware.software_department.set(extract_ids(data.software_department))
        if data.software_vendor:
            newSoftware.software_vendor.set(extract_ids(data.software_vendor))
        if data.software_department_contact_people:
            newSoftware.software_department_contact_people.set(extract_ids(data.software_department_contact_people))
        if data.software_to_operate:
            newSoftware.software_to_operate.set(extract_ids(data.software_to_operate))
        if data.hardware_to_operate:
            newSoftware.hardware_to_operate.set(extract_ids(data.hardware_to_operate))
        if data.software_gl_accounts:
            newSoftware.software_gl_accounts.set(extract_ids(data.software_gl_accounts))
        if data.software_divisions_using:
            newSoftware.software_divisions_using.set(extract_ids(data.software_divisions_using))

        newSoftware.save()

        return 201, SoftwareOut.from_orm(newSoftware)

    except ObjectDoesNotExist as e:
        return 400, ErrorSchema(
            message=f"Object not found: {str(e)}",
            code="OBJECT_NOT_FOUND"
        )
    except IntegrityError as e:
        return 400, ErrorSchema(
            message=f"Database integrity error: {str(e)}",
            code="INTEGRITY_ERROR"
        )
    except ValueError as e:
        return 400, ErrorSchema(
            message=f"Invalid data: {str(e)}",
            code="INVALID_DATA"
        )
    except Exception as e:
        return 500, ErrorSchema(
            message=f"An unexpected error occurred: {str(e)}",
            code="INTERNAL_SERVER_ERROR"
        )

@api_v1.put("software/{id}", response={200: SoftwareOut, 400: ErrorSchema, 500: ErrorSchema})
def update_software(request, id: int, data: SoftwareUpdate):
    try:
        software = get_object_or_404(Software, id=id)
        
        simple_fields = [
            'software_name', 'software_description', 'software_version',
            'software_years_of_use', 'software_is_hosted', 'software_is_tech_supported',
            'software_is_cloud_based', 'software_maintenance_support',
            'software_number_of_licenses', 'software_annual_amount',
        ]
        
        for field in simple_fields:
            if hasattr(data, field):
                setattr(software, field, getattr(data, field))
        
        if data.software_last_updated is not None:
            software.software_last_updated = data.software_last_updated
        if data.software_expiration_date is not None:
            software.software_expiration_date = data.software_expiration_date
        
        if data.software_operational_status == 'Active':
            software.software_operational_status = 'A'
        elif data.software_operational_status == 'Inactive':
            software.software_operational_status = 'I'
        
        def extract_ids(objects):
            return [obj.id for obj in objects] if objects else []

        m2m_fields = [
            ('software_department', Department),
            ('software_vendor', Vendor),
            ('software_department_contact_people', ContactPerson),
            ('software_divisions_using', Division),
            ('software_to_operate', SoftwareToOperate),
            ('hardware_to_operate', HardwareToOperate),
            ('software_gl_accounts', GlAccount)
        ]
        
        for field, model in m2m_fields:
            if hasattr(data, field):
                related_objects = getattr(data, field)
                related_ids = extract_ids(related_objects)
                getattr(software, field).set(model.objects.filter(id__in=related_ids))
        
        software.save()
        
        return 200, SoftwareOut.from_orm(software)

    except ObjectDoesNotExist as e:
        return 400, ErrorSchema(
            message=f"Object not found: {str(e)}",
            code="OBJECT_NOT_FOUND"
        )
    except IntegrityError as e:
        return 400, ErrorSchema(
            message=f"Database integrity error: {str(e)}",
            code="INTEGRITY_ERROR"
        )
    except ValueError as e:
        return 400, ErrorSchema(
            message=f"Invalid data: {str(e)}",
            code="INVALID_DATA"
        )
    except ValidationError as e:
        print("Validation error:", e.errors())
        return 400, ErrorSchema(
            message=f"Validation error: {str(e)}",
            code="VALIDATION_ERROR"
        )
    except Exception as e:
        return 500, ErrorSchema(
            message=f"An unexpected error occurred: {str(e)}",
            code="INTERNAL_SERVER_ERROR"
        )
        

@api_v1.delete("software/{id}", response={204: None, 404: ErrorSchema})
def delete_software(request, id: int):
    software = get_object_or_404(Software, id=id)
    software.delete()
    return 204, None

@api_v1.get("contact-people/", response=List[ContactPersonOut])
def get_all_contact_people(request):
    return ContactPerson.objects.all()

@api_v1.post("contact-people/", response={201: ContactPersonOut, 400: ErrorSchema})
def add_new_contact_person(request, data: ContactPersonIn):
    new_contact = ContactPerson.objects.create(
        contact_name=data.contact_name,
        contact_lastname=data.contact_lastname,
        contact_email=data.contact_email,
        contact_phone_number=data.contact_phone_number
    )

    return 201, ContactPersonOut(
        contact_name=new_contact.contact_name,
        contact_lastname=new_contact.contact_lastname,
        contact_email=new_contact.contact_email,
        contact_phone_number=new_contact.contact_phone_number
    )

@api_v1.get("comments/", response=List[CommentSchema])
def get_all_comments(request):
    return Comment.objects.all()

@api_v1.get("comments/{id}", response=CommentOut)
def get_comment_by_id(request, id: int):
    return get_object_or_404(Comment, id=id)

@api_v1.post("comments/", response={201: CommentOut, 404: ErrorSchema})
def add_new_comment(request, new_comment: CommentIn):
    user = get_object_or_404(User, id=new_comment.user_id)
    software = get_object_or_404(Software, id=new_comment.software_id)
    
    new_comment = Comment.objects.create(
        user=user,
        software=software,
        content=new_comment.content,
        satisfaction_rate=new_comment.satisfaction_rate,
        created_at=datetime.fromisoformat(new_comment.created_at)
    )
    
    print({
        "id": new_comment.id,
        "user_id": new_comment.user.id,
        "user_name": new_comment.user.username,
        "software_id": new_comment.software.id,
        "content": new_comment.content,
        "satisfaction_rate": new_comment.satisfaction_rate,
        "created_at": new_comment.created_at,
        "updated_at": new_comment.updated_at
    })
    
    return 201, CommentOut(
        id=new_comment.id,
        user_id=new_comment.user_id,
        user_name=new_comment.user.username,
        software_id=new_comment.software_id,
        content=new_comment.content,
        satisfaction_rate=new_comment.satisfaction_rate,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at
    )

@api_v1.put("comments/{id}", response={200: CommentSchema, 404: ErrorSchema})
def update_comment(request, id: int, data: CommentIn):
    comment = get_object_or_404(Comment, id=id)
    software = get_object_or_404(Software, id=data.software_id)
    
    comment.software = software
    comment.content = data.content
    comment.save()
    
    return 200, comment

@api_v1.patch("comments/{id}", response={200: CommentSchema, 404: ErrorSchema})
def partial_update_comment(request, id: int, data: CommentUpdate):
    comment = get_object_or_404(Comment, id=id)
    
    if data.content is not None:
        comment.content = data.content
        comment.save()
    
    return 200, comment

@api_v1.delete("comments/{id}", response={200: CommentOut, 404: ErrorSchema})
def delete_comment(request, id: int):
    comment = get_object_or_404(Comment, id=id)
    
    comment_data = CommentOut(
        user_name=comment.user.username,
        software_id=comment.software.id,
        content=comment.content,
        satisfaction_rate=comment.satisfaction_rate,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )
    
    comment.delete()
    return 200, comment_data

# Additional endpoints for other models (basic CRUD operations)
@api_v1.get("departments/", response=List[DepartmentSchema])
def get_all_departments(request):
    return Department.objects.all()

@api_v1.get("vendors/", response=List[VendorSchema])
def get_all_vendors(request):
    return Vendor.objects.all()

# Contact People Endoints
@api_v1.get("contact-people", response=List[ContactPersonSchema])
def get_all_contact_persons(request):
    return ContactPerson.objects.all()

@api_v1.post("contact-people", response={201: ContactPersonOut, 400: ErrorSchema})
def add_new_contact_person(request, data: ContactPersonIn):
    new_contact = ContactPerson.objects.create(
        contact_name=data.contact_name,
        contact_lastname=data.contact_lastname,
        contact_email=data.contact_email,
        contact_phone_number=data.contact_phone_number
    )

    return 201, ContactPersonOut(
        contact_name=new_contact.contact_name,
        contact_lastname=new_contact.contact_lastname,
        contact_email=new_contact.contact_email,
        contact_phone_number=new_contact.contact_phone_number,
        public_id=new_contact.public_id
    )
    
@api_v1.get("contact-people/{contact_id}/", response={200: ContactPersonOut, 404: ErrorSchema})
def get_contact_person(request, contact_id: int):
    contact = get_object_or_404(ContactPerson, id=contact_id)
    
    return 200, ContactPersonOut(
        contact_name=contact.contact_name,
        contact_lastname=contact.contact_lastname,
        contact_email=contact.contact_email,
        contact_phone_number=contact.contact_phone_number,
        public_id=contact.public_id
    )

@api_v1.get("divisions", response=List[DivisionSchema])
def get_all_divisions(request):
    return Division.objects.all()

@api_v1.get("gl-accounts/", response=List[GlAccountSchema])
def get_all_gl_accounts(request):
    return GlAccount.objects.all()

@api_v1.get("software-to-operate/", response=List[SoftwareToOperateSchema])
def get_all_software_to_operate(request):
    return SoftwareToOperate.objects.all()

@api_v1.get("hardware-to-operate/", response=List[HardwareToOperateSchema])
def get_all_hardware_to_operate(request):
    return HardwareToOperate.objects.all()

# Authentication Endpoints
@api_v1.post("/register", response={201: TokenSchema, 400: ErrorSchema, 500: ErrorSchema})
def register_user(request, user_data: UserCreateSchema):
    """User Registration Endpoint"""
    try:
        # Validate fields are not empty (whitespace-only is considered empty)
        empty_fields = {}
        
        if not user_data.username or not user_data.username.strip():
            empty_fields["username"] = "Username cannot be empty"
        
        if not user_data.email or not user_data.email.strip():
            empty_fields["email"] = "Email cannot be empty"
        
        if not user_data.password or not user_data.password.strip():
            empty_fields["password"] = "Password cannot be empty"
        
        if not user_data.confirm_password or not user_data.confirm_password.strip():
            empty_fields["confirm_password"] = "Confirm password cannot be empty"
        
        # First check for empty fields
        if empty_fields:
            return 400, ErrorSchema(
                message="Fields cannot be empty",
                code="EMPTY_FIELDS",
                details=empty_fields
            )

        # Validate password match
        if user_data.password != user_data.confirm_password:
            return 400, ErrorSchema(
                message="Passwords do not match",
                code="PASSWORD_MISMATCH",
                details={"confirm_password": "Passwords must match"}
            )

        try:
            # Validate email format
            validate_email(user_data.email)
        except ValidationError:
            return 400, ErrorSchema(
                message="Invalid email format",
                code="INVALID_EMAIL",
                details={"email": "Email address is not valid"}
            )

        # Check if username already exists
        if User.objects.filter(username=user_data.username).exists():
            return 400, ErrorSchema(
                message="Username already exists",
                code="USERNAME_TAKEN",
                details={"username": "This username is already in use"}
            )

        # Check if email already exists
        if User.objects.filter(email=user_data.email).exists():
            return 400, ErrorSchema(
                message="Email already exists",
                code="EMAIL_TAKEN",
                details={"email": "This email is already registered"}
            )

        try:
            # Create new user
            new_user = User.objects.create(
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                password=make_password(user_data.password)
            )

            # Generate access token
            access_token = AuthHandler.create_access_token(new_user, expiration_minutes=settings.JWT_EXPIRATION_TIME)
            
            return 201, {
                'access_token': access_token,
                'token_type': 'bearer',
                'user': {
                    'id': new_user.id,
                    'username': new_user.username,
                    'email': new_user.email,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name
                }
            }

        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            return 500, ErrorSchema(
                message="Failed to create user",
                code="USER_CREATION_ERROR",
                details={"error": str(e)}
            )

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return 500, ErrorSchema(
            message="Internal server error",
            code="INTERNAL_ERROR",
            details={"error": str(e)}
        )
    
@api_v1.post("/login", response={200: TokenSchema, 400: ErrorSchema, 401: ErrorSchema, 500: ErrorSchema})
def login_view(request, login_data: LoginSchema):
    """
    Login Endpoint
    Allows login with either username or email
    """
    try:
        # Validate input data
        if not login_data.login_identifier or not login_data.password:
            return 400, ErrorSchema(
                message="Missing required fields",
                code="MISSING_FIELDS",
                details={
                    "login_identifier": "Required" if not login_data.login_identifier else None,
                    "password": "Required" if not login_data.password else None
                }
            )

        # Try to find user
        user = User.objects.filter(
            Q(username=login_data.login_identifier) | 
            Q(email=login_data.login_identifier)
        ).first()

        # User not found
        if not user:
            return 401, ErrorSchema(
                message="No user found with this username or email",
                code="USERNAME_OR_EMAIL_NOT_FOUND",
                details={"login_identifier": "No user found with this username or email"}
            )

        # Check password
        if not user.check_password(login_data.password):
            return 401, ErrorSchema(
                message="Incorrect password",
                code="INCORRECT_PASSWORD",
                details={"password": "Incorrect password"}
            )

        try:
            access_token = AuthHandler.create_access_token(user, expiration_minutes=settings.JWT_EXPIRATION_TIME)
            
            return 200, {
                'access_token': access_token,
                'token_type': 'bearer',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }

        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            return 500, ErrorSchema(
                message="Failed to generate authentication token",
                code="TOKEN_GENERATION_ERROR",
                details={"error": str(e)}
            )

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return 500, ErrorSchema(
            message="Internal server error",
            code="INTERNAL_ERROR",
            details={"error": str(e)}
        )

@api_v1.post("/logout", response={200: dict, 400: ErrorSchema, 500: ErrorSchema})
def logout_view(request):
    """Logout Endpoint"""
    
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')

    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]

        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            try:
                BlacklistedToken.objects.create(token=token)
                logger.info(f"Token successfully blacklisted: {token[:10]}...")
            except IntegrityError:
                logger.info(f"Token already blacklisted: {token[:10]}...")
            except Exception as e:
                logger.error(f"Database error while blacklisting token: {str(e)}")
                return 500, ErrorSchema(
                    message="Failed to blacklist token",
                    code="DB_ERROR",
                    details={"error": str(e)}
                )
        except jwt.ExpiredSignatureError:
            logger.info("Token has expired, proceeding with logout")
        except jwt.InvalidTokenError:
            logger.info("Invalid token, proceeding with logout")

    # Return success message regardless of token validity
    return 200, {"message": "Successfully logged out"}

@api_v1.get("/me", auth=BearerAuth(), response=UserResponseSchema)
def get_current_user(request):
    """Get Current Authenticated User"""
    user = request.auth
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
