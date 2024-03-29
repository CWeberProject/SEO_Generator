from google.colab import files
uploaded = files.upload()

import re
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def extract_article_content(url):
    # Send a GET request to the URL
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title = soup.find('title').get_text() if soup.find('title') else ''

        # Create a new soup limited to the article's content only
        specific_section = soup.find('section', {'class': 'gh-content gh-canvas'})
        specific_soup = BeautifulSoup(str(specific_section), 'html.parser')

        # Delete any unwanted sections (content table, image labels)
        for figure in specific_soup.find_all('figure'):
          figure.decompose()
        for div in specific_soup.find_all('div'):
          div.decompose()

        # Extract headers (e.g., h1, h2, h3, etc.)
        headers = [header.get_text() for header in specific_soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]

        # Extract text content
        paragraphs = [p.get_text() for p in specific_soup.find_all('p')]
        content = ' '.join(paragraphs)

        return {
        'Title': title,
        'Headers': '\n'.join(headers),
        'Content': content
            }
    else:
        print(f"Failed to fetch URL: {url}")
        return None

def extract_title_from_url(url):
    # Extract the last part of the URL after the last '/'
    parts = url.split('/')
    title_with_dashes = parts[-2] if parts[-1] == '' else parts[-1]  # Consider -2 if last part is '/'

    # Remove trailing '/' if present in the extracted title
    if title_with_dashes.endswith('/'):
        title_with_dashes = title_with_dashes[:-1]

    # Check if the URL contains any language indication, exclude if found
    if re.search(r'/(pt|es|fr|de|it|ru|pl)/', url):
        return None  # Return None for non-English articles

    # Use regex to replace dashes with spaces and convert to lowercase
    title_with_spaces = re.sub(r'-', ' ', title_with_dashes).lower()

    return title_with_spaces

# Load sitemap as csv
df = pd.read_csv("planner5d_blog_posts.csv")

# Drop unecessary columns
df.drop(['lastmod','image/loc/__text','image/caption/__text'], axis = 'columns', inplace = True)

# Create a duplicate of URLs in a new column
df.insert(0, 'URLs', df['loc'])
df = df.rename(columns={'URLs': 'URLs', 'loc': 'titles'})

# Create a boolean mask filtering out all non-English blog posts
df['titles'] = df['titles'].map(extract_title_from_url)

# Drop all non-English blog posts
df = df.dropna()

# Reset the index
df.reset_index(inplace = True)
df = df.drop('index', axis = 1)

df.head()

df['Title'] = None
df['Headers']= None
df['Content']= None
i = 0

for url in df['URLs']:
  output = extract_article_content(url)
  df.at[i, 'Title'] = output['Title']
  df.at[i, 'Headers'] = output['Headers']
  df.at[i, 'Content'] = output['Content']
  i += 1

df = df.drop('titles', axis = 1)
df.head()

# Change title values to Unicode
articles = df['Content'].values.astype('U')

# Vectorize the text
vectorizer = TfidfVectorizer(stop_words='english')
features = vectorizer.fit_transform(articles)

# Implement the Elbow method to find the optimal K number of clusters
distorsions = []
K = range(1,50)
for k in K:
    kmeanModel = KMeans(n_clusters = k, n_init=10)
    kmeanModel.fit(features)
    distorsions.append(kmeanModel.inertia_)

# Plot the results to find the optimal K value
plt.figure(figsize=(16,8))
plt.plot(K, distorsions,'bx-')
plt.xlabel('k')
plt.ylabel('Distorsion')
plt.title('Elbow method showing the optimal k')
plt.show()

# from sklearn.metrics import silhouette_score

sil = []
kmax = 50

dissimilarity would not be defined for a single cluster, thus, minimum number of clusters should be 2
for k in range(2, kmax+1):
  kmeans = KMeans(n_clusters = k, n_init=10).fit(features)
  labels = kmeans.labels_
  sil.append(silhouette_score(features, labels, metric = 'euclidean'))

# Plot the results to find the optimal K value
plt.figure(figsize=(16,8))
plt.plot(K, sil,'bx-')
plt.xlabel('k')
plt.ylabel('Distorsion')
plt.title('Elbow method showing the optimal k')
plt.show()

"""Based on the results of both the Elbow method and the Silhouette method above, we will be choosing k = 25.

Although it does not provide optimal distorion, it seems to be good enough without having too many clusters.
"""

# We will now apply the K-mean clustering method on our titles dataset
k = 25
model = KMeans(n_clusters = k, init = 'k-means++', max_iter = 300, n_init = 10)
model.fit(features)

# Tag each cluster with the cluster it belongs to
df['cluster'] = model.labels_

# Group the clusters together into seperate files
clusters = df.groupby('cluster')

for cluster in clusters.groups:
    f = open('cluster'+str(cluster)+'.csv', 'w') # Create a CSV file
    data = clusters.get_group(cluster)['loc'] # Get loc column to extract titles
    f.write(data.to_csv())
    f.close

