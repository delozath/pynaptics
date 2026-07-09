/*
 * Progressive enhancement only: every form here already works with a full
 * page reload (see the <noscript> fallback in template_picker.html and the
 * server-side rebuild of specs on POST in template_editor.py). This script
 * just skips the reload when JS is available.
 */
(function () {
  "use strict";

  function setupTemplatePicker() {
    var select = document.getElementById("template-select");
    var dataEl = document.getElementById("template-data");
    if (!select || !dataEl) {
      return;
    }

    var templates;
    try {
      templates = JSON.parse(dataEl.textContent);
    } catch (err) {
      return;
    }

    var keyField = document.getElementById("template-key-field");
    var descriptionEl = document.getElementById("template-description");
    var paramsContainer = document.getElementById("template-parameters");
    var nullableCheckbox = document.getElementById("template-nullable-checkbox");

    function fieldMarkup(spec) {
      var id = "tpl-field-" + spec.name;
      var label = '<label for="' + id + '">' + spec.label + "</label>";
      if (spec.kind === "list") {
        return label + '<textarea id="' + id + '" name="' + spec.name + '" rows="4"></textarea>';
      }
      return label + '<input type="text" id="' + id + '" name="' + spec.name + '" value="">';
    }

    function render(key) {
      var template = templates[key];
      if (!template) {
        return;
      }
      if (keyField) {
        keyField.value = key;
      }
      if (descriptionEl) {
        descriptionEl.textContent = template.description;
      }
      if (nullableCheckbox) {
        nullableCheckbox.checked = Boolean(template.default_nullable);
      }
      if (paramsContainer) {
        paramsContainer.innerHTML = template.params.map(fieldMarkup).join("");
      }
    }

    select.addEventListener("change", function () {
      render(select.value);
    });
  }

  document.addEventListener("DOMContentLoaded", setupTemplatePicker);
})();
