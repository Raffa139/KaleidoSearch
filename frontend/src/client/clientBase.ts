const DEFAULT_HEADERS = {
  "Content-Type": "application/json"
};

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
  const response = await fetch(url, { headers: DEFAULT_HEADERS });

  if (!response.ok) {
    console.error(response.status, await response.text());
    throw new Error();
  }

  return response.json();
};

export const post = async <T>(url: string, body?: object): Promise<T> => {
  const response = await fetch(url, {
    method: "POST",
    headers: DEFAULT_HEADERS,
    body: body ? JSON.stringify(body) : undefined
  });

  if (!response.ok) {
    console.error(response.status, await response.text());
    throw new Error();
  }

  return response.json();
};

export const delete_ = async (url: string): Promise<void> => {
  const response = await fetch(url, {
    method: "DELETE",
    headers: DEFAULT_HEADERS
  });

  if (!response.ok) {
    console.error(response.status, await response.text());
    throw new Error();
  }

  return response.json();
};
