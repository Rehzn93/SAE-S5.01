<script setup>
import logo from './ressources/logo.png'
</script>

<template>
  <nav class="navbar barre-nav">
    <div class="container">
      <RouterLink class="navbar-brand" to="/">
        <img :src="logo" alt="Les Panthères Véloces" />
      </RouterLink>
    </div>
  </nav>

  <main class="container py-4">
    <RouterView />
  </main>

  <footer class="container pb-4 text-muted small">
    SAE S5.01 / Données : ADEME Car Labelling
  </footer>
</template>
