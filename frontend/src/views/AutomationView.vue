<template>
  <div class="flex flex-col gap-4 h-full">
    <!-- Header bar -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div>
          <h2 class="text-sm font-semibold">Automation</h2>
          <p class="text-xs text-muted-foreground">Powered by n8n</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Tooltip>
          <TooltipTrigger as-child>
            <Button variant="outline" size="icon" @click="reload">
              <RiRefreshLine class="w-4 h-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Neu laden</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger as-child>
            <Button variant="outline" size="icon" @click="openExternal">
              <RiExternalLinkLine class="w-4 h-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>In neuem Tab öffnen</TooltipContent>
        </Tooltip>
      </div>
    </div>

    <!-- iframe with loading overlay -->
    <div class="flex-1 rounded-lg overflow-hidden border border-border ring-1 ring-foreground/10 -mx-3 sm:-mx-4 lg:-mx-6 -mb-3 sm:-mb-4 lg:-mb-6 relative">
      <div
          v-if="loading"
          class="absolute inset-0 flex flex-col items-center justify-center gap-3 text-muted-foreground bg-background z-10"
      >
        <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        <p class="text-xs">Verbinde mit n8n…</p>
      </div>

      <iframe
          ref="iframeEl"
          :src="n8nUrl"
          class="w-full h-full border-0"
          allow="clipboard-read; clipboard-write"
          @load="onIframeLoad"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { RiRefreshLine, RiExternalLinkLine } from '@remixicon/vue'

const loading = ref(true)
const iframeEl = ref<HTMLIFrameElement | null>(null)

// Port 5679 = nginx proxy in front of n8n that strips X-Frame-Options
const n8nUrl = computed(() => `http://${window.location.hostname}:5679`)

function onIframeLoad() {
  loading.value = false
}

function reload() {
  loading.value = true
  if (iframeEl.value) {
    iframeEl.value.src = n8nUrl.value
  }
}

function openExternal() {
  window.open(n8nUrl.value, '_blank')
}
</script>