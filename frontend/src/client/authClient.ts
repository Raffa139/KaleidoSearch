import * as Http from "./clientBase";
import type { Token } from "./types";

export class AuthClient extends Http.ClientBase {
  resource(): string {
    return "auth";
  }

  googleLogin(idToken: string): Promise<Token> {
    return Http.post(`${this.baseUrl()}/token/google`, { id_token: idToken });
  }
}