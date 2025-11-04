const typingForm = document.querySelector('.typing-form');
const chatList = document.querySelector('.chat-list');  
const deleteChatButton =  document.querySelector('#delet-chat-button');
let isResponseGenerating = false;
// const BASE_URL = 'http://localhost:3000';
const BASE_URL = "https://slide2study.onrender.com";
// const BASE_URL =
//   window.location.hostname === "localhost"
//     ? "http://localhost:3000"
//     : "https://slide2study.onrender.com";

let allMessages = []; //to resend this everytime to chatgpt 



document.addEventListener("submit", (e) => e.preventDefault());


const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");

// When clicked, open file picker
dropZone.addEventListener("click", () => fileInput.click());

// When files are selected via picker
fileInput.addEventListener("change", (e) => {
  handleFiles(e.target.files);
});

// Visual feedback for drag events
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.style.borderColor = "#007bff";
});

dropZone.addEventListener("dragleave", () => {
  dropZone.style.borderColor = "#aaa";
});

// Handle drop event
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.style.borderColor = "#aaa";
  handleFiles(e.dataTransfer.files);
});

/*
function handleFiles(files) {
  if (!files.length) return;

  const file = files[0];
  console.log("Uploading:", file.name);

  const formData = new FormData();
  formData.append("file", file);



  console.log("Files imported:", files);

  // Hide the initial screen
  const initialScreen = document.getElementById("initial-screen");
  initialScreen.style.display = "none";

  // Show the chat container
  const chatContainer = document.querySelector(".chat-container");
  chatContainer.style.display = "block";
}
  */

async function handleFiles(files) {
  if (!files.length) return;

  const file = files[0];
  console.log("Uploading:", file.name);

  const formData = new FormData();
  formData.append("file", file);
  event.preventDefault();

  try {
    const response = await fetch(`${BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    const result = await response.json();
    console.log("Upload successful:", result);
    const dropZone = document.getElementById("drop-zone");
    dropZone.classList.add("uploaded");
    dropZone.querySelector("p").textContent = "File uploaded successfully!";
  } catch (error) {
    console.error("Error uploading file:", error);
  }

  // try {
  //   const apiResponse = await fetchFromBackend(
  //     `${BASE_URL}/regular`,
  //     allMessages
  //   );
  //   console.log("API response after file upload:", apiResponse);
  // } catch (error) {
  //   console.error("Error fetching /regular:", error);
  // }

  const initialScreen = document.getElementById("initial-screen");
  const chatContainer = document.querySelector(".chat-container");

  // Wait 1 second to let user see "File uploaded successfully!"
  setTimeout(() => {
    initialScreen.classList.add("hidden");
    setTimeout(() => {
      initialScreen.style.display = "none";
      chatContainer.classList.remove("hidden");
    }, 600); // fade duration
  }, 1000); // wait 1 second before fading
}











document.querySelectorAll(".progress-bar .step").forEach((step) => {
  step.addEventListener("click", () => {
    // remove filled from all
    document
      .querySelectorAll(".progress-bar .step")
      .forEach((s) => s.classList.remove("filled"));
    // add filled to clicked one
    step.classList.add("filled");
  });
});

document.querySelectorAll(".progress-bar .step").forEach((step) => {
  step.addEventListener("click", () => {
    // Remove enlargement from all
    document
      .querySelectorAll(".progress-bar .step")
      .forEach((s) => s.classList.remove("enlarged"));
    // Add enlargement to clicked one
    step.classList.add("enlarged");
  });
});

async function handleBloomButtonClick(endpoint) {
  // Prevent overlapping requests
  if (isResponseGenerating) return;
  isResponseGenerating = true;

  // Create a loading response bubble
  const responseDiv = createResponseDiv();

  try {
    // Query backend (send full chat context)
    const apiResponse = await fetchFromBackend(
      `${BASE_URL}/${endpoint}`,
      allMessages
    );

    // Extract model output and display it
    const fullResponse = apiResponse.completion;
    displayRespone(fullResponse, responseDiv);
  } catch (error) {
    console.error(`Error fetching from /${endpoint}:`, error);
    responseDiv.querySelector(".text").innerText = "Error fetching response.";
    responseDiv.classList.remove("loading");
  } finally {
    isResponseGenerating = false;
  }
}

document.querySelectorAll(".progress-bar .step").forEach((step) => {
  step.addEventListener("click", () => {
    const endpoint = step.dataset.endpoint; // e.g. "remember"
    handleBloomButtonClick(endpoint);
  });
});













/*****************************************************************************************************************/

// Create a message element
// its either outgoing or incoming
const createMessageElement = (content, ...classes) => {
    const div = document.createElement("div"); // Create a new div element
    div.classList.add("message", ...classes);  // Add the "message" class and any additional classes to the div
    div.innerHTML = content; // Set the inner HTML content of the div
    return div;
}

// Create div for user input 
//return the div with the message  
const createInputDiv = (userMessage) => {
    const html = `
        <div class="message-content">
            <img src="image/user.jpg" alt="User Image" class="avatar">
            <p class="text"></p>
        </div>`;
    const inputDiv = createMessageElement(html, "outgoing"); // Create a new message element with the "outgoing" class
    inputDiv.querySelector(".text").innerText = userMessage; // Set the inner text of the text element to the user's message
    chatList.appendChild(inputDiv); // Append the new message element to the chat list

    const newMessage = { role: 'user', content: userMessage }; // Create a new message object
    allMessages.push(newMessage); // Add the new message to the messages array
}

//Copy text when copy icon pressed
const copyMessage = (copyIcon) => {
    const messageText = copyIcon.parentElement.querySelector(".text").innerText; // Retrieve the text content of the message associated with the copy icon
    navigator.clipboard.writeText(messageText); // Use the Clipboard to write the message text to the clipboard
    copyIcon.innerText = "done";  
    setTimeout(() => copyIcon.innerText = "content_copy", 1000);  // After 1 second, change the copy icon's text back to copy icon
}

//create the incoming message div and return it
const createResponseDiv = () => {
    const html =
            `<div class="message-content">
                <img src="image/gpt.jpg" alt="Gemini Image" class="avatar">
                <p class="text typing-indicator"></p>
            </div>
            <span onclick="copyMessage(this)"   class="icon material-symbols-rounded">content_copy</span>`;  //call copyMessage when Icon pressed
    const responeDiv = createMessageElement(html, "incoming", "loading"); // Create a new message element with the "incoming" and "loading" classes
    chatList.appendChild(responeDiv); // Append the new message element to the chat list
    return responeDiv;
}


//get a json from the backend
const fetchFromBackend = async (url, messages) => {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages })
    });
    return response.json();
};


//shows a typing effect
//input parameters text and textElement
const showTypingEffect = (text, textElement) => {
    const words = text.split(' '); // Split the input text into an array of words
    let currentWordIndex = 0;

    const typingInterval = setInterval(() => {
        textElement.innerText += (currentWordIndex === 0 ? '' : ' ') + words[currentWordIndex++];  // Append each word to the text element with a space
        if (currentWordIndex === words.length) { // If all words are displayed
            clearInterval(typingInterval); // Clear the interval to stop the typing effect
            isResponseGenerating = false; // The response is no longer generating
        }
        chatList.scrollTo(0, chatList.scrollHeight);
    }, 75); // Interval set to 75 milliseconds for each word

};

const fetchAndDisplayResponse = async (userMessage, responseDiv, appendText = '', endpoint) => {
    const textElement = responseDiv.querySelector('.text');
    try {
        //need to be sending the all the messages to the api here 
        const apiResponse =  await fetchFromBackend(`${BASE_URL}/${endpoint}`, allMessages);
        const fullResponse = apiResponse.completion + appendText;
        showTypingEffect(fullResponse, textElement);
        const newMessage = { role: 'assistant', content: fullResponse }; // Create a new message object
        allMessages.push(newMessage); // Add the new message to the messages array 
    } catch (error) {
        textElement.innerText = error.message; // Display error message in the UI
    } finally {
        responseDiv.classList.remove("loading"); // Remove loading state
    }
}


const fetchResponse = async (endpoint) => {
    try {
        const apiResponse =  await fetchFromBackend(`${BASE_URL}/${endpoint}`, allMessages);
        return apiResponse.completion;
    } catch (error) {
        throw new Error("Failed to fech gpt completion");
    }
}

const displayRespone = (text, responseDiv) => {
    const textElement = responseDiv.querySelector('.text');
    showTypingEffect(text, textElement);
    responseDiv.classList.remove("loading");
    const newMessage = { role: 'assistant', content: text }; // Create a new message object
    allMessages.push(newMessage); // Add the new message to the messages array 
}


const handleFormSubmission = async (appendText, endpoint) => {
    
    userMessage = typingForm.querySelector('.typing-input').value.trim() // Get the user's message 
    if (!userMessage || isResponseGenerating) return; //return if response is generating or userMesage is empty
    
    typingForm.reset(); // Reset the typing form input field
    isResponseGenerating = true; //the respone is generating

    createInputDiv(userMessage);   //create a div for the user input 
    const responseDiv = createResponseDiv();  // create the response div, which contains a load animation
    fetchAndDisplayResponse(userMessage, responseDiv, appendText, endpoint) //need to pass through the 

}



//make it appear
//make css


/*****************************************************************************************************************/
const createResponseDiv2 = () => {
    const html =
            `<div class="message-content">
                <img src="image/gpt.jpg" alt="Gemini Image" class="avatar">
                
                <div class="audio-text-player">
                  <p class="loading-text typing-indicator"></p>  
                    
                </div>
            </div>
            <span onclick="copyMessage(this)"   class="icon material-symbols-rounded">content_copy</span>`;  //call copyMessage when Icon pressed
    const responeDiv = createMessageElement(html, "incoming", "loading"); // Create a new message element with the "incoming" and "loading" classes
    chatList.appendChild(responeDiv); // Append the new message element to the chat list
    return responeDiv;
}


async function fetchGeneratedAudio(allMessages) {
  console.log("Started fetching audio...");
  try {
      const response = await fetch(`${BASE_URL}/hypnosisAudio`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ allMessages }),
    });
    if (!response.ok) 
      throw new Error("Failed to fetch audio from the server");
    
    const audioBlob = await response.blob(); // Receive the audio data as a Binary Large Object
    const audioUrl = URL.createObjectURL(audioBlob); // URL allows the browser to reference the audio data stored in memory without saving it to disk  
    return audioUrl; // Return the audio URL
  } catch (error) {
    throw new Error("Unable to fetch audio");  
  }
}

function createAudioPlayer(responseDiv) {
   responseDiv.classList.remove("loading");
   responseDiv.querySelector('.icon.material-symbols-rounded').remove();
    //responseDiv.querySelector('.text.typing-indicator').remove();
   
    const audioPlayerHTML = `   
        <div id="audioPlayer">
            <button id="playAudio">▶</button>
            <img id="downloadButton" src="image/download.png" alt="Download Audio"/>
            <progress id="progress" value="0" max="100"></progress> 
        </div>`;

    const messageContent = responseDiv.querySelector('.audio-text-player');    // Insert the audioPlayer HTML into the responseDiv
    messageContent.innerHTML += audioPlayerHTML;
    
    return messageContent.querySelector('#audioPlayer');
}


// Function to handle play/pause functionality
function setupPlayPauseButton(audioElement) {
    const playButton = document.getElementById("playAudio");
    playButton.addEventListener("click", () => {
        if (audioElement.paused) {  // If the audio is paused, start playing it
            audioElement.play()
                .then(() => {
                    playButton.textContent = "⏸"; // Switch to pause icon
                })
                .catch(error => {
                    console.error("Error playing audio:", error);
                });
        } else {  // If the audio is playing, pause it
            audioElement.pause();
            playButton.textContent = "▶"; // Switch to play icon
        }
    });

    // Update button state when audio ends
    audioElement.addEventListener("ended", () => {
        playButton.textContent = "▶"; // Reset to play icon
    });
}


// Function to handle progress bar updates and seeking
function setupProgressBar(audioElement) {
  const progressBar = document.getElementById("progress");
  let isDragging = false;     // Enable seeking by clicking or dragging
    
  audioElement.addEventListener("timeupdate", () => { // Update progress bar during playback
    const progress = (audioElement.currentTime / audioElement.duration) * 100;
    progressBar.value = progress;
  });
  progressBar.addEventListener("click", (event) => { // Allow seeking by clicking on the progress bar
    seekAudio(event, progressBar, audioElement);
  });
  progressBar.addEventListener("mousedown", () => {  // Set the dragging flag when the mouse button is pressed down on the progress bar
    isDragging = true;
  });
  document.addEventListener("mousemove", (event) => {   // Allow seeking by dragging the progress bar 
    if (isDragging) {
      seekAudio(event, progressBar, audioElement);
    }
  });
  document.addEventListener("mouseup", () => { // Reset the dragging flag when the mouse button is released
    isDragging = false;
  });
}

// Helper function to handle seeking
function seekAudio(event, progressBar, audioElement) {
  const rect = progressBar.getBoundingClientRect();   // Get the size and position of the progress bar
  const position = (event.clientX - rect.left) / rect.width;  // Calculate the click or drag position as a fraction of the progress bar's width
  progressBar.value = position * 100;    // Update the progress bar's value
  audioElement.currentTime = position * audioElement.duration;  // Update the audio playback position
}

// Function to create and append the download button
function setupDownloadButton(audioUrl) {
    const downloadButton = document.getElementById("downloadButton");
    downloadButton.addEventListener("click", () => {
        const link = document.createElement("a"); // Create a new 'a' (anchor) element to facilitate the download
        link.href = audioUrl; // Set the 'href' attribute of the link to the provided audio URL
        link.download = "smoking_cessastion_hypnotherapy.mp3";
        link.click();  // Programmatically trigger a click event on the link to start the download
  });
}

async function setupAudioPlayback(loadingText) {
    try {
        const responseDiv = createResponseDiv2(); //create a response div, that will have loading class
        const textElement = responseDiv.querySelector('.loading-text');
        showTypingEffect(`${loadingText} \n\n Generating custom hypnotherapy script, this may take a moment...`, textElement);
       
        const audioUrl = await fetchGeneratedAudio(allMessages); //get the hypnosis audio 
        const audioElement = new Audio(audioUrl);  //provides access HTMLAudioElement methods 
        
        createAudioPlayer(responseDiv); //create the audio player inside the respone div       
        setupPlayPauseButton(audioElement);
        setupProgressBar(audioElement);
        setupDownloadButton(audioUrl);

        chatList.scrollTo(0, chatList.scrollHeight);
        
  } catch (error) {
    console.error("Error setting up audio playback:", error);
  }
}

/*****************************************************************************************************************/


const questions = [
    "Lets test you knowledge using Bloom's Taxonomy. Select one of the levels of Blooms Taxonomy.",
];

let questionCounter = 0;

displayRespone(questions[questionCounter], createResponseDiv()); // Display response only on the first load

console.log(allMessages);


typingForm.addEventListener("submit", async (e) => {
  e.preventDefault(); // prevent reload

  const userMessage = typingForm.querySelector(".typing-input").value.trim();
  if (!userMessage || isResponseGenerating) return;

  typingForm.reset(); // clear box
  isResponseGenerating = true;

  createInputDiv(userMessage); // show user's message in chat
  const responseDiv = createResponseDiv(); // show loading bubble

  try {
    const apiResponse = await fetchFromBackend(
      `${BASE_URL}/regular`,
      allMessages
    );
    const fullResponse = apiResponse.completion;
    displayRespone(fullResponse, responseDiv);
  } catch (error) {
    console.error("Error fetching /regular:", error);
    responseDiv.querySelector(".text").innerText = "Error contacting backend.";
    responseDiv.classList.remove("loading");
  } finally {
    isResponseGenerating = false;
  }
});





/*****************************************************************************************************************/

// Add a click event listener to the delete chat button
// deleteChatButton.addEventListener('click', () => {
//         location.reload();
//         displayRespone(questions[0], createResponseDiv()); 
// });

/*****************************************************************************************************************/
