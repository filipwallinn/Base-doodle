// Preload default image on page load
const preloadImage = new Image();
preloadImage.src = "/default-image";
preloadImage.onload = () => {
  const albumArt = document.getElementById("albumArt");
  albumArt.classList.add("loaded");
};

// Triggered when user clicks "Search and Play"
function searchAndPlay() {
  const artist = document.getElementById("artistInput").value;

  fetch("/play", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ artist })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "playing") {
      const albumArt = document.getElementById("albumArt");

      // Fade out current image
      albumArt.classList.remove("loaded");

      // Wait before fetching new image
      setTimeout(() => {
        const timestamp = new Date().getTime();
        const albumArtUrl = `/album-art?t=${timestamp}`;
        console.log("Fetching album art:", albumArtUrl);

        fetch(albumArtUrl)
          .then(res => res.blob())
          .then(blob => {
            const imgUrl = URL.createObjectURL(blob);

            // Revoke old blob URL if needed
            if (albumArt.src.startsWith("blob:")) {
              URL.revokeObjectURL(albumArt.src);
            }

            // Force repaint by clearing src first
            albumArt.src = "";
            albumArt.src = imgUrl;

            // Fade in new image
            albumArt.classList.add("loaded");
          });
      }, 1000); // 1 second delay
    } else {
      alert(data.message || "Something went wrong.");
    }
  });
}

function pausePlayback() {
  fetch("/pause", { method: "POST" })
    .then(res => res.json())
    .then(data => {
      console.log("Playback paused:", data);
    });
}

function showHint() {
  fetch("/hint")
    .then(res => res.json())
    .then(data => {
      alert("Hint: " + data.hint);
    });
}
