export class ClientBase {
  host: string;
  port: number;
  rootPath: string;

  constructor(host: string, port: number, rootPath: string = "") {
    this.host = host;
    this.port = port;
    this.rootPath = rootPath;
  }

  baseUrl(): string {
    return `http://${this.host}:${this.port}${this.rootPath}/${this.resource()}`
  }

  resource(): string {
    throw new Error("Abstract method 'resource' not implemented")
  }
}

export const get = async <T>(url: string): Promise<T> => {
  const response = await fetch_(url);
  return response.json();
};

export const post = async <T>(url: string, body?: object): Promise<T> => {
  const response = await fetch_(url, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined
  });

  return response.json();
};

export const delete_ = async (url: string): Promise<void> => {
  const response = await fetch_(url, { method: "DELETE" });
  return response.json();
};

const fetch_ = async (url: string, init?: RequestInit): Promise<Response> => {
  const response = await fetch(url, {
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
    throw new Error();
  }

  return response;
}
