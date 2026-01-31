let editor;
let currentFileId = null;
let selectedNodeId = null;
let selectedNodeType = null;

const fileList = document.getElementById("file-list");
const termInput = document.getElementById("terminal-input");
const termOutput = document.getElementById("terminal-output");

/* -----------------------------
   CodeMirror
------------------------------ */
editor = CodeMirror.fromTextArea(
  document.getElementById("editor"),
  {
    mode: "python",
    lineNumbers: true,
    tabSize: 4
  }
);

/* -----------------------------
   Terminal helpers
------------------------------ */
function printToTerminal(text) {
  termOutput.textContent += text + "\n";
  termOutput.scrollTop = termOutput.scrollHeight;
}

termInput.addEventListener("keydown", async (e) => {
  if (e.key === "Enter") {
    const command = termInput.value.trim();
    termInput.value = "";

    if (!command) return;

    printToTerminal(`$ ${command}`);

    const res = await fetch("http://localhost:5000/terminal/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command })
    });

    const data = await res.json();
    printToTerminal(data.output || "");
  }
});

/* -----------------------------
   File Tree
------------------------------ */
async function loadTree() {
  const res = await fetch("http://localhost:5000/tree");
  const nodes = await res.json();

  fileList.innerHTML = "";
  renderTree(buildTree(nodes), fileList);
}

function buildTree(nodes, parent = null) {
  return nodes
    .filter(n => n.parent_id === parent)
    .map(n => ({ ...n, children: buildTree(nodes, n.id) }));
}

function renderTree(tree, container, depth = 0) {
  tree.forEach(node => {
    const item = document.createElement("div");
    item.textContent = (node.type === "folder" ? "📁 " : "📄 ") + node.name;
    item.style.paddingLeft = `${depth * 16 + 8}px`;

    item.onclick = () => {
      selectedNodeId = node.id;
      selectedNodeType = node.type;

      document.querySelectorAll(".selected")
        .forEach(el => el.classList.remove("selected"));

      item.classList.add("selected");

      if (node.type === "file") openFile(node.id);
    };

    container.appendChild(item);

    if (node.children.length)
      renderTree(node.children, container, depth + 1);
  });
}

/* -----------------------------
   File Ops
------------------------------ */
async function openFile(id) {
  const res = await fetch(`http://localhost:5000/file/${id}`);
  const data = await res.json();
  editor.setValue(data.content);
  currentFileId = id;
}

async function saveFile() {
  if (!currentFileId) return alert("No file selected");

  await fetch(`http://localhost:5000/file/${currentFileId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: editor.getValue() })
  });

  alert("Saved");
}

async function newFile() {
  const name = prompt("File name:");
  if (!name) return;

  await fetch("http://localhost:5000/file", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      parent_id: selectedNodeType === "folder" ? selectedNodeId : null
    })
  });

  loadTree();
}

async function newFolder() {
  const name = prompt("Folder name:");
  if (!name) return;

  await fetch("http://localhost:5000/folder", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      parent_id: selectedNodeType === "folder" ? selectedNodeId : null
    })
  });

  loadTree();
}

loadTree();
