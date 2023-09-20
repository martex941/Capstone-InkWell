function index_cols() {
    fetch('index_cols')
    .then(response => response.json())
    .then(data => {
        console.log(data);
        for (let i = 0; i < 10; i++) {
            // // POPULAR AUTHORS THIS WEEK
            // const popauthElement = data['popularAuthors_col'][i];
            // const popauthDiv = document.createElement('div');
            // popauthDiv.className = 'popauthDiv'

            // // <a class="authorLink" href="/well/${popauthElement.username}"><h5 class="lead">${popauthElement.username}</h5></a>
            // const a_pop = document.createElement("a");
            // a_pop.href = `/well/${popauthElement.username}`;
            // a_pop.className = 'authorLink';
            // const h5_pop = document.createElement("h5");
            // h5_pop.className = 'lead';
            // h5_pop.innerHTML = `${popauthElement.username}`;
            // a_pop.appendChild(h5_pop);
            // popauthDiv.append(a_pop);

            // document.querySelector("#popularAuthors").append(popauthDiv);

        }
    })
}