// Add classes to align the form
const loginForm = document.querySelector(".needs-align")
const inputs = loginForm.querySelectorAll(".input-align")
const inputClasses = ["col-10", "col-sm-7", "col-md-5"]

for (const x of inputs) {
    inputClasses.forEach(cls => {
        x.classList.add(cls)
    })
}

const labels = loginForm.querySelectorAll(".label-align")
const labelClasses = ["col-sm-3", "col-md-2"]

for (const x of labels) {
    labelClasses.forEach(cls => {
        x.classList.add(cls)
    })
}