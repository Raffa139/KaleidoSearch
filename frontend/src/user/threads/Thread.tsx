import { useState, type FunctionComponent } from "react";
import { useLoaderData } from "react-router";
import { SearchBar } from "./search/SearchBar";
import { useThreadContext } from "./useThreadContext";
import { HttpError } from "../../client/baseClient";
import type { Product, QueryEvaluation } from "../../client/types";
import { ProductSkeleton } from "../../products/ProductSkeleton";
import { ProductProvider } from "../../products/ProductProvider";
import "./thread.css";

export const Thread: FunctionComponent = () => {
  const thread = useLoaderData<QueryEvaluation>();

  const { isBusy, getRecommendations } = useThreadContext();

  const [queryEvaluation, setQueryEvaluation] = useState<QueryEvaluation | undefined>(thread);
  const [products, setProducts] = useState<Product[]>([]);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [hasSearchResults, setHasSearchResults] = useState<boolean>(false);
  const [searchNeedsRefinement, setSearchNeedsRefinement] = useState<boolean>(false);

  const handleSearch = async (queryEvaluation?: QueryEvaluation) => {
    setQueryEvaluation(queryEvaluation);

    try {
      const recommendations = await getRecommendations(thread.thread_id);
      setProducts(recommendations);
      setHasSearched(true);
      setHasSearchResults(recommendations.length > 0);
      setSearchNeedsRefinement(false);
    } catch (error) {
      if (error instanceof HttpError && error.code === 400) {
        setSearchNeedsRefinement(true);
      }
    }
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

        {searchNeedsRefinement && !isBusy && (
          <p>Search needs refinement. Please provide more details.</p>
        )}
      </div>
    </div>
  );
};
