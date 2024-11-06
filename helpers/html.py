indexHTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Question Paper Creator - A Prototype</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; }
        .container { width: 80%; margin: auto; overflow: hidden; }
        header { background: #333; color: #fff; padding-top: 20px; border-bottom: #77aaff 3px solid; }
        header h1 { margin: 0; }
        .form-container { background: #fff; padding: 20px; margin-top: 20px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
        .form-container h1 { margin-bottom: 20px; }
        .form-container label { display: block; margin-bottom: 5px; }
        .form-container input, .form-container select { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 5px; }
        .form-container button { display: inline-block; background: #333; color: #fff; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .form-container button:hover { background: #555; }
        .question-field, .section-field { margin-bottom: 15px; }
        .question-field button, .section-field button { background: #e74c3c; color: #fff; margin-top: 5px; }
        .question-field button:hover, .section-field button:hover { background: #c0392b; }
        .stt-button { position: fixed; bottom: 20px; right: 20px; background-color: #e74c3c; color: #fff; padding: 15px; border-radius: 50%; border: none; font-size: 20px; cursor: pointer; box-shadow: 0 0 10px rgba(0, 0, 0, 0.3); }
    </style>
</head>
<body>
    <div class="container">
        <div class="form-container">
            <h1>Create Question Paper</h1>
            <form method="POST" enctype="multipart/form-data">
                <label>Class Name:</label>
                <input type="text" name="class_name" required>
                <label>Subject:</label>
                <input type="text" name="subject" required>
                <label>Term:</label>
                <input type="text" name="term" required>
                <label>Total Marks:</label>
                <input type="text" name="total_marks" required>
                <label>Number of Sections:</label>
                <input type="number" name="num_sections" min="0" required onchange="generateSections(this.value)">
                <div id="sections-container"></div>
                <button type="submit">Generate Document</button>
            </form>
        </div>
    </div>
    <button class="stt-button" onclick="toggleSTT()">🎤</button>
    <script>
        let recognition, sttActive = false, currentInput = null, finalText = '', lastCommandTime = 0;
        async function requestMicPermission() {
            try { await navigator.mediaDevices.getUserMedia({ audio: true }); alert("Microphone access granted. You can now use Speech-to-Text."); }
            catch (error) { alert("Microphone access denied. Speech-to-Text will not work without access."); console.error("Microphone permission denied:", error); }
        }
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            recognition.lang = 'en-IN';
            recognition.onresult = (event) => {
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript.trim();
                    if (event.results[i].isFinal) {
                        const processedText = processSpeechCommand(transcript);
                        if (processedText !== undefined) finalText += ' ' + processedText;
                    }
                }
                if (currentInput && finalText.length > 0 && finalText !== undefined) currentInput.value = finalText.trim();
            };
            recognition.onend = () => { if (sttActive) recognition.start(); };
            recognition.onerror = (event) => { console.log('Speech recognition error:', event); if (event.error === 'no-speech' || event.error === 'audio-capture') recognition.stop(); };
        } else alert("Your browser does not support Speech Recognition.");
        function toggleSTT() {
            sttActive = !sttActive;
            if (sttActive) {
                requestMicPermission();
                alert("Speech-to-Text activated. Click any input to start speaking.");
                showCommandsOverlay();
                recognition.start();
            } else {
                recognition.stop();
                alert("Speech-to-Text deactivated.");
                hideCommandsOverlay();
            }
        }
        document.addEventListener('focusin', (e) => { if (e.target.tagName === 'INPUT') { currentInput = e.target; finalText = currentInput.value; } });
        document.addEventListener('focusout', (e) => { if (e.target.tagName === 'INPUT') { currentInput = null; finalText = ''; } });
        function processSpeechCommand(text) {
            const formattedText = formatSpeechInput(text);
            if (currentInput) {
                const now = Date.now();
                if (text.toLowerCase() === 'next input' && now - lastCommandTime > 1000) {
                    finalText = '';
                    focusNextInput();
                    lastCommandTime = now;
                } else if (text.toLowerCase() === 'clear all') {
                    currentInput.value = '';
                    finalText = '';
                } else if (text.toLowerCase() === 'clear') {
                    finalText = finalText.trim().split(" ").slice(0, -1).join(" ");
                    currentInput.value = finalText;
                } else return formattedText;
            }
        }
        function formatSpeechInput(text) {
            text = text.charAt(0).toUpperCase() + text.slice(1);
            text = text.replace(/\bdash\b/gi, '_______').replace(/\bblank spaces\b/gi, '    ').replace(/\bcomma\b/gi, ',').replace(/\bperiod\b/gi, '.').replace(/\bexclamation mark\b/gi, '!').replace(/\bspace\b/gi, ' ').replace(/\bhypen\b/gi, '-').replace(/\bquestion mark\b/gi, '?');
            return text;
        }
        function focusNextInput() {
            const inputs = document.querySelectorAll('input, select');
            const index = Array.from(inputs).indexOf(currentInput);
            if (index !== -1 && index < inputs.length - 1) {
                currentInput = inputs[index + 1];
                finalText = currentInput.value;
                currentInput.focus();
            }
        }
        function showCommandsOverlay() {
            const overlay = document.createElement('div');
            overlay.id = 'commands-overlay';
            overlay.innerHTML = `
                <h3>Voice Commands:</h3>
                <ul>
                    <li><strong>Clear all:</strong> Clear entire input</li>
                    <li><strong>Clear:</strong> Clear the last word</li>
                    <li><strong>Next input:</strong> Move to the next input field</li>
                    <li><strong>Dash:</strong> Add "_______"</li>
                    <li><strong>Blank space:</strong> Add four spaces</li>
                    <li><strong>Comma / Period / Question mark:</strong> Add punctuation</li>
                </ul>
            `;
            document.body.appendChild(overlay);
            overlay.style.position = 'fixed';
            overlay.style.bottom = '20px';
            overlay.style.right = '20px';
            overlay.style.backgroundColor = '#333';
            overlay.style.color = '#fff';
            overlay.style.padding = '15px';
            overlay.style.borderRadius = '5px';
            overlay.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.5)';
            overlay.style.zIndex = '1000';
            overlay.addEventListener('click', hideCommandsOverlay);
        }
        function hideCommandsOverlay() {
            const overlay = document.getElementById('commands-overlay');
            if (overlay) overlay.remove();
        }
        function generateSections(numSections) {
            const sectionsContainer = document.getElementById('sections-container');
            sectionsContainer.innerHTML = '';
            for (let i = 0; i < numSections; i++) {
                const sectionDiv = document.createElement('div');
                sectionDiv.classList.add('section-field');
                sectionDiv.innerHTML = `
                    <h2>Section ${i + 1}</h2>
                    <label>Heading Text:</label>
                    <input type="text" name="section_${i}_heading" value="Q.${i+1} " required>
                    <label>Marks (e.g., '10'):</label>
                    <input type="text" name="section_${i}_marks" required>
                    <label>Number of Blank Lines After Each Question:</label>
                    <input type="number" name="section_${i}_blank_lines" min="0" value="0">
                    <label>Number of Questions in this Section:</label>
                    <input type="number" name="section_${i}_num_questions" min="0" required onchange="generateQuestions(${i}, this.value)">
                    <div id="questions-container-${i}"></div>
                `;
                sectionsContainer.appendChild(sectionDiv);
            }
        }
        function generateQuestions(sectionIndex, numQuestions) {
            const questionsContainer = document.getElementById(`questions-container-${sectionIndex}`);
            questionsContainer.innerHTML = '';
            for (let j = 0; j < numQuestions; j++) {
                const questionDiv = document.createElement('div');
                questionDiv.classList.add('question-field');
                questionDiv.innerHTML = `
                    <h3>Question ${j + 1}</h3>
                    <label>Question Text:</label>
                    <input type="text" name="section_${sectionIndex}_question_${j}_text" value="${j+1}. " required>
                    <label>Optional Image for Question:</label>
                    <input type="file" name="section_${sectionIndex}_question_${j}_image" accept="image/*">
                    <label>Does this question need an answer line?</label>
                    <select name="section_${sectionIndex}_question_${j}_answer_line">
                        <option value="yes">Yes</option>
                        <option value="no">No</option>
                    </select>
                `;
                questionsContainer.appendChild(questionDiv);
            }
        }
    </script>
</body>
</html>
'''