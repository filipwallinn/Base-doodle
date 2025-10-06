
// 🚀 Sync playback status on page load
window.addEventListener("DOMContentLoaded", () => {
  syncPlaybackStatus();
  setInterval(syncPlaybackStatus, 5000); // check every 5 seconds

  const selectedMode = localStorage.getItem('selectedMode');
  if (selectedMode) {
    switch (selectedMode) {
      case 'profileShuffle':
        startProfileShuffle();
        break;
      case 'musicTrivia':
        startMusicTrivia();
        break;
      case 'finishTheLyric':
        startFinishTheLyric();
        break;
      case 'albumArtChallenge':
        startAlbumArtChallenge();
        break;
      case 'mysteryArtist':
        startMysteryArtist();
        break;
      case 'classicQuiz':
        startClassicQuiz();
        break;
      default:
        console.warn("Unknown game mode:", selectedMode);
      localStorage.removeItem('selectedMode');
    }
    // Clear the stored mode after starting
    localStorage.removeItem('selectedMode');
  }
});

// Game mode selection
function selectMode(mode) {
  localStorage.setItem('selectedMode', mode);
  switch (mode) {
    case 'classicQuiz':
      window.location.href = '/classic-quiz';
      break;
    case 'musicTrivia':
      window.location.href = '/music-trivia';
      break;
    case 'finishTheLyric':
      window.location.href = '/finish-the-lyric';
      break;
    case 'albumArtChallenge':
      window.location.href = '/album-art-challenge';
      break;
    case 'mysteryArtist':
      window.location.href = '/mystery-artist';
      break;
    case 'profileShuffle':
      window.location.href = '/profile-shuffle';
      break;
    default:
      console.warn("Unknown game mode:", mode);
  }
}

//Placeholder function
function startClassicQuiz() {
  console.log("Classic Quiz started.");
  // Add your quiz logic here later
}

document.addEventListener("DOMContentLoaded", () => {
  fetch("/album-covers")
    .then(response => response.json())
    .then(data => {
      const leftCovers = [...data.left, ...data.left]; // Duplicate for looping
      const rightCovers = [...data.right, ...data.right];

      const leftInner = document.getElementById("album-scroll-left-inner");
      const rightInner = document.getElementById("album-scroll-right-inner");

      if (!leftInner || !rightInner) return;

      leftCovers.forEach(url => {
        const img = document.createElement("img");
        img.src = url;
        img.alt = "Album cover";
        leftInner.appendChild(img);
      });

      rightCovers.forEach(url => {
        const img = document.createElement("img");
        img.src = url;
        img.alt = "Album cover";
        rightInner.appendChild(img);
      });
    })
    .catch(error => console.error("Error loading album covers:", error));
});
