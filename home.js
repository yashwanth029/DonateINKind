const items = [
  {
    name: "Clothes",
    description: "Used clothes in good condition",
    donated_by: "Amit"
  },
  {
    name: "Books",
    description: "Engineering textbooks",
    donated_by: "Rahul"
  },
  {
    name: "Blankets",
    description: "Winter blankets for donation",
    donated_by: "NGO Hope"
  }
];

const itemsDiv = document.getElementById("items");

items.forEach(item => {
  const div = document.createElement("div");
  div.className = "item";
  div.innerHTML = `
    <h3>${item.name}</h3>
    <p>${item.description}</p>
    <small>Donated by ${item.donated_by}</small>
  `;
  itemsDiv.appendChild(div);
});
