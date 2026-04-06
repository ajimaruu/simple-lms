from django.core.management.base import BaseCommand
from django.db import connection, reset_queries
from courses.models import Course

class Command(BaseCommand):
    help = 'Demonstrasi N+1 Problem vs Optimized Queries'

    def handle(self, *args, **kwargs):
        from django.conf import settings
        settings.DEBUG = True # Wajib True agar query terekam
        
        self.stdout.write(self.style.WARNING('\n--- Simulasi N+1 Problem ---'))
        reset_queries()
        
        # Query Buruk: Tanpa select_related (akan memicu query berulang di dalam loop)
        bad_courses = Course.objects.all()
        for course in bad_courses:
            print(f"Course: {course.title} | Instructor: {course.instructor.username}")
            
        bad_query_count = len(connection.queries)
        self.stdout.write(self.style.ERROR(f'Jumlah Query (N+1): {bad_query_count} queries\n'))

        self.stdout.write(self.style.SUCCESS('--- Simulasi Optimized Query ---'))
        reset_queries()
        
        # Query Baik: Pakai custom manager yang sudah ada select_related-nya
        good_courses = Course.objects.for_listing()
        for course in good_courses:
            print(f"Course: {course.title} | Instructor: {course.instructor.username}")
            
        good_query_count = len(connection.queries)
        self.stdout.write(self.style.SUCCESS(f'Jumlah Query (Optimized): {good_query_count} queries\n'))