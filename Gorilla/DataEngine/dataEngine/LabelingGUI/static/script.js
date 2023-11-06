const apiUrl = "http://localhost:8000";

let paragraphs = [];

let currentParagraphIndex = 0;
const textArea = document.getElementById("text-area");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");

// Fetch the paragraphs from the API
fetch(`${apiUrl}/paragraphs`)
  .then(response => response.json())
  .then(data => {
    paragraphs = data;
    textArea.value = paragraphs[currentParagraphIndex];
    updateButtons();
  });

function updateButtons() {
  prevBtn.disabled = currentParagraphIndex === 0;
  nextBtn.disabled = currentParagraphIndex === paragraphs.length - 1;
}

prevBtn.addEventListener("click", () => {
  currentParagraphIndex--;
  textArea.value = paragraphs[currentParagraphIndex];
  updateButtons();
});

nextBtn.addEventListener("click", () => {
  currentParagraphIndex++;
  textArea.value = paragraphs[currentParagraphIndex];
  updateButtons();
});

function saveEdits() {
  // Get the current paragraph index
  console.log("HERE");
  let currentIndex = currentParagraphIndex;

  // Get the textarea element
  let textarea = document.getElementById("text-area");

  // Get the current text from the textarea
  let currentText = textarea.value;

  // Update the text for the current paragraph in the paragraphs array
  paragraphs[currentIndex] = currentText;
  console.log("HERE2");
  // Send a PUT request to update the paragraph in the API
  console.log(paragraphs[currentIndex]);
  fetch(`${apiUrl}/paragraphs/${currentIndex}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ paragraph: paragraphs[currentIndex] })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to save edits");
      }
    })
    .catch(error => {
      console.error(error);
      alert("Failed to save edits");
    });
}

function newEntry() {
  // Get the index of the current paragraph
  let currentIndex = currentParagraphIndex;

  // Send a POST request to add a new paragraph with an empty content at the current index
  fetch(`${apiUrl}/newentry/${currentIndex}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ content: "placeholder" }),
  })
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to add paragraph");
      }
      // Update the paragraphs list with the new paragraph
      paragraphs.splice(currentIndex, 0, { content: "" });
      // Update the current paragraph index to point to the new paragraph
      currentParagraphIndex = currentIndex;
      updateButtons();
    })
    .catch(error => {
      console.error(error);
      alert("Failed to add paragraph");
    });
}



function nextParagraph() {
  saveEdits(); // Save any edits before moving to the next paragraph

  // Move to the next paragraph
  currentParagraphIndex++;

  // If there are no more paragraphs, wrap around to the beginning
  if (currentParagraphIndex >= paragraphs.length) {
    currentParagraphIndex = 0;
  }

  // Update the paragraph index and text
  textArea.value = paragraphs[currentParagraphIndex].content;
  updateButtons();
}
