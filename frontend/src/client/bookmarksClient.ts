import * as Http from "./clientBase";
import type { Bookmark } from "./types";

export class BookmarksClient extends Http.ClientBase {
  uid: number | string;

  constructor(host: string, port: number, uid: number | string, rootPath: string = "") {
    super(host, port, rootPath);
    this.uid = uid;
  }

  resource(): string {
    return "bookmarks";
  }

  baseUrl(): string {
    return super.baseUrl().replace("{uid}", String(this.uid));
  }

  async getAll(): Promise<Bookmark[]> {
    const bookmarks: Bookmark[] = await Http.get(`${this.baseUrl()}`);
    return bookmarks.map(this.toLocalTime);
  }

  async getByProductId(productId: number): Promise<Bookmark | null> {
    try {
      return this.toLocalTime(await Http.get(`${this.baseUrl()}/${productId}`));
    } catch (error) {
      return null;
    }
  }

  async create(productId: number): Promise<Bookmark> {
    return this.toLocalTime(await Http.post(`${this.baseUrl()}`, { product_id: productId }));
  }

  delete(id: number | string): Promise<void> {
    return Http.delete_(`${this.baseUrl()}/${id}`)
  }

  private toLocalTime(bookmark: Bookmark): Bookmark {
    return {
      ...bookmark,
      created_at: new Date(`${bookmark.created_at}Z`)
    };
  }
}
