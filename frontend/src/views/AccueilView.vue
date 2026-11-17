<script setup>
import logo from '../ressources/logo.png'
</script>

<template>
  <div class="text-center py-4">
    <img :src="logo" alt="Les Panthères Véloces" class="logo-accueil mb-3" />
    <h1 class="h3 fw-bold">Trouve ta voiture à la vitesse d'une panthère</h1>
    <p class="text-muted">Comment veux-tu chercher ?</p>
  </div>

  <div class="row g-4 justify-content-center">
    <div class="col-md-5">
      <RouterLink to="/criteres" class="card carte-choix h-100 shadow-sm">
        <div class="card-body p-4">
          <div class="icone mb-3">☰</div>
          <h2 class="h5 fw-bold">Je décris mes besoins</h2>
          <p class="text-muted mb-0">
            Budget, motorisation, type de voiture… Réponds à quelques filtres
            et on te propose les voitures qui te correspondent.
          </p>
        </div>
      </RouterLink>
    </div>

    <div class="col-md-5">
      <RouterLink to="/voiture" class="card carte-choix h-100 shadow-sm">
        <div class="card-body p-4">
          <div class="icone mb-3">⇄</div>
          <h2 class="h5 fw-bold">J'ai déjà une voiture en tête</h2>
          <p class="text-muted mb-0">Indique une voiture et on te propose des alternatives proches.</p>
        </div>
      </RouterLink>
    </div>
  </div>
</template>
