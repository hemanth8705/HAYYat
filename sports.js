document.addEventListener('DOMContentLoaded', function() {
    // Fetch news data from the JSON file
    fetch('news_data.json')
        .then(response => response.json())
        .then(data => {
            const sportsNews = data.sports;

            const newsCardsContainer = document.getElementById('news-cards');

            sportsNews.forEach(news => {
                const card = document.createElement('div');
                card.classList.add('card');

                // Apply sentiment-specific classes
                if (news.sentiment === 'positive') {
                    card.classList.add('positive-news');
                } else if (news.sentiment === 'negative') {
                    card.classList.add('negative-news');
                } else {
                    card.classList.add('neutral-news');
                }

                const headline = document.createElement('h2');
                headline.textContent = news.sentiment.charAt(0).toUpperCase() + news.sentiment.slice(1) + " News";

                const listItem = document.createElement('li');
                const link = document.createElement('a');
                link.href = news.url;
                link.target = '_blank';
                link.textContent = news.headline;
                listItem.appendChild(link);

                card.appendChild(headline);
                const ul = document.createElement('ul');
                ul.appendChild(listItem);
                card.appendChild(ul);

                newsCardsContainer.appendChild(card);
            });
        })
        .catch(error => console.error('Error fetching news:', error));
});
