// Preload default image on page load
const preloadImage = new Image();
preloadImage.src = "/default-image";
preloadImage.onload = () => {
  const albumArt = document.getElementById("albumArt");
  albumArt.classList.add("loaded");
};

let isPlaying = true;

// Sync button with Spotify playback status
function syncPlaybackStatus() {
  fetch("/playback-status")
    .then(res => res.json())
    .then(data => {
      const button = document.getElementById("playPauseButton");
      const flipper = button.querySelector(".flipper");

      if (data.isPlaying) {
        flipper.parentElement.classList.remove("flipped");
        isPlaying = true;
      } else {
        flipper.parentElement.classList.add("flipped");
        isPlaying = false;
      }
    });
}

// Toggle play/pause and flip icon
function togglePlayback() {
  const button = document.getElementById("playPauseButton");
  const flipper = button.querySelector(".flipper");

  if (isPlaying) {
    fetch("/pause", { method: "POST" })
      .then(res => res.json())
      .then(() => {
        flipper.parentElement.classList.add("flipped");
        isPlaying = false;
      });
  } else {
    fetch("/resume", { method: "POST" })
      .then(res => res.json())
      .then(() => {
        flipper.parentElement.classList.remove("flipped");
        isPlaying = true;
      });
  }
}

// 🔍 Search and play by artist
function searchByArtist() {
  const artist = document.getElementById("artistInput").value;

  fetch("/play-artist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ artist })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "playing") {
      updateAlbumArt();
    } else {
      alert(data.message || "Artist not found.");
    }
  })
  .then(() => {
    syncPlaybackStatus();
  });
}

// 🎵 Search and play by song
function searchBySong() {
  const song = document.getElementById("songInput").value;

  fetch("/play-song-by-name", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ song: song })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "playing") {
      updateAlbumArt();
    } else {
      alert(data.message || "Song not found.");
    }
  })
  .then(() => {
    syncPlaybackStatus();
  });
}

// 🔍 Search Spotify and list results
function searchSpotify() {
  const query = document.getElementById("mainSearchInput").value;

  fetch("/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: query, type: "track" })
  })
  .then(res => res.json())
  .then(results => {
    const list = document.getElementById("searchResults");
    list.innerHTML = "";

    results.forEach(item => {
      const li = document.createElement("li");
      li.textContent = `${item.name} — ${item.artist} (${item.album})`;
      li.style.cursor = "pointer";

      li.addEventListener("click", () => {
        fetch("/play-song", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ uris: [item.uri] })
        })
        .then(() => {
            updateAlbumArt(); // trigger album art refresh
            syncPlaybackStatus(); // also update play/pause button
        });
      });

      list.appendChild(li);
    });
  });
}

// 🎨 Update album art with fade effect
function updateAlbumArt() {
  const albumArt = document.getElementById("albumArt");
  albumArt.classList.remove("loaded");

  setTimeout(() => {
    const timestamp = new Date().getTime();
    const albumArtUrl = `/album-art?t=${timestamp}`;

    fetch(albumArtUrl)
      .then(res => res.blob())
      .then(blob => {
        const imgUrl = URL.createObjectURL(blob);

        if (albumArt.src.startsWith("blob:")) {
          URL.revokeObjectURL(albumArt.src);
        }

        albumArt.src = "";
        albumArt.src = imgUrl;
        albumArt.classList.add("loaded");
      });
  }, 1000);
}

// 💡 Show a hint about the current song
function showHint() {
  fetch("/hint")
    .then(res => res.json())
    .then(data => {
      alert("Hint: " + data.hint);
    });
}

// 🎉 Spheal surprise animation
const sphealButton = document.getElementById("sphealSurprise");
if (sphealButton) {
  sphealButton.addEventListener("click", () => {
    const spheal = document.createElement("img");
    spheal.src = "/static/images/spheal.gif";
    spheal.id = "spheal";
    document.body.appendChild(spheal);

    setTimeout(() => {
      spheal.remove();
    }, 5000);
  });
}

function goToMainMenu() {
  window.location.href = "/";
}