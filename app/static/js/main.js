// Disparition automatique des alertes après 5 secondes
document.addEventListener("DOMContentLoaded", function () {
  // Sélectionner toutes les alertes avec bouton de fermeture
  const alerts = document.querySelectorAll(".alert-dismissible");

  // Pour chaque alerte, ajouter un timer pour la cacher après 5 secondes
  alerts.forEach(function (alert) {
    setTimeout(function () {
      // Créer et dispatcher un événement de clic sur le bouton close
      const closeButton = alert.querySelector(".btn-close");
      if (closeButton) {
        closeButton.click();
      }
    }, 5000);
  });

  // Calculer automatiquement le prix total lors de la création/modification d'envoi
  const weightInput = document.getElementById("weight_kg");
  const packageCountInput = document.getElementById("package_count");
  const priceInput = document.getElementById("price");

  // Fonction pour suggérer un prix basé sur le poids et le nombre de colis
  function updateSuggestedPrice() {
    if (weightInput && packageCountInput && priceInput) {
      const weight = parseFloat(weightInput.value) || 0;
      const packageCount = parseInt(packageCountInput.value) || 0;

      // Formule simple: 10€ de base + 5€ par kg + 2€ par colis supplémentaire
      let suggestedPrice = 10 + weight * 5;
      if (packageCount > 1) {
        suggestedPrice += (packageCount - 1) * 2;
      }

      // Ne mettre à jour que si le champ prix est vide ou si l'utilisateur n'a pas encore modifié le prix
      if (
        priceInput.value === "" ||
        priceInput.getAttribute("data-auto-calculated") === "true"
      ) {
        priceInput.value = suggestedPrice.toFixed(2);
        priceInput.setAttribute("data-auto-calculated", "true");
      }
    }
  }

  // Ajouter des écouteurs d'événements pour mettre à jour le prix suggéré
  if (weightInput && packageCountInput) {
    weightInput.addEventListener("input", updateSuggestedPrice);
    packageCountInput.addEventListener("input", updateSuggestedPrice);

    // Marquer le prix comme modifié manuellement si l'utilisateur change la valeur
    if (priceInput) {
      priceInput.addEventListener("input", function () {
        priceInput.setAttribute("data-auto-calculated", "false");
      });
    }
  }
});
