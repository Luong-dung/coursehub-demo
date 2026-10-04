-- =============================================================================
-- COURSEHUB AI QUERY COMPARISON
-- File: 07_ai_query.sql
-- Mục đích: Đối chiếu truy vấn đếm sai (thường do AI hoặc người mới học viết)
--           với truy vấn đã sửa đúng khi thống kê số lượng bản ghi với LEFT JOIN.
-- =============================================================================

-- =============================================================================
-- BÀI TOÁN:
-- Yêu cầu: Thống kê số lượng sinh viên đã đăng ký cho TẤT CẢ các lớp học phần,
--          kể cả các lớp chưa có sinh viên nào đăng ký (ví dụ: lớp INT2204_02).
-- =============================================================================


-- -----------------------------------------------------------------------------
-- PHẦN 1: TRUY VẤN DO AI SINH RA (BỊ LỖI LOGIC ĐẾM SAI)
-- Vấn đề: Sử dụng COUNT(*) kết hợp với LEFT JOIN
-- -----------------------------------------------------------------------------
SELECT 
    cl.class_id,
    cl.course_code,
    cl.capacity,
    COUNT(*) AS enrolled_students_wrong
FROM classes cl
LEFT JOIN enrollments e ON cl.class_id = e.class_id
GROUP BY cl.class_id, cl.course_code, cl.capacity
ORDER BY cl.class_id;

/*
GIẢI THÍCH NGUYÊN NHÂN SAI:
- Lớp 'INT2204_02' là lớp mới mở, chưa có sinh viên nào đăng ký trong bảng enrollments.
- Khi thực hiện LEFT JOIN, hệ thống vẫn giữ lại dòng của bảng classes và gán toàn bộ 
  các cột của bảng enrollments (như e.enrollment_id, e.student_id) mang giá trị NULL.
- Tuy nhiên, hàm COUNT(*) có cơ chế đếm TỔNG SỐ DÒNG xuất hiện trong nhóm, không quan tâm 
  dòng đó có chứa giá trị NULL hay không.
- Vì tồn tại 1 dòng được sinh ra từ LEFT JOIN (với các cột enrollments mang giá trị NULL),
  COUNT(*) đếm dòng này và trả về kết quả là 1.
=> KẾT QUẢ SAI LỆCH: Lớp chưa có ai đăng ký lại bị báo là có 1 sinh viên!
*/


-- -----------------------------------------------------------------------------
-- PHẦN 2: TRUY VẤN CHUẨN XÁC ĐÃ ĐƯỢC SỬA LỖI
-- Cách sửa: Thay COUNT(*) bằng COUNT(e.student_id) hoặc COUNT(e.enrollment_id)
-- -----------------------------------------------------------------------------
SELECT 
    cl.class_id,
    cl.course_code,
    cl.capacity,
    COUNT(e.student_id) AS enrolled_students_correct,
    (cl.capacity - COUNT(e.student_id)) AS remaining_slots
FROM classes cl
LEFT JOIN enrollments e ON cl.class_id = e.class_id
GROUP BY cl.class_id, cl.course_code, cl.capacity
ORDER BY cl.class_id;

/*
GIẢI THÍCH TẠI SAO ĐÚNG:
- Hàm COUNT(tên_cột) chỉ đếm các dòng có giá trị KHÁC NULL (ignoring NULL values).
- Đối với lớp 'INT2204_02', cột e.student_id mang giá trị NULL, do đó COUNT(e.student_id) 
  bỏ qua giá trị này và trả về chính xác là 0.
=> KẾT QUẢ CHÍNH XÁC: Phản ánh đúng thực tế lớp học phần chưa có người đăng ký.
*/


-- -----------------------------------------------------------------------------
-- PHẦN 3: TRUY VẤN ĐỐI CHIẾU TRỰC TIẾP TRÊN CÙNG MỘT BẢNG KẾT QUẢ
-- Chạy truy vấn này để quan sát trực tiếp sự khác biệt giữa hai cách đếm:
-- -----------------------------------------------------------------------------
SELECT 
    cl.class_id,
    cl.course_code,
    cl.capacity,
    COUNT(*) AS ai_count_wrong,
    COUNT(e.student_id) AS correct_count,
    CASE 
        WHEN COUNT(*) <> COUNT(e.student_id) THEN 'SAI LỆCH KHI LỚP TRỐNG'
        ELSE 'KHỚP NHAU'
    END AS status_check
FROM classes cl
LEFT JOIN enrollments e ON cl.class_id = e.class_id
GROUP BY cl.class_id, cl.course_code, cl.capacity
ORDER BY cl.class_id;
