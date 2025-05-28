import { ProductsClient } from "./productsClient";
import { UsersClient } from "./usersClient";

class KaleidoClient {
  Products: ProductsClient;
  Users: UsersClient;

  constructor(host: string, port: number) {
    this.Products = new ProductsClient(host, port);
    this.Users = new UsersClient(host, port);
  }
}

export const client = new KaleidoClient("localhost", 8000);
