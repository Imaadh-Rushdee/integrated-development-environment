let editor;
let currentFileId = null;

let selectedNodeId = null;
let selectedNodeType = null;

const terminal = document.getElementById("terminal");
const fileList = document.getElementById("file-list");

/* -----------------------------
   CodeMirror init
------------------------------ */
editor = CodeMirror.fromTextArea(
  document.getElementById("editor"),
  {
    mode: "python",
    theme: "default",
    lineNumbers: true,
    tabSize: 4,
    indentWithTabs: false
  }
);

/* -----------------------------
   Run code (Piston)
------------------------------ */
async function runCode() {
  terminal.textContent = "Running...\n";

  const code = editor.getValue();

  const res = await fetch("https://emkc.org/api/v2/piston/execute", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      language: "python",
      version: "3.10.0",
      files: [{ content: code }]
    })
  });

  const data = await res.json();
  terminal.textContent = data.run.output || "No output";
}

/* -----------------------------
   Backend filesystem
------------------------------ */

async function loadTree() {
  const res = await fetch("http://localhost:5000/tree");
  const nodes = await res.json();

  const tree = buildTree(nodes);
  fileList.innerHTML = "";
  renderTree(tree, fileList);
}

function buildTree(nodes, parent = null) {
  return nodes
    .filter(n => n.parent_id === parent)
    .map(n => ({
      ...n,
      children: buildTree(nodes, n.id)
    }));
}

function renderTree(tree, container, depth = 0) {
  tree.forEach(node => {
    const item = document.createElement("div");

    item.textContent =
      (node.type === "folder" ? "📁 " : "📄 ") + node.name;

    item.style.paddingLeft = `${depth * 16 + 8}px`;
    item.style.cursor = "pointer";

    item.onclick = (e) => {
      e.stopPropagation();

      selectedNodeId = node.id;
      selectedNodeType = node.type;

      // highlight selection
      document
        .querySelectorAll(".selected")
        .forEach(el => el.classList.remove("selected"));

      item.classList.add("selected");

      if (node.type === "file") {
        openFile(node.id);
      }
    };

    container.appendChild(item);

    if (node.children && node.children.length) {
      renderTree(node.children, container, depth + 1);
    }
  });
}


/* -----------------------------
   File operations
------------------------------ */

async function openFile(id) {
  const res = await fetch(`http://localhost:5000/file/${id}`);
  const data = await res.json();

  editor.setValue(data.content);
  currentFileId = id;
}

async function saveFile() {
  if (!currentFileId) {
    alert("No file selected");
    return;
  }

  await fetch(`http://localhost:5000/file/${currentFileId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      content: editor.getValue()
    })
  });

  alert("Saved!");
}


/* -----------------------------
   Create file / folder
------------------------------ */

async function newFile() {
  const name = prompt("File name:");
  if (!name) return;

  let parentId = null;

  if (selectedNodeType === "folder") {
    parentId = selectedNodeId;
  }

  await fetch("http://localhost:5000/file", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      parent_id: parentId
    })
  });

  loadTree();
}

async function newFolder() {
  const name = prompt("Folder name:");
  if (!name) return;

  let parentId = null;

  if (selectedNodeType === "folder") {
    parentId = selectedNodeId;
  }

  await fetch("http://localhost:5000/folder", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      parent_id: parentId
    })
  });

  loadTree();
}


/* -----------------------------
   Initial load
------------------------------ */
loadTree();
