function index_cols() {
    fetch('index_cols')
    .then(response => response.json())
    .then(data => {
        console.log(data);
        for (let i = 0; i < 10; i++) {
            // POPULAR AUTHORS THIS WEEK
            const popauthElement = data['popularAuthors_col'][i];
            const popauthDiv = document.createElement('div');
            popauthDiv.className = 'popauthDiv'

            // <a class="authorLink" href="/well/${popauthElement.username}"><h5 class="lead">${popauthElement.username}</h5></a>
            const a_pop = document.createElement("a");
            a_pop.href = `/well/${popauthElement.username}`;
            a_pop.className = 'authorLink';
            const h5_pop = document.createElement("h5");
            h5_pop.className = 'lead';
            h5_pop.innerHTML = `${popauthElement.username}`;
            a_pop.appendChild(h5_pop);
            popauthDiv.append(a_pop);

            document.querySelector("#popularAuthors").append(popauthDiv);

            // TOP AUTHORS THIS WEEK
            const topauthElement = data['topAuthors_col'][i];
            const topauthDiv = document.createElement('div');
            topauthDiv.className = 'topauthDiv'

            const a_top = document.createElement("a");
            a_top.href = `/well/${topauthElement.username}`;
            a_top.className = 'authorLink';
            const h5_top = document.createElement("h5");
            h5_top.className = 'lead';
            h5_top.innerHTML = `${topauthElement.username}`;
            a_top.appendChild(h5_top);
            topauthDiv.append(a_top);

            document.querySelector("#topAuthors").append(topauthDiv);

            // TOP CO-AUTHORS THIS WEEK
            const topcoauthElement = data['topCoAuthors_col'][i];
            const topcoauthDiv = document.createElement('div');
            popauthDiv.className = 'topcoauthDiv'

            const a_cotop = document.createElement("a");
            a_cotop.href = `/well/${topcoauthElement.username}`;
            a_cotop.className = 'authorLink';
            const h5_cotop = document.createElement("h5");
            h5_cotop.className = 'lead';
            h5_cotop.innerHTML = `${topcoauthElement.username}`;
            a_cotop.appendChild(h5_cotop);
            topcoauthDiv.append(a_cotop);

            document.querySelector("#topCoAuthors").append(topcoauthDiv);
        }
    })
}