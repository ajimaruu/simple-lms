from ninja import Schema, ModelSchema
from pydantic import EmailStr
from .models import User, Course, Enrollment

class UserSchemaOut(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']

class RegisterSchemaIn(Schema):
    username: str
    email: EmailStr
    password: str
    first_name: str = ""
    last_name: str = ""
    role: str = "student" 

class LoginSchemaIn(Schema):
    username: str
    password: str

class TokenSchemaOut(Schema):
    access_token: str

class UpdateProfileSchemaIn(Schema):
    first_name: str = None
    last_name: str = None
    email: EmailStr = None

class CourseSchemaOut(ModelSchema):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'category', 'instructor', 'created_at']

class CourseCreateSchemaIn(Schema):
    title: str
    description: str = ""
    category_id: int = None

class CourseUpdateSchemaIn(Schema):
    title: str = None
    description: str = None

class EnrollmentSchemaOut(ModelSchema):
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'enrolled_at', 'is_completed']

class EnrollmentCreateSchemaIn(Schema):
    course_id: int