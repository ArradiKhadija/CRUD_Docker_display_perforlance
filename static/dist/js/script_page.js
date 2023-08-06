

  function openPopup() {
    var popup = document.getElementById("popup");
    popup.style.display = "block";
  }

  window.addEventListener("DOMContentLoaded", function () {
    var optionalToggleSettings = document.querySelector(".optional-toggle-settings");
    var optionalFields = document.querySelectorAll(".optional-field");
    var optionalLabels = document.querySelectorAll(".optional-label");

    optionalToggleSettings.addEventListener("click", function () {
      optionalFields.forEach(function (field) {
        field.classList.toggle("hidden");
      });

      optionalLabels.forEach(function (label) {
        label.classList.toggle("hidden");
      });

      optionalToggleSettings.classList.toggle("fa-angle-up");
      optionalToggleSettings.classList.toggle("fa-angle-down");
    });
  });

  var closeButton = document.getElementById("close-button");

  // Récupération de l'élément conteneur du formulaire
  var formContainer = document.getElementById("popup");

  // Ajout d'un gestionnaire d'événement pour le clic sur le bouton de fermeture
  closeButton.addEventListener("click", function () {
    // Masquer le formulaire en définissant la propriété CSS "display" sur "none"
    formContainer.style.display = "none";
  });

  var runButtons = document.querySelectorAll(".run-button");

  runButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var containerName = button.dataset.name;
      var hiddenInput = document.getElementById("container-image-input");
      hiddenInput.value = containerName;
    });
  });

  //search
  function getRelatedImages(imageName, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_related_images/' + encodeURIComponent(imageName) + '/');
    xhr.onload = function () {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        callback(response.related_images);
      } else {
        console.error('Une erreur s\'est produite lors de la récupération des images liées.');
        callback([]);
      }
    };
    xhr.send();
  }

  document.getElementById("search-form").addEventListener("submit", function (event) {
    event.preventDefault();

    var imageInput = document.getElementById("image-input");
    var imageName = imageInput.value;

    // Appeler la fonction pour récupérer les images liées
    getRelatedImages(imageName, function (relatedImages) {
      // Générer le tableau des résultats
      var resultContainer = document.getElementById("result-container");
      resultContainer.innerHTML = "";

      if (relatedImages.length === 0) {
        resultContainer.innerHTML = "Aucune image liée trouvée.";
      } else {
        var table = document.createElement("table");
        table.classList.add("table");
        table.classList.add("table-bordered");

        var thead = document.createElement("thead");
        var tr = document.createElement("tr");
        var headers = ["Nom de l'image", "Description","Action"];

        for (var i = 0; i < headers.length; i++) {
          var th = document.createElement("th");
          th.textContent = headers[i];
          tr.appendChild(th);
        }

        thead.appendChild(tr);
        table.appendChild(thead);

        var tbody = document.createElement("tbody");

        for (var j = 0; j < relatedImages.length; j++) {
          var image = relatedImages[j];

          var tr = document.createElement("tr");

          var td1 = document.createElement("td");
          td1.textContent = image.name;
          tr.appendChild(td1);

          var td2 = document.createElement("td");
          td2.textContent = image.description;
          tr.appendChild(td2);
          var td3 = document.createElement("td");
          var link = document.createElement("a");
          link.href = "/pull_image/" + image.name;
          var button = document.createElement("button");
          button.textContent = "pull";
          button.className = "bg-primary run-button";
          button.style.width = "100px";
          link.appendChild(button);
          td3.appendChild(link);
          tr.appendChild(td3);
          tbody.appendChild(tr);
        }

        table.appendChild(tbody);
        resultContainer.appendChild(table);
      }

      imageInput.value = "";
    });
  });
function showDeleteButton() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    var deleteButton = document.getElementById('delete-button');
    var cancelButton = document.getElementById('cancel-button');
    var show = document.getElementById('show');
    var hide = document.getElementById('hide');
    var selectAllCheckbox = document.getElementById('select-all-checkbox');

    for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = selectAllCheckbox.checked;
    }

    var checkedCount = 0;
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            checkedCount++;
        }
    }

    if (checkedCount > 0) {
        deleteButton.style.display = 'block';
        show.style.display = 'block';
        cancelButton.style.display = 'block';
        hide.style.display = 'none';
    } else {
        deleteButton.style.display = 'none';
        cancelButton.style.display = 'none';
        show.style.display = 'none';
        hide.style.display = 'block';
    }
} 
function cancel() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    var deleteButton = document.getElementById('delete-button');
    var cancelButton = document.getElementById('cancel-button');
    var show = document.getElementById('show');
    var hide = document.getElementById('hide');
    var selectAllCheckbox = document.getElementById('select-all-checkbox');

    for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = false; // Décoche les cases à cocher
    }

    var checkedCount = 0;
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            checkedCount++;
        }
    }

    if (checkedCount > 0) {
        deleteButton.style.display = 'block';
        show.style.display = 'block';
        cancelButton.style.display = 'block';
        hide.style.display = 'none';
    } else {
        deleteButton.style.display = 'none';
        cancelButton.style.display = 'none';
        show.style.display = 'none';
        hide.style.display = 'block';
    }
}

