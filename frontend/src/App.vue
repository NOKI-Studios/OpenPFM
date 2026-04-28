<script setup lang="ts">
import { Button } from '@/components/ui/button'
</script>

<template>
  <div>
    <h1>Welcome to your new project</h1>
  </div>
  <div class="p-8">
    <Button>Test Button</Button>
    <Button variant="outline" class="ml-2">Outline</Button>
    <Button variant="destructive" class="ml-2">Destructive</Button>
  </div>
</template>
