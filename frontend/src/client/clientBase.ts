export const DEFAULT_HEADERS = {
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
