import { BaseClient } from "./baseClient";
import type { Bookmark } from "./types";

export class BookmarksClient extends BaseClient {
  resource(): string {
    return "me/bookmarks";
  }

  async getAll(): Promise<Bookmark[]> {
    const bookmarks: Bookmark[] = await this.Http.get();
    return bookmarks.map(this.toLocalTime);
  }

  async getByProductId(productId: number): Promise<Bookmark | null> {
    try {
      return this.toLocalTime(await this.Http.get(`${productId}`));
    } catch (error) {
      return null;
    }
  }

  async create(productId: number): Promise<Bookmark> {
    return this.toLocalTime(await this.Http.post({ product_id: productId }));
  }

  delete(id: number | string): Promise<void> {
    return this.Http.delete_(`${id}`)
  }

  private toLocalTime(bookmark: Bookmark): Bookmark {
    return {
      ...bookmark,
      created_at: new Date(`${bookmark.created_at}Z`)
    };
  }
}
