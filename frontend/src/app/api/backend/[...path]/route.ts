import { NextRequest } from "next/server";

const BACKEND_API_URL = (
  process.env.QCSTS_API_URL ?? "http://127.0.0.1:8000/api/v1"
).replace(/\/$/, "");

const FORWARDED_HEADERS = [
  "accept",
  "accept-encoding",
  "authorization",
  "content-type",
  "cookie",
  "x-csrftoken",
  "x-signature-token",
  "x-organization-id",
  "x-site-id",
];

async function handler(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;

  // QCSTS Django endpoints use trailing-slash URLs. Next.js route params
  // normalize the incoming proxy path, so append the slash explicitly.
  const target = `${BACKEND_API_URL}/${path.join("/")}/${request.nextUrl.search}`;

  const headers = new Headers();
  for (const name of FORWARDED_HEADERS) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  const body =
    request.method === "GET" || request.method === "HEAD"
      ? undefined
      : await request.arrayBuffer();

  const response = await fetch(target, {
    method: request.method,
    headers,
    body,
    redirect: "manual",
    cache: "no-store",
  });

  const responseHeaders = new Headers();
  const contentType = response.headers.get("content-type");
  const cacheControl = response.headers.get("cache-control");
  const setCookie = response.headers.get("set-cookie");

  if (contentType) responseHeaders.set("content-type", contentType);
  if (cacheControl) responseHeaders.set("cache-control", cacheControl);
  if (setCookie) responseHeaders.set("set-cookie", setCookie);

  if (response.status >= 300 && response.status < 400) {
    const location = response.headers.get("location");
    if (location) responseHeaders.set("location", location);
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
export const HEAD = handler;
