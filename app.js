const chapterList = document.querySelector('#chapter-list');
const searchInput = document.querySelector('#search-input');
const resultCount = document.querySelector('#result-count');
const emptyState = document.querySelector('#empty-state');
const errorState = document.querySelector('#error-state');
const sheetFrame = document.querySelector('#consistency-sheet');

// 공개 Google Sheets 문서를 iframe용 미리보기 화면으로 표시합니다.
const PUBLISHED_SHEET_URL = 'https://docs.google.com/spreadsheets/d/1-PLvdTOC_fdulGL_S4gS7VuejX28AZNU4PH7CONRDoM/preview?gid=0&widget=true&headers=false';
sheetFrame.src = PUBLISHED_SHEET_URL;

let chapters = [];

function summarize(text, limit = 145) {
  const normalized = text.replace(/\s+/g, ' ').trim();
  return normalized.length <= limit ? normalized : `${normalized.slice(0, limit).trim()}…`;
}

function createCard(chapter) {
  const article = document.createElement('article');
  article.className = 'card';

  const badge = document.createElement('span');
  badge.className = 'card__number';
  badge.textContent = `${chapter.장}장`;

  const title = document.createElement('h3');
  title.textContent = chapter.제목;

  const body = document.createElement('p');
  body.textContent = summarize(chapter.본문);

  article.append(badge, title, body);
  return article;
}

function render(query = '') {
  const keyword = query.trim().toLocaleLowerCase('ko-KR');
  const filtered = chapters.filter((chapter) =>
    `${chapter.제목} ${chapter.본문}`.toLocaleLowerCase('ko-KR').includes(keyword),
  );

  chapterList.replaceChildren(...filtered.map(createCard));
  resultCount.textContent = `결과 ${filtered.length}건`;
  emptyState.hidden = filtered.length !== 0;
}

async function initialize() {
  try {
    const response = await fetch('./장데이터.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (!Array.isArray(data)) throw new Error('Invalid chapter data');
    chapters = data;
    render();
  } catch (error) {
    console.error(error);
    errorState.hidden = false;
    resultCount.textContent = '결과 0건';
  } finally {
    chapterList.setAttribute('aria-busy', 'false');
  }
}

searchInput.addEventListener('input', (event) => render(event.target.value));
initialize();
