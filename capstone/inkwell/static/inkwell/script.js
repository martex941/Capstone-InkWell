function timeline() {

    // By default show the main timeline with all inks
    document.querySelector("#main-timeline").style.display = 'block';
    document.querySelector("#following-timeline").style.display = 'none';

    document.querySelector("#mainTimelineBtn").style.display = 'none';

    // Clear the timeline feed
    document.querySelector("#main-timeline").innerHTML = '';
    document.querySelector("#following-timeline").innerHTML = '';

    // Declare the page
    let page = 1;
    load(page, "allInks");

    function infiniteScroll (timeline) {
        window.onscroll = () => {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
                load(page, timeline);
                page++;
            }
        };
    }
    
    function load(page, timeline) {
        fetch(`index_cols/${page}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            data[timeline].forEach(element => {
                const ink_div = document.createElement('div');
                ink_div.className = 'inkDiv';

                const statusSpan = document.createElement('span');
                if (!element.updateStatus) {
                    statusSpan.innerHTML = `<a href="well/${element.inkOwner}"></a> posted a new Ink`;
                }
                else {
                    statusSpan.innerHTML = `<a href="well/${element.inkOwner}"></a> updated ${element.title}`;
                }
                ink_div.append(statusSpan);

                const contents = document.createElement('p');
                contents.className = 'inkPostDescription';
                contents.innerHTML = `${element.description}`
                ink_div.append(contents)

                const date = document.createElement('span');
                date.className = 'date';
                date.innerHTML = `Created: ${element.creation_date}`
                ink_div.append(date)

                document.querySelector("#timeline").append(ink_div);

            });
        })
    }
    function mainTimelineBtn () {
        page = 1;
        document.querySelector("#mainTimelineBtn").style.display = 'block';
        document.querySelector("#followingTimelineBtn").style.display = 'none';
        load(page, "allInks");
        infiniteScroll("allInks");
    }
    function followingTimelineBtn () {
        page = 1;
        document.querySelector("#mainTimelineBtn").style.display = 'none';
        document.querySelector("#followingTimelineBtn").style.display = 'block';
        load(page, "followingInks");
        infiniteScroll("followingInks");
    }
    document.querySelector("#mainTimelineBtn").addEventListener('click', mainTimelineBtn);
    document.querySelector("#followingTimelineBtn").addEventListener('click', followingTimelineBtn);
}

function notifications() {
    
}