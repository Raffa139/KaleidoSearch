import { ClientBase, DEFAULT_HEADERS } from "./clientBase";
import type { ProductSummary } from "./types";

export class ProductsClient extends ClientBase {
  resource(): string {
    return "products";
  }

  async summarize(ids: number[], length: number = 25): Promise<ProductSummary[]> {
    const response = await fetch(`${this.baseUrl()}/summarize?length=${length}`, {
      method: "POST",
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(ids)
    });

    if (!response.ok) {
      console.error(response.status, await response.text());
      throw new Error("Failed to fetch product summary");
    }

    return response.json();
  }
}
