import { useEffect, useState } from "react";
import { api } from "../api.js";
import Notice from "./Notice.jsx";

const PAGE_SIZE = 5;

// Bai tap 3: lich su dang ky/huy cua sinh vien, chi dataset demo, phan trang
// tai server (skip/limit). Lay du 1 dong de biet con trang sau hay khong.
export default function EventHistory({ studentId, refresh }) {
  const [page, setPage] = useState(0);
  const [rows, setRows] = useState([]);
  const [hasNext, setHasNext] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => { setPage(0); }, [studentId]);

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams({
      student_id: studentId, dataset: "demo",
      skip: String(page * PAGE_SIZE), limit: String(PAGE_SIZE + 1),
    });
    setLoading(true);
    setError("");
    api(`/enrollment-events?${params}`, { signal: controller.signal })
      .then((data) => {
        if (controller.signal.aborted) return;
        setRows(data.slice(0, PAGE_SIZE));
        setHasNext(data.length > PAGE_SIZE);
      })
      .catch((err) => {
        if (controller.signal.aborted) return;
        setError(err.message);
        setRows([]);
        setHasNext(false);
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [studentId, page, refresh]);

  return (
    <section className="panel">
      <h2>4. Lịch sử đăng ký (demo)</h2>
      <Notice kind="error">{error}</Notice>
      {loading ? <p className="muted">Đang tải lịch sử...</p>
        : !error && rows.length === 0 ? <p>Chưa có sự kiện nào.</p>
        : (
          <div className="table-scroll">
            <table aria-label="Lịch sử đăng ký">
              <thead>
                <tr><th>Thời điểm</th><th>Lớp</th><th>Sự kiện</th></tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.id}>
                    <td>{new Date(row.occurred_at).toLocaleString("vi-VN")}</td>
                    <td>{row.class_section_id}</td>
                    <td>{row.event_type === "CREATED" ? "Đăng ký" : "Hủy"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      <div className="pager">
        <button type="button" className="secondary" disabled={loading || page === 0}
          onClick={() => setPage((p) => p - 1)}>Trang trước</button>
        <span className="muted">Trang {page + 1}</span>
        <button type="button" className="secondary" disabled={loading || !hasNext}
          onClick={() => setPage((p) => p + 1)}>Trang sau</button>
      </div>
    </section>
  );
}
