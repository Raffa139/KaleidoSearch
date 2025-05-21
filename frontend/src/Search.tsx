import type { FunctionComponent } from "react";
import { useLoaderData } from "react-router";
import "./Search.css";

export const Search: FunctionComponent = () => {
  const { user } = useLoaderData();

  console.log("Logged in as", user);

  return (
    <>
      <header className="search-header">
        <div className="search-bar">
          <input type="text" placeholder="Search..." className="search-input" />
          <button className="search-button"><i className="fas fa-search"></i></button>
        </div>
      </header>

      <div className="results-container">
        <div className="search-result">
          <div className="result-icons">
            <button className="icon-btn"><i className="fas fa-bookmark"></i></button>
            <button className="icon-btn"><i className="fas fa-share-alt"></i></button>
          </div>
          <img src="/placeholder.png" alt="Result Image" className="result-image" />
          <div className="result-content">
            <h3 className="result-title">Example Search Result Title One</h3>
            <span className="price-tag">$19.99</span>
            <p className="result-description">
              This is a concise description of the search result. It provides a brief overview
              of the item or content.
            </p>
          </div>
        </div>

        <div className="search-result">
          <div className="result-icons">
            <button className="icon-btn"><i className="fas fa-heart"></i></button>
            <button className="icon-btn"><i className="fas fa-plus"></i></button>
          </div>
          <img src="/placeholder.png" alt="Result Image" className="result-image" />
          <div className="result-content">
            <h3 className="result-title">Another Product or Service Here</h3>
            <span className="price-tag">$49.50</span>
            <p className="result-description">
              Here's another descriptive text for a search result, giving more details about
              what's offered.
            </p>
          </div>
        </div>

        <div className="search-result">
          <div className="result-icons">
            <button className="icon-btn"><i className="fas fa-shopping-cart"></i></button>
          </div>
          <img src="/placeholder.png" alt="Result Image" className="result-image" />
          <div className="result-content">
            <h3 className="result-title">Third Item in the List</h3>
            <span className="price-tag">$75.00</span>
            <p className="result-description">
              A short and sweet description for the third search result, highlighting its key
              features.
            </p>
          </div>
        </div>

        <div className="search-result">
          <div className="result-icons">
            <button className="icon-btn"><i className="fas fa-bookmark"></i></button>
            <button className="icon-btn"><i className="fas fa-share-alt"></i></button>
          </div>
          <img src="/placeholder.png" alt="Result Image" className="result-image" />
          <div className="result-content">
            <h3 className="result-title">Example Search Result Title One</h3>
            <span className="price-tag">$19.99</span>
            <p className="result-description">
              This is a concise description of the search result. It provides a brief overview
              of the item or content.
            </p>
          </div>
        </div>

        <div className="search-result">
          <div className="result-icons">
            <button className="icon-btn"><i className="fas fa-heart"></i></button>
            <button className="icon-btn"><i className="fas fa-plus"></i></button>
          </div>
          <img src="/placeholder.png" alt="Result Image" className="result-image" />
          <div className="result-content">
            <h3 className="result-title">Another Product or Service Here</h3>
            <span className="price-tag">$49.50</span>
            <p className="result-description">
              Here's another descriptive text for a search result, giving more details about
              what's offered.
            </p>
          </div>
        </div>

        <div className="search-result">
          <div className="result-icons">
            <button className="icon-btn"><i className="fas fa-shopping-cart"></i></button>
          </div>
          <img src="/placeholder.png" alt="Result Image" className="result-image" />
          <div className="result-content">
            <h3 className="result-title">Third Item in the List</h3>
            <span className="price-tag">$75.00</span>
            <p className="result-description">
              A short and sweet description for the third search result, highlighting its key
              features.
            </p>
          </div>
        </div>
      </div>
    </>
  );
};