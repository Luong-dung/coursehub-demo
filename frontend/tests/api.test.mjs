// Kiem thu api.js voi fetch gia lap (khong goi Backend/PostgreSQL that).
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { api } from "../src/api.js";

const realFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = realFetch; });

function mock(status, raw, capture = {}) {
  globalThis.fetch = async (url, init) => {
    capture.url = url;
    capture.init = init;
    return { status, ok: status >= 200 && status < 300, text: async () => raw };
  };
  return capture;
}

test("GET 200 tra JSON va dung BASE_URL mac dinh", async () => {
  const cap = mock(200, '[{"class_id":"WEB-01"}]');
  const data = await api("/sections");
  assert.deepEqual(data, [{ class_id: "WEB-01" }]);
  assert.equal(cap.url, "http://127.0.0.1:8000/sections");
  assert.equal(cap.init.method, "GET");
  assert.deepEqual(cap.init.headers, {});
});

test("POST gui body JSON va Content-Type", async () => {
  const cap = mock(201, '{"student_id":"22000004"}');
  const body = { student_id: "22000004", class_section_id: "WEB-01" };
  await api("/enrollments", { method: "POST", body });
  assert.equal(cap.init.body, JSON.stringify(body));
  assert.equal(cap.init.headers["Content-Type"], "application/json");
});

test("DELETE 204 tra null, khong doc JSON", async () => {
  mock(204, "");
  assert.equal(await api("/enrollments/22000004/WEB-01", { method: "DELETE" }), null);
});

test("404 voi detail chuoi nem loi co status", async () => {
  mock(404, '{"detail":"Khong tim thay sinh vien"}');
  await assert.rejects(api("/students/99999999/enrollments"),
    (e) => e.status === 404 && e.message === "HTTP 404: Khong tim thay sinh vien");
});

test("409 xung dot giu nguyen detail", async () => {
  mock(409, '{"detail":"Lop da het cho"}');
  await assert.rejects(api("/enrollments", { method: "POST", body: {} }),
    (e) => e.status === 409 && e.message.includes("Lop da het cho"));
});

test("422 detail dang danh sach duoc ghep thong bao", async () => {
  mock(422, '{"detail":[{"msg":"field required"},{"msg":"bad type"}]}');
  await assert.rejects(api("/enrollments", { method: "POST", body: {} }),
    (e) => e.message === "HTTP 422: field required; bad type");
});

test("phan hoi khong phai JSON bao loi ro rang", async () => {
  mock(500, "<html>oops</html>");
  await assert.rejects(api("/sections"), /HTTP 500: phản hồi không phải JSON/);
});

test("mat ket noi bao loi, AbortError duoc nem lai nguyen", async () => {
  globalThis.fetch = async () => { throw new TypeError("Failed to fetch"); };
  await assert.rejects(api("/sections"), /Không nhận được phản hồi API/);
  globalThis.fetch = async () => {
    const e = new Error("aborted"); e.name = "AbortError"; throw e;
  };
  await assert.rejects(api("/sections"), (e) => e.name === "AbortError");
});
