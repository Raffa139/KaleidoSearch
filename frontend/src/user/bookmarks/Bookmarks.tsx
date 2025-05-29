import type { FunctionComponent } from "react";
import { useLoaderData } from "react-router";
import type { Bookmark } from "../../client/types";
import { ProductProviderByIds } from "../../products/ProductProviderByIds";
import "./bookmarks.css";

export const Bookmarks: FunctionComponent = () => {
  const bookmarks = useLoaderData<Bookmark[]>();
  const productIds = bookmarks.map(bookmark => bookmark.product_id);

  return (
    <div className="container">
      <div className="bookmarks">
        <h2 className="title-header">Bookmarks</h2>

        <div className="results-container">
          <ProductProviderByIds productIds={productIds} showBookmarkDate />
        </div>
      </div>
    </div>
  )
};
