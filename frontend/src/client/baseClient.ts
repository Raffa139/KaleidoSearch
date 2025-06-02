export class HttpError extends Error {
  code: number;

  constructor(code: number, message: string = "") {
    super(message);
    this.code = code;
  }
}

export class BaseClient {
  host: string;
  port: number;
  rootPath: string;
  Http: HttpMethods;

  constructor(host: string, port: number, rootPath: string = "") {
    this.host = host;
    this.port = port;
    this.rootPath = rootPath;
    this.Http = new HttpMethods(this.baseUrl());
  }

  baseUrl(): string {
    return `http://${this.host}:${this.port}${this.rootPath}/${this.resource()}`;
  }

  resource(): string {
    throw new Error("Abstract method 'resource' not implemented");
  }
}

class HttpMethods {
  baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  async get<T>(...paths: string[]): Promise<T> {
    const response = await this.fetch_(this.baseUrl, { method: "GET" }, ...paths);
    return response.json();
  }

  async post<T>(body?: object, ...paths: string[]): Promise<T> {
    const response = await this.fetch_(
      this.baseUrl,
      { method: "POST", body: body ? JSON.stringify(body) : undefined },
      ...paths
    );

    return response.json();
  }

  async delete_(...paths: string[]): Promise<void> {
    const response = await this.fetch_(this.baseUrl, { method: "DELETE" }, ...paths);
    return response.json();
  }

  private async fetch_(baseUrl: string, init?: RequestInit, ...paths: string[]): Promise<Response> {
    const response = await fetch(`${baseUrl}/${paths.join("/")}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        ...init?.headers
      }
    });

    if (response.status === 498) {
      console.error("Token expired, redirect to login");
      window.location.replace("/");
    }

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new HttpError(response.status);
    }

    return response;
  }
}
