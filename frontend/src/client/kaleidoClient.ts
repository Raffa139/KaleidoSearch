import { AuthClient } from "./authClient";
import { ProductsClient } from "./productsClient";
import { UsersClient } from "./usersClient";

class KaleidoClient {
  Products: ProductsClient;
  Users: UsersClient;
  Auth: AuthClient;

  constructor(host: string, port: number) {
    this.Products = new ProductsClient(host, port);
    this.Users = new UsersClient(host, port);
    this.Auth = new AuthClient(host, port);
  }
}

export const client = new KaleidoClient("localhost", 8000);
