import uuid
from ninja import Schema
from typing import List, Optional
from datetime import date, datetime

class ErrorSchema(Schema):
    message: str
    code: str
    details: Optional[dict] = None

class DepartmentSchema(Schema):
    id: int
    name: str

class VendorSchema(Schema):
    id: int
    name: str

class ContactPersonSchema(Schema):
    id: int
    contact_name: str
    contact_lastname: str
    contact_email: str
    contact_phone_number: Optional[int]
    public_id: uuid.UUID

class ContactPersonIn(Schema):
    contact_name: str
    contact_lastname: str
    contact_email: str = None
    contact_phone_number: Optional[int] = None

class ContactPersonOut(Schema):
    contact_name: str
    contact_lastname: str
    contact_email: str
    contact_phone_number: Optional[int]
    public_id: uuid.UUID

class DivisionSchema(Schema):
    id: int
    name: str

class GlAccountSchema(Schema):
    id: int
    name: str

class SoftwareToOperateSchema(Schema):
    id: int
    name: str

class HardwareToOperateSchema(Schema):
    id: int
    name: str

class CommentSchema(Schema):
    id: int
    user_id: int
    user_name: str
    software_id: int
    content: str
    satisfaction_rate: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @staticmethod
    def resolve_created_at(obj):
        return obj.created_at.isoformat() if obj.created_at else None

    @staticmethod
    def resolve_updated_at(obj):
        return obj.updated_at.isoformat() if obj.updated_at else None
    
    @staticmethod
    def resolve_user_name(obj):
        return obj.user.username

class SoftwareSchema(Schema):
    id: int
    software_name: str
    software_description: str
    software_department: List[DepartmentSchema]
    software_version: Optional[str]
    software_years_of_use: Optional[int]
    software_last_updated: Optional[str]
    software_expiration_date: Optional[str]
    software_is_hosted: str
    software_is_tech_supported: str
    software_is_cloud_based: Optional[str]
    software_maintenance_support: str
    software_vendor: List[VendorSchema]
    software_department_contact_people: List[ContactPersonSchema]
    software_divisions_using: List[DivisionSchema]
    software_number_of_licenses: int
    software_to_operate: List[SoftwareToOperateSchema]
    hardware_to_operate: List[HardwareToOperateSchema]
    software_annual_amount: Optional[float]
    software_gl_accounts: List[GlAccountSchema]
    software_operational_status: str
    
    @staticmethod
    def resolve_software_last_updated(obj):
        return obj.software_last_updated.isoformat() if obj.software_last_updated else None

    @staticmethod
    def resolve_software_expiration_date(obj):
        return obj.software_expiration_date.isoformat() if obj.software_expiration_date else None

class SoftwareWithCommentsSchema(SoftwareSchema):
    software_comments: List[CommentSchema]

# Input Schemas
class SoftwareIn(Schema):
    software_name: str
    software_description: str
    software_department: List[DepartmentSchema]
    software_version: Optional[str]
    software_years_of_use: Optional[int]
    software_last_updated: Optional[date]
    software_expiration_date: Optional[date]
    software_is_hosted: str
    software_is_tech_supported: str
    software_is_cloud_based: Optional[str]
    software_maintenance_support: str
    software_vendor: List[VendorSchema]
    software_department_contact_people: List[ContactPersonSchema]
    software_divisions_using: List[DivisionSchema]
    software_number_of_licenses: int
    software_to_operate: List[SoftwareToOperateSchema]
    hardware_to_operate: List[HardwareToOperateSchema]
    software_annual_amount: Optional[float]
    software_gl_accounts: List[GlAccountSchema]
    software_operational_status: str

class SoftwareOut(Schema):
    software_name: str
    software_description: str
    software_department: List[DepartmentSchema]
    software_version: Optional[str]
    software_years_of_use: Optional[int]
    software_last_updated: Optional[datetime]
    software_expiration_date: Optional[date]
    software_is_hosted: str
    software_is_tech_supported: str
    software_is_cloud_based: Optional[str]
    software_maintenance_support: str
    software_vendor: List[VendorSchema]
    software_department_contact_people: List[ContactPersonSchema]
    software_divisions_using: List[DivisionSchema]
    software_number_of_licenses: int
    software_to_operate: List[SoftwareToOperateSchema]
    hardware_to_operate: List[HardwareToOperateSchema]
    software_annual_amount: Optional[float]
    software_gl_accounts: List[GlAccountSchema]
    software_operational_status: str

class SoftwareUpdate(Schema):
    software_name: str
    software_description: str
    software_department: List[DepartmentSchema]
    software_version: Optional[str]
    software_years_of_use: Optional[int]
    software_last_updated: Optional[datetime]
    software_expiration_date: Optional[date]
    software_is_hosted: str
    software_is_tech_supported: str
    software_is_cloud_based: Optional[str]
    software_maintenance_support: str
    software_vendor: List[VendorSchema]
    software_department_contact_people: List[ContactPersonSchema]
    software_divisions_using: List[DivisionSchema]
    software_number_of_licenses: int
    software_to_operate: List[SoftwareToOperateSchema]
    hardware_to_operate: List[HardwareToOperateSchema]
    software_annual_amount: Optional[float]
    software_gl_accounts: List[GlAccountSchema]
    software_operational_status: str
    
    @classmethod
    def validate_software_last_updated(cls, value):
        if value is not None:
            return datetime.fromisoformat(value)
        return value

    @classmethod
    def validate_software_expiration_date(cls, value):
        if value is not None:
            return date.fromisoformat(value)
        return value

class CommentIn(Schema):
    content: str
    created_at: str
    satisfaction_rate: int
    software_id: int
    user_id: int
    user_name: str

class CommentOut(Schema):
    user_name: str
    software_id: int
    content: str
    satisfaction_rate: int
    created_at: datetime
    updated_at: Optional[datetime]

class CommentUpdate(Schema):
    content: Optional[str]

# Authentication Schemas
class UserCreateSchema(Schema):
    username: str
    first_name: str
    last_name:str
    email: str
    password: str
    confirm_password: str
    
class LoginSchema(Schema):
    login_identifier: str  # Can be username or email
    password: str

class UserResponseSchema(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str

class TokenSchema(Schema):
    access_token: str
    token_type: str = 'bearer'
    user: UserResponseSchema
    
class AnalyticsSchema(Schema):
    totalSpending: float
    averageSatisfaction: float
    activeSoftware: int
    totalSoftware: int
    expiringSoon: int
    mostExpensive: dict
    cheapest: dict
    averageCost: float
    highestRated: dict
    lowestRated: dict
    vendors: list
    activeLicenses: int
    inactiveLicenses: int