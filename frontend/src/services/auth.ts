import http from "../apis/http";

export interface TokenResponse {
  access_token: string;
  token_type: string;
  scopes: string[];
}

export async function login(username: string, password: string) {
  const body = new URLSearchParams();
  body.append("username", username);
  body.append("password", password);

  const { data } = await http.post<TokenResponse>("/auth/login", body, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  return data;
}
