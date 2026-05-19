from pydantic import BaseModel

class CourseDataDto(BaseModel):
    courseId: str
    courseActv: str
    courseLang: str