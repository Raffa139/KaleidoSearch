import { useState, type FunctionComponent } from "react";
import { useLoaderData, useOutletContext } from "react-router";
import { SearchBar } from "./search/SearchBar";
import { useThreadContext } from "./useThreadContext";
import type { Product, QueryEvaluation, User } from "../../client/types";
import { ProductSkeleton } from "../../products/ProductSkeleton";
import { ProductProvider } from "../../products/ProductProvider";
import "./thread.css";

export const Thread: FunctionComponent = () => {
  const thread = useLoaderData<QueryEvaluation>();
  const user = useOutletContext<User>();

  const { isBusy, getRecommendations } = useThreadContext();

  const [queryEvaluation, setQueryEvaluation] = useState<QueryEvaluation | undefined>(thread);
  const [products, setProducts] = useState<Product[]>([]);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [hasSearchResults, setHasSearchResults] = useState<boolean>(false);

  console.log("Logged in as", user, "in thread", thread);

  const handleSearch = async (queryEvaluation?: QueryEvaluation) => {
    setQueryEvaluation(queryEvaluation);
    const products = await getRecommendations(user.id, thread.thread_id);
    setProducts(products);
    setHasSearched(true);
    setHasSearchResults(products.length > 0);
  };

  return (
    <div className="container">
      <SearchBar queryEvaluation={queryEvaluation} onSearch={handleSearch} />

      <div className="results-container">
        <ProductSkeleton loading={isBusy} count={3} />

        {!isBusy && <ProductProvider products={products} />}

        {hasSearched && !hasSearchResults && !isBusy && (
          <p>No results found. Please try a different search.</p>
        )}
      </div>
    </div>
  );
};
