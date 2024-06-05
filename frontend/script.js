document.addEventListener('DOMContentLoaded', () => {
    const recognitionButton = document.getElementById('start-recognition');
    const recognizedText = document.getElementById('recognized-text');
    const textToSpeak = document.getElementById('text-to-speak');
    const nluEndPoint = 'http://localhost:8000/chat';

    // Speech Recognition
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            recognitionButton.textContent = 'Listening...';
        };

        recognition.onresult = (event) => {
            recognizedText.textContent = ''
            textToSpeak.textContent = ''
            const transcript = event.results[0][0].transcript;
            recognizedText.textContent = transcript;
            processNLU(transcript);
        };

        recognition.onerror = (event) => {
            console.error(event.error);
            recognitionButton.textContent = 'Start Recognition';
        };

        recognition.onend = () => {
            recognitionButton.textContent = 'Start Recognition';
        };

        recognitionButton.addEventListener('click', () => {
            recognition.start();
        });
    } else {
        recognitionButton.disabled = true;
        recognizedText.textContent = 'Speech recognition not supported in this browser.';
    }

    //NLU & Speech Synthesis
    async function processNLU(text) {
        await fetch(nluEndPoint, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
            },
          body: JSON.stringify({ chat_input: text,
          chat_history: []}),
        })
        .then(response => response.json())
        .then(data => {
          const responseText = data['output']
          textToSpeak.textContent = responseText;
          synthesizeSpeech(responseText);
        })
        .catch(error => {
            recognizedText.textContent = `Error occurred in NLU processing: ${error}`;
        });
      }

    function synthesizeSpeech(text) {
        const speech = new SpeechSynthesisUtterance(text);

        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(speech);
      }
});

