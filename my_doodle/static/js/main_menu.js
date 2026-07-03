function selectMode(mode) {
  const routes = {
    classicQuiz: '/classic-quiz',
    profileShuffle: '/profile-shuffle',
    musicTrivia: '/music-trivia',
    finishTheLyric: '/finish-the-lyric',
    albumArtChallenge: '/album-art-challenge',
    mysteryArtist: '/mystery-artist'
  };

  const route = routes[mode];
  if (!route) {
    console.warn("Unknown game mode:", mode);
    return;
  }

  window.location.href = route;
}

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fetch("/album-covers")
    .then(response => response.json())
    .then(data => {
      const leftCovers = [...data.left];
      const rightCovers = [...data.right];

      shuffleArray(leftCovers);
      shuffleArray(rightCovers);

      const leftInner = document.getElementById("album-scroll-left-inner");
      const rightInner = document.getElementById("album-scroll-right-inner");

      if (!leftInner || !rightInner) return;

      [...leftCovers, ...leftCovers].forEach((url, index) => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("album-img-wrapper");
        wrapper.style.setProperty("--i", index);

        const img = document.createElement("img");
        img.src = url;
        img.alt = "Album cover";

        wrapper.appendChild(img);
        leftInner.appendChild(wrapper);
      });

      [...rightCovers, ...rightCovers].forEach((url, index) => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("album-img-wrapper");
        wrapper.style.setProperty("--i", index);

        const img = document.createElement("img");
        img.src = url;
        img.alt = "Album cover";

        wrapper.appendChild(img);
        rightInner.appendChild(wrapper);
      });
    })
    .catch(error => console.error("Error loading album covers:", error));
});
