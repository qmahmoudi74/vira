const tester = document.querySelector(".tester");
const text = tester.querySelector("#sample");
const render = tester.querySelector("#render");
const size = tester.querySelector("#size");
const weight = tester.querySelector("#weight");
const tabular = tester.querySelector("#tabular");
const sizeOutput = tester.querySelector("#size-output");
const weightOutput = tester.querySelector("#weight-output");
const familyOutput = tester.querySelector("#family-output");
const number = new Intl.NumberFormat("fa-IR", { useGrouping: false });
const examples = {
  persian: "همه‌ی سفارش‌ها بررسی شدند. موجودی حساب ۴۸۵٬۰۰۰ تومان است.",
  latin: "Sales Report · ORDER-248 · 485,000",
  mixed: "گزارش فروش · Sales Report · 485,000",
};

function update() {
  const family = tester.querySelector('input[name="family"]:checked').value;
  render.textContent = text.value;
  render.style.setProperty("--sample-family", JSON.stringify(family));
  render.style.setProperty("--sample-size", size.value + "px");
  render.style.setProperty("--sample-weight", weight.value);
  render.classList.toggle("tabular", tabular.checked);
  sizeOutput.value = number.format(size.value) + " پیکسل";
  weightOutput.value = number.format(weight.value);
  size.setAttribute("aria-valuetext", sizeOutput.value);
  weight.setAttribute("aria-valuetext", weightOutput.value);
  familyOutput.textContent = family;
}

tester.addEventListener("input", update);
for (const button of tester.querySelectorAll("[data-example]")) {
  button.addEventListener("click", () => {
    text.value = examples[button.dataset.example];
    update();
  });
}
update();
