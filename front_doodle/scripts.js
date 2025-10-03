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
  });

  fetch(`/album-art?artist=${encodeURIComponent(artist)}`)
    .then(res => res.blob())
    .then(blob => {
      const imgUrl = URL.createObjectURL(blob);
      document.getElementById("albumArt").src = imgUrl;
    });
}
