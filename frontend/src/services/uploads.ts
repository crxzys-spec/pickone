import http from "../apis/http";

export async function uploadExpertCredential(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await http.post("/uploads/expert-credential", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data as { url: string; filename: string; path: string };
}
