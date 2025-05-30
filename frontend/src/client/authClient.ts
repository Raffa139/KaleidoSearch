import { BaseClient } from "./baseClient";
import type { Token } from "./types";

export class AuthClient extends BaseClient {
  resource(): string {
    return "auth/token";
  }

  googleLogin(idToken: string): Promise<Token> {
    return this.Http.post({ id_token: idToken }, "google");
  }
}