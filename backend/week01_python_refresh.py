students = [
    {"id": "22000001", "name": "Nguyen Minh Anh", "major": "KHDL"},
    {"id": "22000002", "name": "Tran Duc Long", "major": "KHDL"},
]

courses = [
    {
        "code": "INT2204",
        "name": "Co so du lieu Web va he thong thong tin",
        "capacity": 3,
        "enrolled": 2,
    },
    {
        "code": "INT2205",
        "name": "Khai pha du lieu",
        "capacity": 2,
        "enrolled": 2,
    },
]

enrollments = [{"student_id": "22000001", "course_code": "INT2204"}]


def find_course(course_code):
    for course in courses:
        if course["code"] == course_code:
            return course
    return None


def find_student(student_id):
    for student in students:
        if student["id"] == student_id:
            return student
    return None


def search_courses(keyword):
    normalized = keyword.strip().lower()
    results = []
    for course in courses:
        code = course["code"].lower()
        name = course["name"].lower()
        if normalized in code or normalized in name:
            results.append(course)
    return results


def can_enroll(student_id, course_code):
    if find_student(student_id) is None:
        return False, "Sinh vien khong ton tai"

    course = find_course(course_code)
    if course is None:
        return False, "Hoc phan khong ton tai"

    if course["enrolled"] >= course["capacity"]:
        return False, "Lop da du so luong"

    duplicated = any(
        item["student_id"] == student_id and item["course_code"] == course_code
        for item in enrollments
    )
    if duplicated:
        return False, "Sinh vien da dang ky hoc phan nay"

    return True, "Co the dang ky"


def enroll_student(student_id, course_code):
    valid, message = can_enroll(student_id, course_code)
    if not valid:
        return False, message

    enrollments.append({"student_id": student_id, "course_code": course_code})
    course = find_course(course_code)
    if course is not None:
        course["enrolled"] += 1
    return True, "Dang ky hoc phan thanh cong"


print("5 tinh huong chay thu")

# Tình huống 1: Đăng ký trùng
print("1.", enroll_student("22000001", "INT2204"))

# Tình huống 2: Lớp đầy
print("2.", enroll_student("22000001", "INT2205"))

# Tình huống 3: Mã học phần không tồn tại
print("3.", enroll_student("22000001", "INT9999"))

# Tình huống 4: Mã sinh viên không tồn tại
print("4.", enroll_student("99999999", "INT2204"))

# Tình huống 5: Đăng ký thành công
print("5.", enroll_student("22000002", "INT2204"))
