import { cookies } from "next/headers";
import HTTPClient from "../HTTPClient";

export default class IVServerHTTPClient extends HTTPClient {
  constructor(options?: { withCredentials: boolean }) {
    super(process.env.IV_API_URL ?? "");
    this.withCredentials = options?.withCredentials ?? false;
  }
  public fetch(
    url: RequestInfo | URL,
    options?: RequestInit | undefined,
  ): Promise<Response> {
    "use server";
    const response = super.fetch(url, options);
    const now = new Date().toJSON().replace("T", " ").replace("Z", "");
    response.then(
      (r) => {
        console.log(`[${now}] (${r.status} ${r.statusText}) ${url}`);
        return r;
      },
      (r) => {
        console.error(`[${now}] Erro! ${url}`, r);
      },
    );
    return response;
  }
  protected getCredentials(
    url: RequestInfo | URL,
    options?: RequestInit | undefined,
  ): { newUrl: RequestInfo | URL; newOptions: RequestInit } {
    const headers = { ...options?.headers } as Record<string, string>;
    const token = cookies().get("user_token");
    if (token) {
      headers["X-User-Token"] = token.value;
    }
    return { newUrl: url, newOptions: { ...options, headers } };
  }
}
