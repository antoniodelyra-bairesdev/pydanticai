import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("user_token");
  const { pathname } = request.nextUrl;

  if (!pathname.startsWith("/_") && pathname !== "/favicon.ico") {
    const loginPath = "/login";
    const homePath = "/";

    if (!token?.value && !pathname.startsWith(loginPath)) {
      return NextResponse.redirect(new URL(loginPath, request.url));
    } else if (token?.value && pathname.startsWith(loginPath)) {
      return NextResponse.redirect(new URL(homePath, request.url));
    }
  }

  return NextResponse.next();
}
