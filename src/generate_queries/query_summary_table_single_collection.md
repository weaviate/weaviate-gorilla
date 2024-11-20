
| Search Query | Filter | Aggregation | Group By | Natural Language Command |
|-------------|--------|-------------|----------|-------------------------|
| ✓ | integer | integer | ✓ | What is the average price of seasonal specialty menu items under $20, grouped by whether they are vegetarian or not? |
| ✓ | integer | integer |  | What is the average rating of romantic Italian restaurants that have a rating of 4 or above? |
| ✓ | integer | text | ✓ | Find all Italian restaurants with a cozy ambiance and an average rating of 3.5 or below. Once you've found these, group them by whether they are currently open, and aggregate the most common words used in their descriptions to capture typical features these restaurants offer. |
| ✓ | integer | text |  | Find restaurants where I can have a romantic dinner with outdoor seating that have an average rating greater than 4. Also, provide a list of the top 5 most mentioned types of cuisine across all these restaurants' descriptions. |
| ✓ | integer | boolean | ✓ | What are the most highly-rated vegan-friendly brunch spots that are currently open, and can you provide a breakdown of these spots by cuisine type? I need places with an average rating of 4.5 or higher, and show the percentage of them that are open now. |
| ✓ | integer | boolean |  | How many romantic restaurants with a relaxing atmosphere are currently open and have an average rating of at least 4? |
| ✓ | integer |  | ✓ | What romantic dining locations have an average rating greater than 4.5, and can you group them by whether they are currently open? |
| ✓ | integer |  |  | What are some affordable vegetarian dishes that cost less than $15? |
| ✓ | text | integer | ✓ | What is the average price of vegetarian healthy salads offered by different restaurants? |
| ✓ | text | integer |  | What is the highest average rating among currently open restaurants with excellent ambiance and food quality, whose names start with 'La'? |
| ✓ | text | text | ✓ | Find live jazz music restaurants that are currently open, which are suitable for a romantic dinner. Provide the count of these restaurants grouped by their cuisine style. |
| ✓ | text | text |  | How many different romantic Italian restaurants with vegan options and an average rating above 4.5 are there, and can you show me examples of their descriptions? |
| ✓ | text | boolean | ✓ | Find romantic Italian restaurants that offer organic options and group them by average rating. Show how many of these restaurants are currently open, also ensuring they are described as Italian in their profiles. |
| ✓ | text | boolean |  | How many romantic Italian cuisine restaurants are open right now, and list those with the word 'Restaurant' in their name? |
| ✓ | text |  | ✓ | Find cozy Italian restaurants that are currently open and group the results by their average rating. |
| ✓ | text |  |  | What are some romantic dinner spots that have a rooftop view, live jazz music, and whose names start with 'Cafe'? This requires understanding the context and ambiance described in the descriptions, while also filtering for restaurants based on the exact name pattern 'Cafe%'. |
| ✓ | boolean | integer | ✓ | What is the average rating of open restaurants with a cozy ambiance, categorized by cuisine type? |
| ✓ | boolean | integer |  | What is the average rating of family-friendly Thai restaurants with a relaxing ambiance that are currently open? |
| ✓ | boolean | text | ✓ | How many restaurants that are currently open and known for a cozy atmosphere are there for each type of cuisine? |
| ✓ | boolean | text |  | What are some cozy restaurants that are currently open, and what are the most common types of cuisine these open restaurants offer? |
| ✓ | boolean | boolean | ✓ | What percentage of restaurants known for romantic dining settings are currently open, and how are they grouped by average ratings? |
| ✓ | boolean | boolean |  | How many restaurants that are currently open offer an Italian ambiance? |
| ✓ | boolean |  | ✓ | Show me open restaurants with a romantic ambiance and group the results by their average rating so I can compare their ratings. |
| ✓ | boolean |  |  | What open restaurants offer a romantic Italian dining experience? |
| ✓ |  | integer | ✓ | What is the average price of affordable vegetarian meals with healthy ingredients, and can you group these meals by different restaurants to see where they are available? |
| ✓ |  | integer |  | What is the average price of healthy vegetarian meals across various restaurants' menus? |
| ✓ |  | text | ✓ | Can you find cozy Italian restaurants with a romantic ambiance and group them by their average rating? Also, please provide a summary of the most common features mentioned for open restaurants. |
| ✓ |  | text |  | Which restaurants have a cozy atmosphere and a romantic ambiance, and what are the top 5 most frequently mentioned cuisines overall? |
| ✓ |  | boolean | ✓ | Find Asian restaurants that have a cozy ambiance. For those that match, determine what percentage are currently open. Also, group the open restaurants by their average rating. This query not only seeks semantic matches but also uses aggregation and grouping on the data. |
| ✓ |  | boolean |  | What percentage of restaurants offering romantic Italian dining experiences are currently open? |
| ✓ |  |  | ✓ | Find trendy restaurants with a cozy atmosphere and group them by whether they are currently open or not. |
| ✓ |  |  |  | Find restaurants characterized by a cozy ambiance suitable for an intimate dinner, that are currently open and have an average rating of at least 4 stars. |
|  | integer | integer | ✓ | What is the average party size for reservations with more than 5 people, grouped by whether the reservation is confirmed or not? |
|  | integer | integer |  | What is the average rating of restaurants that have a rating of at least 4 stars? |
|  | integer | text | ✓ | How many unique names are there for reservations with a party size greater than 4, grouped by whether the reservation is confirmed? |
|  | integer | text |  | How many unique menu items are there in the restaurant menus that are priced under $20? |
|  | integer | boolean | ✓ | How many reservations are there with a party size of 5 or more, count how many of these are confirmed, and display the results grouped by party size? |
|  | integer | boolean |  | How many reservations are there for more than 4 people, and what percentage of these reservations are confirmed? |
|  | integer |  | ✓ | What are the menu items that cost more than $20, and how can they be grouped by whether they are vegetarian? |
|  | integer |  |  | Find all confirmed reservations where the party size is greater than or equal to 6 people. |
|  | text | integer | ✓ | What is the average rating for restaurants noted as having a 'cozy' ambiance, grouped by whether they are currently open or not? |
|  | text | integer |  | What is the average rating of restaurants that have 'Japanese' mentioned in their description? |
|  | text | text | ✓ | How many restaurants contain 'Cuisine' in their description, and what is the count of restaurants for each unique average rating? |
|  | text | text |  | How many restaurants have names that start with the letter 'A', and what is the count of these restaurants grouped by their description categories? |
|  | text | boolean | ✓ | What percentage of reservations made under the name 'John Doe' are confirmed, grouped by the size of the party? |
|  | text | boolean |  | How many Italian restaurants are currently open? |
|  | text |  | ✓ | Show me all the vegetarian items on the menu and group them by their name. |
|  | text |  |  | Find all restaurants that have the word 'Cafe' in their name. |
|  | boolean | integer | ✓ | What is the average number of people per confirmed reservation, grouped by the person who made the reservation? |
|  | boolean | integer |  | What is the average price of all vegetarian menu items? |
|  | boolean | text | ✓ | How many restaurants that are currently open are there for each different cuisine or ambiance type, and organize this information by their average rating score? |
|  | boolean | text |  | How many different party sizes are there among all confirmed reservations? |
|  | boolean | boolean | ✓ | How many confirmed reservations are there grouped by each party size? |
|  | boolean | boolean |  | How many reservations are confirmed, and what percentage of all reservations does this represent? |
|  | boolean |  | ✓ | Which vegetarian menu items are available, and can you group them by their price? |
|  | boolean |  |  | Which reservations are currently unconfirmed, indicating that they have not been finalized yet? |
|  |  | integer | ✓ | What is the average price of menu items, grouped by whether the item is vegetarian or not, in the menu database? |
|  |  | integer |  | What is the average price of all the menu items available across the various restaurants in the system? |
|  |  | text | ✓ | For each average rating score, how many times does each unique cuisine type appear in restaurant descriptions, and what are the top 5 most common words used to describe restaurant ambiance? |
|  |  | text |  | What are the different types of menu items available in terms of dietary options, such as vegetarian and non-vegetarian, and how many are there of each type based on their descriptions in the Menus collection? |
|  |  | boolean | ✓ | For each name under which reservations are made, what percentage of those reservations are confirmed? |
|  |  | boolean |  | How many reservations are there in total, and how many of them are confirmed versus not confirmed? |
|  |  |  | ✓ | What are all the unique restaurant descriptions that mention 'romantic Italian dining' and organize them by their average rating scores? |
