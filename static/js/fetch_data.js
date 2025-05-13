
async function fetchChampionData() {
    try {
        // Fetch latest version
        const versionResponse = await fetch('https://ddragon.leagueoflegends.com/api/versions.json');
        const versions = await versionResponse.json();
        const latestVersion = versions[0];

        // Fetch champion data
        const championsResponse = await fetch(`https://ddragon.leagueoflegends.com/cdn/${latestVersion}/data/en_US/champion.json`);
        const championsData = await championsResponse.json();

        const champions = championsData.data;
        const championList = document.getElementById('champion_list');

        for (let championId in champions) {
            let champion = champions[championId];
            let diff = champion.info.difficulty;
            let diffClass = diff <= 3 ? "easy" : diff <= 7 ? "medium" : "hard";

            championList.innerHTML += `
                <a href="/champion/${championId}" class="flex-item">
                    <div class="flex-icon">
                        <img src="https://ddragon.leagueoflegends.com/cdn/${latestVersion}/img/champion/${championId}.png" alt="${champion.name}">
                    </div>
                    <div class="champion-label">${champion.name}</div>
                    <div class="champion-description">${champion.title}</div>
                    <div class="difficulty-bar ${diffClass}"></div>
                </a>
            `;
        }
    } catch (error) {
        console.error('Error fetching champion data:', error);
    }
}

fetchChampionData();
