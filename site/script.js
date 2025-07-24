const list = document.getElementById("item-list");
const search = document.getElementById("search");
const pagination = document.getElementById("pagination");

const tabCars = document.getElementById("tab-cars");
const tabSkins = document.getElementById("tab-skins");
const tabMapping = document.getElementById("tab-mapping");

let allCars = [];
let allSkins = [];
let allMappings = [];
let filteredItems = [];
let currentPage = 1;
const itemsPerPage = 50;
let currentTab = "cars";

const skinTypeNames = {
  7: "Магазин одежды + донат",
  6: "Рабочий класс",
  0: "Остальное"
};

async function loadCars() {
  const res = await fetch(`./cars.json?t=${Date.now()}`);
  allCars = await res.json();
}

async function loadSkins() {
  const res = await fetch(`./skins.json?t=${Date.now()}`);
  allSkins = await res.json();
}

async function loadMappings() {
  const res = await fetch(`./map.json?t=${Date.now()}`);
  allMappings = await res.json();
}

function saveState() {
  localStorage.setItem("state", JSON.stringify({
    currentPage,
    currentTab,
    searchTerm: search.value
  }));
}

function filterAndRender(resetPage = true) {
  filterItems();
  if (resetPage) currentPage = 1;
  renderPage(currentPage);
  renderPagination();
  saveState();
}

function filterItems() {
  const term = search.value.toLowerCase();
  
  let source;
  if (currentTab === "cars") {
    source = allCars;
  } else if (currentTab === "skins") {
    source = allSkins;
  } else {
    source = allMappings;
  }

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
  
  if (items.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-message";
    empty.textContent = "ничего не найдено";
    list.appendChild(empty);
    return;
  }
  
  items.forEach((item, index) => {
    let className = "item-card";
    let cardColor = "#0078d4";
    
    if (currentTab === "cars") {
      className += " car-card";
      cardColor = "#0078d4";
    } else if (currentTab === "skins") {
      className += " skin-card";
      cardColor = "#9c27b0";
    } else {
      className += " mapping-card";
      cardColor = "#4CAF50";
    }

    const div = document.createElement("div");
    div.className = className;
    div.style.boxShadow = `0 0 8px ${cardColor}aa`;
    div.style.opacity = "0";
    div.style.animation = `fadeIn 0.5s ease forwards ${index * 0.05}s`;

    const img = document.createElement("img");
    img.src = item.image;
    img.alt = item.name || "";
    img.onerror = () => { 
      img.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%23222'/%3E%3Ctext x='50%25' y='50%25' font-size='12' text-anchor='middle' fill='%23aaa'%3Eno image%3C/text%3E%3C/svg%3E";
    };
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
      const typeName = skinTypeNames[item.type] || "Неизвестно";
      const pType = document.createElement("p");
      pType.innerHTML = `<strong>Тип:</strong> ${typeName}`;
      div.appendChild(pType);
    }

    const btnsDiv = document.createElement("div");
    btnsDiv.className = "card-buttons";

    const a = document.createElement("a");
    let prefix;
    if (currentTab === "cars") {
      prefix = "get_car_";
    } else if (currentTab === "skins") {
      prefix = "get_skin_";
    } else {
      prefix = "get_map_";
    }
    
    a.href = `https://t.me/unware_bot?start=${prefix}${item.id}`;
    a.target = "_blank";
    a.textContent = "ПОЛУЧИТЬ";
    a.className = "get-btn";
    a.style.backgroundColor = cardColor;

    btnsDiv.appendChild(a);
    div.appendChild(btnsDiv);
    list.appendChild(div);
  });
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
  if (totalPages <= 1) {
    pagination.style.display = "none";
    return;
  }

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
  prevBtn.className = "pagination-btn";
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
    btn.className = `pagination-btn ${i === currentPage ? "active" : ""}`;
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
  nextBtn.className = "pagination-btn";
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

function switchTab(tab, initial = false) {
  tabCars.classList.remove("active");
  tabSkins.classList.remove("active");
  tabMapping.classList.remove("active");
  
  currentTab = tab;
  
  if (tab === "cars") {
    tabCars.classList.add("active");
  } else if (tab === "skins") {
    tabSkins.classList.add("active");
  } else if (tab === "mapping") {
    tabMapping.classList.add("active");
  }

  const title = document.getElementById('main-title');
  title.className = '';
  if (tab === "cars") {
    title.classList.add('cars-title');
  } else if (tab === "skins") {
    title.classList.add('skins-title');
  } else {
    title.classList.add('mapping-title');
  }

  if (!initial) {
    search.value = "";
  }
  
  filterAndRender();
  saveState();
}

tabCars.addEventListener("click", () => switchTab("cars"));
tabSkins.addEventListener("click", () => switchTab("skins"));
tabMapping.addEventListener("click", () => switchTab("mapping"));

search.addEventListener("input", () => {
  filterAndRender();
  saveState();
});

search.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    search.blur();
    e.preventDefault();
    filterAndRender();
  }
});

function disableTouchMove() {
  let startY = 0;
  let startX = 0;
  
  document.addEventListener('touchstart', function(event) {
    if (event.touches.length === 1) {
      startY = event.touches[0].pageY;
      startX = event.touches[0].pageX;
    } else if (event.touches.length > 1) {
      event.preventDefault();
    }
  }, {passive: false});
  
  document.addEventListener('touchmove', function(event) {
    if (event.touches.length > 1) {
      event.preventDefault();
    } else if (event.touches.length === 1) {

      const moveY = event.touches[0].pageY - startY;
      const moveX = event.touches[0].pageX - startX;
      
      if (Math.abs(moveX) > Math.abs(moveY)) {
        event.preventDefault();
      }
    }
  }, {passive: false});

  let lastTap = 0;
  document.addEventListener('touchend', function(event) {
    const now = Date.now();
    if (now - lastTap < 300) {
      event.preventDefault();
    }
    lastTap = now;
  }, {passive: false});
  
  document.addEventListener('gesturestart', function(e) {
    e.preventDefault();
  });
  
  document.addEventListener('wheel', function(e) {
    if (e.ctrlKey) {
      e.preventDefault();
    }
  }, {passive: false});
}

disableTouchMove();

async function init() {
  await Promise.all([loadCars(), loadSkins(), loadMappings()]);
  
  const saved = JSON.parse(localStorage.getItem("state"));
  if (saved) {
    currentTab = saved.currentTab || "cars";
    search.value = saved.searchTerm || "";
    currentPage = saved.currentPage || 1;
  }

  switchTab(currentTab, true);
  
  filterItems();
  renderPage(currentPage);
  renderPagination();

  setTimeout(() => {
    switchTab(currentTab, true);
  }, 100);
}

window.addEventListener('DOMContentLoaded', init);