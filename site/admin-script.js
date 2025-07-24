const list = document.getElementById("item-list");
const search = document.getElementById("search");
const pagination = document.getElementById("pagination");
const exportBtn = document.getElementById("export-btn");
const tabCars = document.getElementById("tab-cars");
const tabSkins = document.getElementById("tab-skins");
const modal = document.getElementById("edit-modal");
const saveBtn = document.getElementById("save-btn");
const cancelBtn = document.getElementById("cancel-btn");
const inputId = document.getElementById("edit-id");
const inputName = document.getElementById("edit-name");
const inputModel = document.getElementById("edit-model");
const inputImage = document.getElementById("edit-image");
const inputType = document.getElementById("edit-type");
const skinTypeField = document.getElementById("skin-type-field");
const uploadBtn = document.getElementById("upload-btn");
const fileInput = document.getElementById("file-input");
const imagePreview = document.getElementById("image-preview");
const uploadStatus = document.getElementById("upload-status");

let allCars = [];
let allSkins = [];
let filteredItems = [];
let currentPage = 1;
const itemsPerPage = 50;
let currentTab = "cars";
let editingItem = null;

const skinTypeNames = {
  7: "Магазин одежды + донат",
  6: "Рабочий класс",
  0: "Остальное"
};


async function loadCars() {
  console.log('[loadCars] starting to load cars.json');
  try {
    const res = await fetch(`./cars.json?t=${Date.now()}`);
    if (!res.ok) throw new Error(`status ${res.status}`);
    allCars = await res.json();
    console.log('[loadCars] successfully loaded', allCars.length, 'cars');
  } catch (err) {
    console.error('[loadCars] failed to load:', err);
    uploadStatus.textContent = `ошибка загрузки машин: ${err.message}`;
    uploadStatus.style.color = '#ff6b6b';
  }
}

async function loadSkins() {
  console.log('[loadSkins] старт загрузки skins.json');
  try {
    const res = await fetch(`./skins.json?t=${Date.now()}`);
    if (!res.ok) throw new Error(`status ${res.status}`);
    allSkins = await res.json();
    console.log('[loadSkins] успешно загружено', allSkins.length, 'скинов');
  } catch (err) {
    console.error('[loadSkins] ошибка загрузки:', err);
    uploadStatus.textContent = `ошибка загрузки скинов: ${err.message}`;
    uploadStatus.style.color = '#ff6b6b';
  }
}


function saveState() {
  localStorage.setItem("state", JSON.stringify({
    currentPage,
    currentTab,
    searchTerm: search.value
  }));
}


function filterAndRender(resetPage) {
  filterItems();
  if (resetPage) currentPage = 1;
  renderPage(currentPage);
  renderPagination();
  saveState();
}

function filterItems() {
  const term = search.value.toLowerCase();
  const source = currentTab === "cars" ? allCars : allSkins;

  filteredItems = source.filter(item => {
    const matchId = String(item.id).includes(term);
    const matchName = item.name && item.name.toLowerCase().includes(term);
    const matchModel = item.model && item.model.toLowerCase().includes(term);

    if (currentTab === "skins") {
      const typeName = skinTypeNames[item.type] || "";
      const matchType = typeName.toLowerCase().includes(term);
      return matchId || matchName || matchModel || matchType;
    }

    return matchId || matchName || matchModel;
  });
}


function renderItems(items) {
  list.innerHTML = "";
  
  items.forEach((item, index) => {
    const div = document.createElement("div");
    div.className = currentTab === "cars" ? "car" : "skin";

    const img = document.createElement("img");
    img.src = item.image;
    img.alt = item.name || "";
    img.onerror = () => { img.style.display = "none"; };
    div.appendChild(img);

    const pId = document.createElement("p");
    pId.innerHTML = `<strong>ID:</strong> ${item.id}`;
    div.appendChild(pId);

    const pName = document.createElement("p");
    pName.innerHTML = `<strong>Name:</strong> ${item.name || ""}`;
    div.appendChild(pName);

    const pModel = document.createElement("p");
    pModel.innerHTML = `<strong>Model:</strong> ${item.model || ""}`;
    div.appendChild(pModel);

    if (currentTab === "skins") {
      const typeName = skinTypeNames[item.type] || "неизвестно";
      const pType = document.createElement("p");
      pType.innerHTML = `<strong>Тип:</strong> ${typeName}`;
      div.appendChild(pType);
    }

    const actionsDiv = document.createElement("div");
    actionsDiv.className = "item-actions";

    const moveDiv = document.createElement("div");
    moveDiv.className = "move-buttons";
    
    const moveUpBtn = document.createElement("button");
    moveUpBtn.className = "move-btn";
    moveUpBtn.innerHTML = "↑";
    moveUpBtn.title = "Переместить вверх";
    moveUpBtn.disabled = index === 0;
    moveUpBtn.onclick = () => moveItem(item, -1);
    moveDiv.appendChild(moveUpBtn);
    
    const moveDownBtn = document.createElement("button");
    moveDownBtn.className = "move-btn";
    moveDownBtn.innerHTML = "↓";
    moveDownBtn.title = "Переместить вниз";
    moveDownBtn.disabled = index === items.length - 1;
    moveDownBtn.onclick = () => moveItem(item, 1);
    moveDiv.appendChild(moveDownBtn);
    
    actionsDiv.appendChild(moveDiv);

    const actionButtonsDiv = document.createElement("div");
    actionButtonsDiv.className = "action-buttons";
    
    const editBtn = document.createElement("button");
    editBtn.className = "edit-btn";
    editBtn.innerHTML = "✏️ редактировать";
    editBtn.onclick = () => openEditor(item);
    actionButtonsDiv.appendChild(editBtn);

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.innerHTML = "❌ удалить";
    deleteBtn.onclick = () => deleteItem(item);
    actionButtonsDiv.appendChild(deleteBtn);
    
    actionsDiv.appendChild(actionButtonsDiv);
    
    div.appendChild(actionsDiv);
    list.appendChild(div);
  });
}


function moveItem(item, direction) {
  const source = currentTab === "cars" ? allCars : allSkins;
  const index = source.findIndex(i => i.id === item.id);
  
  if (index === -1) return;
  
  const newIndex = index + direction;
  
  if (newIndex < 0 || newIndex >= source.length) return;
  
  [source[index], source[newIndex]] = [source[newIndex], source[index]];

  filterAndRender(false);

  setTimeout(() => {
    const elements = list.querySelectorAll('.car, .skin');
    if (elements[newIndex - (currentPage - 1) * itemsPerPage]) {
      elements[newIndex - (currentPage - 1) * itemsPerPage].scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      });
    }
  }, 100);
}


function deleteItem(item) {
  if (!confirm("вы уверены, что хотите удалить этот элемент?")) return;
  
  const source = currentTab === "cars" ? allCars : allSkins;
  const index = source.findIndex(i => i.id === item.id);
  
  if (index !== -1) {
    source.splice(index, 1);
    filterAndRender(false);
  }
}


function renderPage(page) {
  currentPage = page;
  saveState();

  const start = (page - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  renderItems(filteredItems.slice(start, end));
}

function renderPagination() {
  pagination.innerHTML = "";
  const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
  if (totalPages <= 1) return;

  pagination.style.display = "flex";
  pagination.style.justifyContent = "center";
  pagination.style.alignItems = "center";
  pagination.style.gap = "6px";
  pagination.style.flexWrap = "nowrap";

  const maxButtons = 7;
  let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
  let endPage = startPage + maxButtons - 1;

  if (endPage > totalPages) {
    endPage = totalPages;
    startPage = Math.max(1, endPage - maxButtons + 1);
  }

  const prevBtn = document.createElement("button");
  prevBtn.textContent = "←";
  prevBtn.disabled = currentPage === 1;
  prevBtn.onclick = () => {
    if (currentPage > 1) {
      currentPage--;
      renderPage(currentPage);
      renderPagination();
      window.scrollTo({top:0, behavior:"smooth"});
    }
  };
  pagination.appendChild(prevBtn);

  for(let i = startPage; i <= endPage; i++) {
    const btn = document.createElement("button");
    btn.className = "page-btn" + (i === currentPage ? " active" : "");
    btn.textContent = i;
    btn.onclick = () => {
      currentPage = i;
      renderPage(i);
      renderPagination();
      window.scrollTo({top:0, behavior:"smooth"});
    };
    pagination.appendChild(btn);
  }

  const nextBtn = document.createElement("button");
  nextBtn.textContent = "→";
  nextBtn.disabled = currentPage === totalPages;
  nextBtn.onclick = () => {
    if (currentPage < totalPages) {
      currentPage++;
      renderPage(currentPage);
      renderPagination();
      window.scrollTo({top:0, behavior:"smooth"});
    }
  };
  pagination.appendChild(nextBtn);
}


function switchTab(tab) {
  currentTab = tab;
  if(tab === "cars") {
    tabCars.classList.add("active");
    tabSkins.classList.remove("active");
  } else {
    tabSkins.classList.add("active");
    tabCars.classList.remove("active");
  }
  search.value = "";
  filterAndRender(true);
  saveState();
}


function openEditor(item = null) {
  modal.classList.remove("hidden");
  editingItem = item;


  uploadStatus.textContent = "";
  fileInput.value = '';
  imagePreview.style.display = 'none';
  
  if (item) {
    inputId.value = item.id || "";
    inputName.value = item.name || "";
    inputModel.value = item.model || "";
    inputImage.value = item.image || "";
    

    if (item.image) {
      imagePreview.src = item.image;
      imagePreview.style.display = 'block';
    }
    
    if (currentTab === "skins") inputType.value = item.type || 0;
  } else {

    const source = currentTab === "cars" ? allCars : allSkins;
    const maxId = Math.max(...source.map(i => i.id), 0);
    inputId.value = maxId + 1;
    
    inputName.value = "";
    inputModel.value = "";
    inputImage.value = "";
    if (currentTab === "skins") inputType.value = 0;
  }

  skinTypeField.style.display = currentTab === "skins" ? "block" : "none";
}

function closeEditor() {
  modal.classList.add("hidden");
  editingItem = null;
}


uploadBtn.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", async (e) => {
  const file = fileInput.files[0];
  if (!file) return;

  try {
    uploadStatus.textContent = "загрузка...";
    uploadStatus.style.color = "#ccc";

    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch('https://unware.ru/upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || `server error: ${response.status}`);
    }

    const data = await response.json();
    inputImage.value = data.url;
    uploadStatus.textContent = "фото успешно загружено!";
    uploadStatus.style.color = "#4CAF50";

  } catch (error) {
    console.error("upload error:", error);
    uploadStatus.textContent = `ошибка: ${error.message}`;
    uploadStatus.style.color = "#ff6b6b";
    imagePreview.style.display = 'none';
  }
});

saveBtn.onclick = () => {
  const newItem = {
    id: Number(inputId.value),
    name: inputName.value.trim(),
    model: inputModel.value.trim(),
    image: inputImage.value.trim(),
  };

  if (currentTab === "skins") {
    newItem.type = Number(inputType.value);
  }

  if (editingItem) {
    const source = currentTab === "cars" ? allCars : allSkins;
    const idx = source.findIndex(i => i.id === editingItem.id);
    if (idx !== -1) source[idx] = newItem;
  } else {
    const source = currentTab === "cars" ? allCars : allSkins;
    source.push(newItem);
  }

  closeEditor();
  filterAndRender(false);
};


async function init() {
  await Promise.all([loadCars(), loadSkins()]);

  const saved = JSON.parse(localStorage.getItem("state"));
  if (saved) {
    currentTab = saved.currentTab || "cars";
    search.value = saved.searchTerm || "";
    currentPage = saved.currentPage || 1;
  }

  if (currentTab === "cars") {
    tabCars.classList.add("active");
    tabSkins.classList.remove("active");
  } else {
    tabSkins.classList.add("active");
    tabCars.classList.remove("active");
  }

  filterItems();
  renderPage(currentPage);
  renderPagination();
}


tabCars.addEventListener("click", () => switchTab("cars"));
tabSkins.addEventListener("click", () => switchTab("skins"));

search.addEventListener("input", () => {
  filterAndRender(false);
  saveState();
});

search.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    search.blur();
    e.preventDefault();
    filterAndRender(false);
  }
});

cancelBtn.onclick = closeEditor;

exportBtn.addEventListener("click", () => {
  const data = currentTab === "cars" ? allCars : allSkins;
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement("a");
  a.href = url;
  a.download = `${currentTab}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  alert(`файл ${currentTab}.json готов к скачиванию!`);
});


function setupInputBlurOnEnter(input) {
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      input.blur();
    }
  });
}

setupInputBlurOnEnter(inputId);
setupInputBlurOnEnter(inputName);
setupInputBlurOnEnter(inputModel);
setupInputBlurOnEnter(inputImage);
setupInputBlurOnEnter(inputType);


init();


document.addEventListener('touchmove', function(event) {
  if (event.scale !== 1) {
    event.preventDefault();
  }
}, { passive: false });

let lastTouchEnd = 0;
document.addEventListener('touchend', function(event) {
  const now = Date.now();
  if (now - lastTouchEnd <= 300) {
    event.preventDefault();
  }
  lastTouchEnd = now;
}, { passive: false });
