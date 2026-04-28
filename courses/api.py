from ninja import NinjaAPI
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import User, Course, Enrollment, Lesson, Progress
from .schemas import (
    RegisterSchemaIn, UserSchemaOut, LoginSchemaIn, TokenSchemaOut, UpdateProfileSchemaIn, 
    CourseSchemaOut, CourseCreateSchemaIn, CourseUpdateSchemaIn,
    EnrollmentSchemaOut, EnrollmentCreateSchemaIn
)
from .auth import create_access_token 
from .auth import JWTAuth
from .permissions import is_instructor, is_admin, is_student
from django.shortcuts import get_object_or_404
from typing import List

api = NinjaAPI(title="Simple LMS API", version="1.0.0", description="API untuk Sistem Manajemen Pembelajaran")

@api.post("/auth/register", response={201: UserSchemaOut}, tags=["Authentication"])
def register(request, payload: RegisterSchemaIn):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username already exists")
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=payload.role
    )
    user.set_password(payload.password) 
    user.save()
    
    return 201, user

@api.post("/auth/login", response=TokenSchemaOut, tags=["Authentication"])
def login(request, payload: LoginSchemaIn):
    user = authenticate(username=payload.username, password=payload.password)
    
    if user is None:
        raise HttpError(401, "Invalid username or password")

    access_token = create_access_token(user.id)
    
    return {"access_token": access_token}


@api.get("/auth/me", response=UserSchemaOut, auth=JWTAuth(), tags=["Authentication"])
def get_current_user(request):
    """
    Mengambil data profil user yang sedang login.
    Endpoint ini dilindungi oleh JWTAuth.
    """
    return request.auth

@api.put("/auth/me", response=UserSchemaOut, auth=JWTAuth(), tags=["Authentication"])
def update_profile(request, payload: UpdateProfileSchemaIn):
    """
    Mengubah data profil user yang sedang login.
    """
    user = request.auth
    
    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.email is not None:
        user.email = payload.email
        
    user.save()
    return user

@api.get("/courses", response=List[CourseSchemaOut], tags=["Courses (Public)"])
def list_courses(request):
    """Melihat daftar semua course (Bisa diakses siapa saja)"""
    return Course.objects.all()

@api.get("/courses/{course_id}", response=CourseSchemaOut, tags=["Courses (Public)"])
def get_course(request, course_id: int):
    """Melihat detail satu course"""
    return get_object_or_404(Course, id=course_id)

@api.post("/courses", response={201: CourseSchemaOut}, auth=JWTAuth(), tags=["Courses (Protected)"])
@is_instructor
def create_course(request, payload: CourseCreateSchemaIn):
    """Membuat course baru (Hanya untuk Instructor)"""
    course = Course.objects.create(
        title=payload.title,
        description=payload.description,
        category_id=payload.category_id,
        instructor=request.auth # Otomatis set instructor dari user yang login
    )
    return 201, course

@api.patch("/courses/{course_id}", response=CourseSchemaOut, auth=JWTAuth(), tags=["Courses (Protected)"])
@is_instructor
def update_course(request, course_id: int, payload: CourseUpdateSchemaIn):
    """Update course (Hanya untuk Owner Course)"""
    course = get_object_or_404(Course, id=course_id)
    
    # Ownership Validation (Hanya pembuat course atau admin yang bisa edit)
    if course.instructor != request.auth and request.auth.role != 'admin':
        raise HttpError(403, "Forbidden: You are not the owner of this course")

    if payload.title is not None:
        course.title = payload.title
    if payload.description is not None:
        course.description = payload.description
    
    course.save()
    return course

@api.delete("/courses/{course_id}", auth=JWTAuth(), tags=["Courses (Protected)"])
@is_admin
def delete_course(request, course_id: int):
    """Hapus course (Hanya untuk Admin)"""
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return {"success": True, "message": "Course berhasil dihapus"}

@api.post("/enrollments", response={201: EnrollmentSchemaOut}, auth=JWTAuth(), tags=["Enrollments"])
@is_student
def enroll_course(request, payload: EnrollmentCreateSchemaIn):
    """Enroll / mendaftar ke sebuah course (Hanya untuk Student)"""
    course = get_object_or_404(Course, id=payload.course_id)
    
    if Enrollment.objects.filter(student=request.auth, course=course).exists():
        raise HttpError(400, "You are already enrolled in this course")
        
    enrollment = Enrollment.objects.create(student=request.auth, course=course)
    return 201, enrollment

@api.get("/enrollments/my-courses", response=List[EnrollmentSchemaOut], auth=JWTAuth(), tags=["Enrollments"])
@is_student
def my_enrolled_courses(request):
    """Melihat daftar course yang sedang diikuti (Hanya untuk Student)"""
    return Enrollment.objects.filter(student=request.auth)

@api.post("/enrollments/{lesson_id}/progress", auth=JWTAuth(), tags=["Enrollments"])
@is_student
def mark_lesson_complete(request, lesson_id: int):
    """Menandai lesson selesai (Hanya untuk Student)"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if not Enrollment.objects.filter(student=request.auth, course=lesson.course).exists():
        raise HttpError(403, "Forbidden: You must be enrolled in the course")
        
    progress, created = Progress.objects.get_or_create(
        student=request.auth, lesson=lesson, defaults={'is_completed': True}
    )
    if not created:
        progress.is_completed = True
        progress.save()
        
    return {"success": True, "message": "Lesson marked as complete"}