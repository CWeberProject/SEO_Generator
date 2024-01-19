# SEO_Generator
Goal: scrape the sitemaps of various websites surrounding one industry, extract the titles and content of all their SEO content (mainly blog articles), cluster the results and find valuable insights about popular SEO topics in your industry.

## Method
1. Query the sitemaps of the websites we're interested in and scrape the titles + URLs of their blog articles.
2. Using Beautiful Soup, extract the content of these articles and create a dataframe with URLs, Titles, and Content.
3. Find the optimal k for a k-means algorithm on this data using the elbow method.
4. Using the k-means clustering algorithm on the content of the articles, cluster the results to uncover valuable insights about the topics most competitors talk about in their blogs.
5. Create your own SEO strategy based on these results + a quick ahref analysis.
