export default abstract class HTTPClient {
  public withCredentials: boolean = false;

  constructor(private baseURL: string) {}

  public fetch(
    url: RequestInfo | URL,
    options?: RequestInit & { multipart?: boolean },
  ): Promise<Response> {
    if (this.withCredentials) {
      const { newUrl, newOptions } = this.getCredentials(url, options);
      url = newUrl;
      options = newOptions;
    }
    const strUrl = url.toString();
    const joinedURL = `${
      this.baseURL.endsWith("/")
        ? this.baseURL.substring(0, this.baseURL.length - 1)
        : this.baseURL
    }/${strUrl.startsWith("/") ? strUrl.substring(1, strUrl.length) : strUrl}`;

    const headers = { ...options?.headers } as Record<string, string>;
    if (!options?.multipart) {
      headers["Content-Type"] ??= "application/json";
    } else {
      delete headers["Content-Type"];
    }

    return fetch(joinedURL, { cache: "no-store", ...options, headers });
  }

  protected abstract getCredentials(
    url: RequestInfo | URL,
    options?: RequestInit & { multipart?: boolean },
  ): { newUrl: RequestInfo | URL; newOptions: RequestInit };
}
