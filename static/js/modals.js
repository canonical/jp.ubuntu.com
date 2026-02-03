function getCustomFields() {
  let message = "";
  const formFields = document.querySelectorAll(".js-formfield");

  formFields.forEach(function (formField) {
    // Only include form fields in the message payload that have the class js-formfield
    const comma = ",";
    const fieldsetForm = formField.querySelector(".js-formfield-title");
    let fieldTitle = "";
    if (fieldsetForm) {
      fieldTitle = fieldsetForm;
    } else {
      fieldTitle =
        formField.querySelector(".p-heading--5") ??
        formField.querySelector(".p-modal__question-heading");
    }
    const inputs = formField.querySelectorAll(
      "input, textarea:not(.js-other-input), select"
    );
    if (fieldTitle) {
      message += fieldTitle.innerText + "\r\n";
    }

    inputs.forEach(function (input) {
      switch (input.type) {
        case "select-one":
          message +=
            input.options[input.selectedIndex]?.textContent + comma + " ";
          break;
        case "radio":
          if (input.checked) {
            message += input.value + comma + " ";
          }
          break;
        case "checkbox":
          if (input.checked) {
            if (fieldsetForm) {
              message += input.value + comma + " ";
            } else {
              // Forms that have column separation
              let subSectionText = "";
              if (
                input.closest('[class*="col-"]') &&
                input
                  .closest('[class*="col-"]')
                  .querySelector(".js-sub-section")
              ) {
                let subSection = input
                  .closest('[class*="col-"]')
                  .querySelector(".js-sub-section");
                subSectionText = subSection.innerText + ": ";
              }

              let label = formField.querySelector(
                "span#" + input.getAttribute("aria-labelledby")
              );

              if (label) {
                label = subSectionText + label.innerText;
              } else {
                label = input.getAttribute("aria-labelledby");
              }
              message += label + comma + "\r\n\r\n";
            }
          }
          break;
        case "text":
        case "number":
        case "textarea":
          if (
            input.value !== "" &&
            !input.classList.contains("js-other-input")
          ) {
            message += input.value + comma + " ";
          }
          break;
      }
    });
    message += "\r\n\r\n";
  });

  const radioFieldsets = document.querySelectorAll(".js-remove-radio-names");
  if (radioFieldsets.length > 0) {
    radioFieldsets.forEach((radioFieldset) => {
      const radioInputs = radioFieldset.querySelectorAll("input[type='radio']");
      radioInputs.forEach((radioInput) => {
        radioInput.removeAttribute("name");
      });
    });
  }

  const checkboxFieldsets = document.querySelectorAll(
    ".js-remove-checkbox-names"
  );
  if (checkboxFieldsets.length > 0) {
    checkboxFieldsets.forEach((checkboxFieldset) => {
      const checkboxInputs = checkboxFieldset.querySelectorAll(
        "input[type='checkbox']"
      );
      checkboxInputs.forEach((checkboxInput) => {
        checkboxInput.removeAttribute("name");
      });
    });
  }

  const textarea = document.getElementById("Comments_from_lead__c");
  textarea.value = message;
}
