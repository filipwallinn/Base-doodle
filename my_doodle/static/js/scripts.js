// Preload default album art image, if this page has one
if (document.getElementById("albumArt")) {
  const preloadImage = new Image();
  preloadImage.src = "/default-image";
  preloadImage.onload = () => {
    document.getElementById("albumArt").classList.add("loaded");
  };
}

let isPlaying = true;

function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add("toast-visible"));

  setTimeout(() => {
    toast.classList.remove("toast-visible");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function setAlbumArtLoading(isLoading) {
  const spinner = document.getElementById("albumArtSpinner");
  if (spinner) spinner.classList.toggle("spinner-visible", isLoading);
}

function updateNowPlaying(track, artist) {
  const trackEl = document.getElementById("nowPlayingTrack");
  const artistEl = document.getElementById("nowPlayingArtist");
  if (!trackEl || !artistEl) return;

  if (track) {
    trackEl.textContent = track;
    artistEl.textContent = artist || "";
  } else {
    trackEl.textContent = "Nothing playing yet";
    artistEl.textContent = "";
  }
}

// Sync button, now-playing info, with the actual Spotify playback state
function syncPlaybackStatus() {
  const button = document.getElementById("playPauseButton");
  if (!button) return;

  fetch("/playback-status")
    .then(res => res.json())
    .then(data => {
      const flipper = button.querySelector(".flipper");

      if (data.isPlaying) {
        flipper.parentElement.classList.remove("flipped");
        isPlaying = true;
      } else {
        flipper.parentElement.classList.add("flipped");
        isPlaying = false;
      }

      updateNowPlaying(data.track, data.artist);
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

// Spotify's playback state takes a moment to catch up after a play command,
// so wait before re-reading it instead of racing an immediately-stale read.
function refreshAfterPlay() {
  updateAlbumArt();
  setTimeout(() => {
    syncPlaybackStatus();
    loadSimilarTracks();
  }, 1200);
}

// Play one or more track URIs and refresh the UI to match
function playUris(uris) {
  setAlbumArtLoading(true);
  return fetch("/play-song", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uris })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status !== "playing") {
      setAlbumArtLoading(false);
      showToast(data.message || "Couldn't play that track.", "error");
      return;
    }
    refreshAfterPlay();
  });
}

// Search and play an artist's top song
function searchByArtist() {
  const artist = document.getElementById("artistInput").value.trim();
  if (!artist) return;

  setAlbumArtLoading(true);
  fetch("/play-artist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ artist })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "playing") {
      refreshAfterPlay();
    } else {
      setAlbumArtLoading(false);
      showToast(data.message || "Artist not found.", "error");
    }
  });
}

// Search and play a specific song
function searchBySong() {
  const song = document.getElementById("songInput").value.trim();
  if (!song) return;

  setAlbumArtLoading(true);
  fetch("/play-song-by-name", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ song: song })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "playing") {
      refreshAfterPlay();
    } else {
      setAlbumArtLoading(false);
      showToast(data.message || "Song not found.", "error");
    }
  });
}

// Search Spotify and list results
function searchSpotify() {
  const query = document.getElementById("mainSearchInput").value.trim();
  if (!query) return;

  const list = document.getElementById("searchResults");
  list.innerHTML = "";

  fetch("/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: query, type: "track" })
  })
  .then(res => res.json())
  .then(results => {
    if (!results.length) {
      const li = document.createElement("li");
      li.textContent = "No results found.";
      list.appendChild(li);
      return;
    }

    results.forEach(item => {
      const li = document.createElement("li");
      li.textContent = `${item.name} — ${item.artist} (${item.album})`;
      li.style.cursor = "pointer";

      li.addEventListener("click", () => playUris([item.uri]));

      list.appendChild(li);
    });
  });
}

// Update album art with fade effect
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
        setAlbumArtLoading(false);
      });
  }, 1000);
}

// Load and render tracks similar to what's currently playing
function loadSimilarTracks() {
  const panel = document.getElementById("similarPanel");
  const list = document.getElementById("similarList");
  if (!panel || !list) return;

  fetch("/similar-tracks")
    .then(res => res.json())
    .then(tracks => {
      list.innerHTML = "";

      if (!tracks.length) {
        panel.classList.remove("similar-panel-visible");
        return;
      }

      tracks.forEach(track => {
        const card = document.createElement("button");
        card.className = "similar-card";

        const img = document.createElement("img");
        img.src = track.image || "/default-image";
        img.alt = track.name;

        const info = document.createElement("div");
        info.className = "similar-card-info";

        const nameEl = document.createElement("span");
        nameEl.className = "similar-card-name";
        nameEl.textContent = track.name;

        const artistEl = document.createElement("span");
        artistEl.className = "similar-card-artist";
        artistEl.textContent = track.artist;

        info.appendChild(nameEl);
        info.appendChild(artistEl);
        card.appendChild(img);
        card.appendChild(info);
        card.addEventListener("click", () => playUris([track.uri]));

        list.appendChild(card);
      });

      panel.classList.add("similar-panel-visible");
    });
}

// Show a hint about the current song
function showHint() {
  fetch("/hint")
    .then(res => res.json())
    .then(data => {
      const hintEl = document.getElementById("hintText");
      if (hintEl) {
        hintEl.textContent = data.hint;
      } else {
        showToast(data.hint, "info");
      }
    });
}

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

function bindEnterKey(inputId, action) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") action();
  });
}

window.addEventListener("DOMContentLoaded", () => {
  syncPlaybackStatus();
  setInterval(syncPlaybackStatus, 5000);
  loadSimilarTracks();

  bindEnterKey("mainSearchInput", searchSpotify);
  bindEnterKey("artistInput", searchByArtist);
  bindEnterKey("songInput", searchBySong);
});
