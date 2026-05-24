let currentQ = 0;
const totalQ = questionsData.length;
const status = Array(totalQ).fill('not-visited');
const answers = Array(totalQ).fill(null);

function renderPalette() {
    const palette = document.getElementById('palette');
    palette.innerHTML = '';
    for (let i = 0; i < totalQ; i++) {
        const item = document.createElement('div');
        item.className = 'palette-item';
        
        // Apply status class
        if (status[i] === 'answered') item.classList.add('answered');
        else if (status[i] === 'marked') item.classList.add('marked');
        else if (status[i] === 'visited') item.classList.add('visited');
        
        // Active highlight
        if (i === currentQ) item.classList.add('active');
        
        item.innerText = i + 1;
        item.onclick = () => jumpTo(i);
        palette.appendChild(item);
    }
}

function showQuestion(index) {
    currentQ = index;
    const q = questionsData[index];
    
    // Update status to visited if not already answered or marked
    if (status[index] === 'not-visited') status[index] = 'visited';
    
    document.getElementById('q-title').innerText = `Question ${index + 1}`;
    document.getElementById('q-text').innerText = q.question;
    
    const optionsCont = document.getElementById('options');
    optionsCont.innerHTML = '';
    
    const opts = [
        { id: 'option1', text: q.option1 },
        { id: 'option2', text: q.option2 },
        { id: 'option3', text: q.option3 },
        { id: 'option4', text: q.option4 }
    ];

    opts.forEach(opt => {
        if (!opt.text) return; // Skip empty options if any
        
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'option-btn';
        if (answers[index] === opt.id) btn.classList.add('selected');
        
        btn.innerHTML = `
            <div class="radio-dot"></div>
            <span>${opt.text}</span>
        `;
        btn.onclick = () => selectOption(index, opt.id);
        optionsCont.appendChild(btn);
    });

    renderPalette();
}

function selectOption(qIdx, optId) {
    answers[qIdx] = optId;
    // When an option is selected, keep the 'marked' status if it was marked, otherwise set to 'answered'
    if (status[qIdx] !== 'marked') status[qIdx] = 'answered';
    showQuestion(qIdx);
}

function next() { 
    if (currentQ < totalQ - 1) {
        showQuestion(currentQ + 1);
    }
}

function prev() { 
    if (currentQ > 0) showQuestion(currentQ - 1); 
}

function mark() { 
    status[currentQ] = 'marked'; 
    renderPalette(); 
    next(); 
}

function jumpTo(index) { 
    showQuestion(index); 
}

function submitExam() {
    const form = document.getElementById('examForm');
    questionsData.forEach((q, i) => {
        if (answers[i]) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = q.id;
            input.value = answers[i];
            form.appendChild(input);
        }
    });
    form.submit();
}

let timeLeft = durationSeconds;
const timerInterval = setInterval(() => {
    if (timeLeft <= 0) {
        clearInterval(timerInterval);
        submitExam();
    } else {
        timeLeft--;
        const m = Math.floor(timeLeft / 60);
        const s = timeLeft % 60;
        const timerEl = document.getElementById('timer');
        if (timerEl) {
            timerEl.innerText = `${m}:${s < 10 ? '0' : ''}${s}`;
            // Red timer alert when under 5 minutes
            if (timeLeft < 300) {
                timerEl.style.color = '#f43f5e';
                timerEl.style.background = 'rgba(244, 63, 94, 0.1)';
            }
        }
    }
}, 1000);

document.addEventListener('DOMContentLoaded', () => {
    if (totalQ > 0) showQuestion(0);
    else document.getElementById('q-text').innerText = "No questions available in this session.";
});
